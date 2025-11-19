# Design Notes - ILS v2 Architecture

## Overview

This document describes the **ILS v2 (Intermediate Layout Schema Version 2)** architecture implemented in the Figma to Multicode Generator. This is a major upgrade that transforms the system into a production-quality, maintainable, and extensible codebase.

---

## Architecture Philosophy

The system follows a **clean pipeline architecture** with well-defined stages:

```
Image Upload
    ↓
[1] Detection (OpenCV)
    ↓
[2] Classification (CNN or Fallback)
    ↓
[3] Style Analysis (Colors, Spacing, Typography)
    ↓
[4] ILS v2 Building (Tree Structure, Semantic Sections)
    ↓
[5] Code Generation (Tailwind, HTML+CSS, React, Flutter)
    ↓
Multi-Framework Code Output
```

Each stage is:
- **Decoupled**: Can be tested independently
- **Replaceable**: Easy to swap implementations
- **Documented**: Clear APIs and examples
- **Robust**: Never crashes, always returns valid output

---

## Stage 1: Detection (`utils/detection.py`)

### Purpose
Detect rectangular UI blocks using pure OpenCV operations.

### Key Functions
- `detect_blocks(image_bgr) -> List[Dict]`: Main detection pipeline
- `cluster_rows(blocks, gap_threshold) -> List[List[Dict]]`: Group blocks into horizontal rows
- `cluster_columns(blocks, gap_threshold) -> List[List[Dict]]`: Group blocks into vertical columns

### Algorithm
1. **Preprocessing**: Gaussian blur + Canny edges + Adaptive threshold
2. **Contour Detection**: RETR_TREE for nested elements
3. **Filtering**: Area, aspect ratio, solidity checks
4. **Merging**: Combine overlapping blocks (IoU > 0.3)
5. **Sorting**: Reading order (top-to-bottom, left-to-right)

### Output Format
```python
[
    {"x": int, "y": int, "w": int, "h": int},
    ...
]
```

### Configuration
All thresholds in `config.py`:
- `DETECTION_MIN_AREA`: 500 (pixels²)
- `DETECTION_MAX_AREA`: 500000
- `DETECTION_MIN_ASPECT_RATIO`: 0.1
- `DETECTION_MAX_ASPECT_RATIO`: 20.0

---

## Stage 2: Classification (`utils/classifier.py`)

### Purpose
Classify detected blocks into UI element types using CNN or geometric fallback.

### Key Functions
- `load_model(config) -> Optional[Model]`: Load trained CNN model
- `classify_blocks(model, image, blocks) -> List[TypedBlock]`: Classify all blocks
- `get_classifier_status(model) -> Dict`: Get diagnostic info

### Data Structures
```python
@dataclass
class Block:
    id: str
    x: int
    y: int
    w: int
    h: int

@dataclass
class TypedBlock:
    id: str
    x: int
    y: int
    w: int
    h: int
    type: str          # button, input_field, heading, etc.
    confidence: float  # 0.0 to 1.0
    source: str        # "cnn" or "fallback"
```

### CNN Path
1. Crop each block from image
2. Resize to 224×224 (model input size)
3. Normalize to [0, 1]
4. Batch inference with `model.predict()`
5. Map output index → class name

### Fallback Path
Uses geometric heuristics when CNN not available:
- Button: 50-300px wide, 20-80px tall, aspect 1.5-8
- Input: 100-600px wide, 20-60px tall, aspect 2-15
- Heading: Near top, wide, moderate height
- Card: Large area, squarish aspect 0.5-3

### Model Integration
**Location**: `backend/models/ui_classification_model.h5`

**Expected Format**:
- Input: (None, 224, 224, 3) - RGB images normalized [0, 1]
- Output: (None, 9) - 9 class probabilities

**Class Mapping** (TODO: Update to match YOUR model):
```python
CLASS_NAMES = [
    'background',      # Index 0
    'button',          # Index 1
    'card',            # Index 2
    'heading',         # Index 3
    'image_block',     # Index 4
    'input_field',     # Index 5
    'link',            # Index 6
    'password_input',  # Index 7
    'text_block'       # Index 8
]
```

---

## Stage 3: Style Analysis (`utils/style_analyzer.py`)

### Purpose
Extract visual styling using pure OpenCV/NumPy (no ML).

### Key Functions
- `analyze_style(image, typed_blocks) -> Dict`: Main analysis function
- `extract_dominant_colors(image, k=5) -> List[Tuple[hex, prominence]]`: K-means color clustering
- `detect_background_color(image) -> str`: Sample edges for background
- `analyze_block_style(image, rect) -> Dict`: Per-block style extraction

### Output Format
```python
{
    "page": {
        "background_color": "#f3f4f6",
        "primary_color": "#2563eb",
        "accent_color": "#f59e0b",
        "text_color": "#111827",
        "base_spacing": 16  # pixels
    },
    "blocks": [
        {
            "id": "block_0",
            "type": "button",
            "rect": {"x": 100, "y": 200, "w": 120, "h": 40},
            "style": {
                "background_color": "#2563eb",
                "text_color": "#ffffff",
                "border_radius": 8,
                "font_scale": "body",
                "variant": "solid"
            }
        },
        ...
    ]
}
```

### Algorithms

#### Color Extraction
- **K-means clustering** (k=5) on image pixels
- Identify background (largest cluster or edge sampling)
- Primary = most prominent non-background color
- Accent = second most prominent
- Text = darkest (light bg) or lightest (dark bg)

#### Spacing Estimation
- Calculate gaps between blocks (vertical & horizontal)
- Use quartiles: Q1=small, Q2=medium, Q3=large
- Default to 8/16/24 if insufficient data

#### Border Radius Detection
- Sample corner regions of blocks
- Compare edge variance (high = rounded)
- Map to Tailwind scale: 0/4/8/12/24/999 (full)

#### Variant Detection (solid/outline/ghost)
- **Solid**: Uniform fill, low std dev
- **Outline**: High edge-to-center contrast
- **Ghost**: Mostly transparent

---

## Stage 4: ILS v2 Building (`utils/ils_builder.py`)

### Purpose
Build hierarchical tree representation with semantic sections.

### Key Concept: ILSNode
```python
@dataclass
class ILSNode:
    id: str
    type: NodeType  # page | navbar | hero | form | cards | button | etc.
    role: Optional[Role]  # primary | secondary | cta | highlight
    rect: Optional[Dict]  # {"x": int, "y": int, "w": int, "h": int}
    
    layout: Dict  # How children are arranged
    style: Dict   # Visual styling
    text: Optional[str]  # Text content
    children: List[ILSNode]  # Nested elements
```

### Tree Structure
```
Page (root)
├── Navbar
│   ├── Link
│   ├── Link
│   └── Button
├── Hero
│   ├── Heading
│   └── Text Block
├── Form
│   ├── Input Field
│   ├── Input Field
│   └── Button (primary)
├── Cards (grid)
│   ├── Card
│   │   ├── Image
│   │   └── Text
│   ├── Card
│   └── Card
└── Footer
    ├── Link
    └── Link
```

### Section Detection

#### Navbar
- In top 15% of image
- Spans >60% of width
- Horizontal layout

#### Hero
- Upper half of image
- Large area (>10% of image)
- Contains heading or image_block

#### Form
- 2+ input fields vertically aligned
- Optional button below inputs
- Vertical layout with gap

#### Cards
- 2+ similar-sized blocks
- Aligned horizontally or vertically
- Grid layout with columns

#### Footer
- In bottom 15% of image
- Horizontal layout

### Layout Modes
- **vertical**: `flex flex-col` (forms, sections)
- **horizontal**: `flex flex-row` (navbar, footer)
- **grid**: `grid grid-cols-N` (cards, galleries)
- **absolute**: Absolute positioning (rare)

### Main Function
```python
def build_ils(typed_blocks, style_info) -> Dict:
    """
    Build complete ILS tree.
    
    Process:
    1. Detect semantic sections (navbar, hero, forms, cards, footer)
    2. Group remaining blocks into generic sections
    3. Build hierarchical tree
    4. Apply style information
    5. Return JSON-serializable dict
    """
```

---

## Stage 5: Code Generation (`utils/generators/`)

### Architecture
Each generator walks the ILS tree recursively and maps nodes to framework-specific code.

### Tailwind Generator (`tailwind_gen.py`)

#### Mapping Functions
- `map_layout_mode_to_flex(mode)`: "vertical" → "flex flex-col"
- `map_gap_to_tailwind(gap_px)`: 16px → "gap-4"
- `map_padding_to_tailwind(pad_px)`: 24px → "p-6"
- `map_border_radius_to_tailwind(radius_px)`: 8px → "rounded-lg"
- `map_font_scale_to_tailwind(scale)`: "heading" → "text-2xl font-semibold"

#### Node Rendering
```python
def render_node(node, depth) -> str:
    """Route to appropriate renderer based on node type."""
    if node.type == "page":
        return render_page(node, depth)
    elif node.type == "navbar":
        return render_section(node, depth)  # <nav>
    elif node.type == "button":
        return render_button(node, depth)  # <button>
    # ... etc
```

#### Example Output
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body>
  <div class="min-h-screen flex flex-col">
    <nav class="flex flex-row gap-4 p-4 w-full shadow-sm">
      <a href="#" class="hover:underline">Home</a>
      <a href="#" class="hover:underline">About</a>
      <button class="px-6 py-2 rounded-lg">Sign In</button>
    </nav>
    <section class="flex flex-col gap-6 p-12 w-full text-center">
      <h1 class="text-4xl font-bold">Welcome</h1>
      <p class="text-base">Get started today</p>
    </section>
  </div>
</body>
</html>
```

### Future Generators
- **HTML+CSS**: Separate .html and .css files
- **React**: JSX components with hooks
- **Flutter**: Dart widgets with Material/Cupertino

---

## API Contract

### `/analyze` Endpoint

**Request**:
```
POST /analyze
Content-Type: multipart/form-data

file: <image file>
include_debug: <boolean> (optional)
```

**Response**:
```json
{
  "success": true,
  "stats": {
    "blocks_detected": 12,
    "blocks_classified": 12,
    "cnn_classifications": 10,
    "fallback_classifications": 2,
    "sections_detected": 4
  },
  "layout": [...],  // Legacy format (backward compat)
  "ils": {
    "id": "page_root",
    "type": "page",
    "layout": {...},
    "style": {...},
    "children": [...]
  },
  "style": {
    "page": {...},
    "blocks": [...]
  },
  "outputs": {
    "html_tailwind": "<!DOCTYPE html>...",
    "html_plain": "<html>...",
    "css": "body { ... }",
    "react": "export function App() {...}",
    "dart": "void main() {...}"
  }
}
```

**IMPORTANT**: The `/analyze` endpoint **MUST** maintain this response structure. Generators can be improved, but never remove existing keys.

---

## Configuration (`config.py`)

All magic numbers and thresholds live here:

```python
class Config:
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Detection
    DETECTION_MIN_AREA: int = 500
    DETECTION_MAX_AREA: int = 500000
    DETECTION_MIN_ASPECT_RATIO: float = 0.1
    DETECTION_MAX_ASPECT_RATIO: float = 20.0
    
    # Model
    MODEL_PATH: Path = Path(__file__).parent / "models" / "ui_classification_model.h5"
    
    # ... etc
```

---

## Logging Strategy

### Log Levels
- **DEBUG**: Detailed processing steps (development only)
- **INFO**: Pipeline stages, major decisions
- **WARNING**: Fallbacks, degraded modes
- **ERROR**: Failures that are handled
- **CRITICAL**: Unrecoverable failures

### Example Log Output
```
2025-11-20 10:15:32 - app - INFO - ==========================================
2025-11-20 10:15:32 - app - INFO - FIGMA TO MULTICODE GENERATOR - Starting
2025-11-20 10:15:32 - app - INFO - ==========================================
2025-11-20 10:15:33 - classifier - INFO - Loading trained CNN model from: backend/models/ui_classification_model.h5
2025-11-20 10:15:34 - classifier - INFO - ✓ UI classifier model: LOADED successfully
2025-11-20 10:15:34 - classifier - INFO -   Input shape: (None, 224, 224, 3)
2025-11-20 10:15:34 - classifier - INFO -   Output classes: 9
2025-11-20 10:15:34 - app - INFO - Classifier mode: cnn
2025-11-20 10:15:34 - app - INFO - Application ready!
```

---

## Testing Strategy

### Unit Tests (Future)
```
tests/
├── test_detection.py       # Detection algorithms
├── test_classifier.py      # Classification logic
├── test_style_analyzer.py  # Style extraction
├── test_ils_builder.py     # ILS tree building
└── test_generators.py      # Code generation
```

### Integration Tests
- Upload test images
- Verify complete pipeline
- Check output format

### Manual Testing
1. Run `python -m pytest tests/`
2. Upload various UI screenshots
3. Verify generated code renders correctly

---

## Future Improvements

### Near-Term (1-2 weeks)
- [ ] Upgrade HTML+CSS generator to ILS v2
- [ ] Upgrade React generator to ILS v2
- [ ] Upgrade Flutter generator to ILS v2
- [ ] Add debug endpoint with visual overlays
- [ ] Add more section types (tabs, modals, sidebars)

### Medium-Term (1-2 months)
- [ ] Text extraction with OCR (actual content)
- [ ] Responsive layout detection
- [ ] Animation/transition hints
- [ ] Component library integration (Shadcn, MUI)

### Long-Term (3+ months)
- [ ] Multi-page support
- [ ] State management generation
- [ ] API integration scaffolding
- [ ] Accessibility (ARIA) attributes

---

## Contributing

### Code Style
- **Python**: PEP 8, type hints, docstrings
- **Functions**: Single responsibility, max 50 lines
- **Classes**: Dataclasses for data, regular classes for behavior
- **Imports**: Standard lib → Third party → Local

### Adding a New Generator
1. Create `backend/utils/generators/framework_gen.py`
2. Implement `generate_framework_code(ils: Dict) -> str`
3. Walk ILS tree with `render_node(node, depth)`
4. Add to `backend/app.py` outputs
5. Test with multiple UI types

### Adding a New Section Type
1. Add to `NodeType` enum in `ils_builder.py`
2. Create `detect_NEW_section(typed_blocks, image_size)` function
3. Call in `build_ils()` detection phase
4. Update generators to handle new type

---

## Performance Notes

### Bottlenecks
1. **CNN Inference**: ~100-200ms for 20 blocks
2. **Style Analysis**: ~50-100ms (k-means clustering)
3. **ILS Building**: ~10-20ms (fast)
4. **Code Generation**: ~5-10ms per framework

### Optimization
- Use batch inference for CNN (already implemented)
- Cache style analysis for similar images
- Profile with `python -m cProfile backend/app.py`

### Scalability
- Current: ~1-2 requests/second (single worker)
- With Gunicorn (4 workers): ~4-8 requests/second
- With model quantization: ~2-3x faster

---

## Troubleshooting

### Model Not Loading
```
⚠ Running in fallback mode (geometric classifier)
```
**Solution**: Place `ui_classification_model.h5` in `backend/models/` directory

### No Blocks Detected
```
ERROR: No UI elements detected in image
```
**Causes**:
- Image too blurry or low resolution
- All-white or all-black image
- Text-only screenshot (no clear UI elements)

**Solution**: Use clearer screenshot with visible UI components

### Low Classification Confidence
```
Classified: 0 CNN, 15 fallback
```
**Causes**:
- Model not trained on similar UI elements
- Confidence threshold too high (currently 0.3)

**Solution**: Retrain model or adjust `CONFIDENCE_THRESHOLD` in `classifier.py`

---

## License & Credits

**Project**: Figma to Multicode Generator  
**Version**: 2.0 (ILS v2 Architecture)  
**Author**: Your Team  
**License**: MIT  

**Technologies**:
- FastAPI (web framework)
- OpenCV (computer vision)
- TensorFlow/Keras (deep learning)
- NumPy (numerical computing)
- Tailwind CSS (styling)

---

**Last Updated**: November 20, 2025  
**Architecture Version**: ILS v2.0
