# Figma to Multicode Generator - Complete Project Report

## 📋 Executive Summary

The **Figma to Multicode Generator** is an AI-powered web application that automatically converts UI screenshots into production-ready code across multiple frameworks (HTML/CSS, Tailwind, React, and Flutter). The system leverages Computer Vision (OpenCV), a trained CNN model (TensorFlow/Keras), and intelligent code generation to streamline the UI development process.

---

## 🎯 Project Overview

### Problem Statement
Manual conversion of UI designs into code is time-consuming, error-prone, and requires expertise across multiple frameworks. Developers spend significant time translating visual designs into functional code.

### Solution
An automated system that:
1. Accepts UI screenshots as input
2. Detects and classifies UI elements using AI
3. Analyzes layout and styling
4. Generates clean, functional code in multiple frameworks

### Key Technologies
- **Backend**: Python, FastAPI, TensorFlow/Keras, OpenCV
- **Frontend**: React, Vite, TailwindCSS
- **AI/ML**: Custom-trained CNN for UI element classification
- **Computer Vision**: OpenCV for element detection

---

## 🏗️ System Architecture

### High-Level Architecture

```
┌─────────────────┐
│   User Upload   │
│  (UI Screenshot)│
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│         Backend (FastAPI)               │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │   1. OpenCV Detection            │  │
│  │   - Identifies bounding boxes    │  │
│  │   - Detects UI element regions   │  │
│  └──────────────┬───────────────────┘  │
│                 │                       │
│                 ▼                       │
│  ┌──────────────────────────────────┐  │
│  │   2. TensorFlow Classification   │  │
│  │   - Trained CNN model            │  │
│  │   - 9 UI element classes         │  │
│  │   - Confidence scoring           │  │
│  └──────────────┬───────────────────┘  │
│                 │                       │
│                 ▼                       │
│  ┌──────────────────────────────────┐  │
│  │   3. Style Analysis              │  │
│  │   - Color extraction             │  │
│  │   - Spacing detection            │  │
│  │   - Border properties            │  │
│  └──────────────┬───────────────────┘  │
│                 │                       │
│                 ▼                       │
│  ┌──────────────────────────────────┐  │
│  │   4. ILS Builder                 │  │
│  │   - Intermediate Layout Schema   │  │
│  │   - Hierarchy construction       │  │
│  │   - Relationship mapping         │  │
│  └──────────────┬───────────────────┘  │
│                 │                       │
│                 ▼                       │
│  ┌──────────────────────────────────┐  │
│  │   5. Code Generators             │  │
│  │   - HTML + CSS                   │  │
│  │   - HTML + Tailwind              │  │
│  │   - React Components             │  │
│  │   - Flutter Widgets              │  │
│  └──────────────┬───────────────────┘  │
│                 │                       │
└─────────────────┼───────────────────────┘
                  │
                  ▼
         ┌────────────────┐
         │  JSON Response │
         │  (Code Output) │
         └────────┬───────┘
                  │
                  ▼
         ┌────────────────┐
         │    Frontend    │
         │  (React + Vite)│
         └────────────────┘
```

---

## 🧠 AI/ML Model Details

### Model Architecture

**Type**: Convolutional Neural Network (CNN)  
**Framework**: TensorFlow/Keras  
**Input**: 224×224×3 RGB images  
**Output**: 9 class probabilities

### Classification Classes

| Class Name      | Description                  | Mapped UI Type |
|----------------|------------------------------|----------------|
| background     | Background containers        | container      |
| button         | Action buttons               | button         |
| card           | Card components              | card           |
| heading        | Heading text elements        | heading        |
| image_block    | Image placeholders           | image          |
| input_field    | Text input fields            | text_input     |
| link           | Hyperlinks                   | link           |
| password_input | Password input fields        | text_input     |
| text_block     | Regular text content         | text           |

### Model Training Process

1. **Data Collection**
   - Real UI screenshots from web and mobile applications
   - Synthetic UI screens generated programmatically
   - Diverse dataset covering multiple design patterns

2. **Data Labeling**
   - Manual annotation of bounding boxes
   - Auto-labeling tools for efficiency
   - Quality assurance and validation

3. **Data Preprocessing**
   - Image resizing to 224×224
   - Normalization to [0, 1] range
   - Data augmentation (rotation, scaling, color jitter)

4. **Model Training**
   - Architecture: Custom CNN with multiple convolutional layers
   - Optimizer: Adam
   - Loss Function: Categorical Crossentropy
   - Training Duration: 30-100 epochs
   - Validation Split: 80/20

5. **Model Evaluation**
   - Accuracy metrics on test set
   - Confusion matrix analysis
   - Confidence threshold optimization

6. **Model Deployment**
   - Export as `.h5` file
   - Integration with FastAPI backend
   - Real-time inference during runtime

---

## 🔄 Complete Processing Pipeline

### 1. Screenshot Input
- User uploads UI screenshot (PNG, JPG, etc.)
- File validation (size, format, dimensions)
- Image preprocessing and normalization

### 2. Element Detection (OpenCV)
```python
# Pseudo-code
gray_image = convert_to_grayscale(screenshot)
edges = detect_edges(gray_image)
contours = find_contours(edges)
bounding_boxes = extract_rectangles(contours)
```

**Output**: List of bounding boxes `[{x, y, w, h}, ...]`

### 3. Element Classification (TensorFlow)
```python
# Pseudo-code
for each bounding_box in bounding_boxes:
    crop = extract_crop(screenshot, bounding_box)
    preprocessed = resize_and_normalize(crop, 224, 224)
    predictions = model.predict(preprocessed)
    class_name = get_top_class(predictions)
    confidence = get_confidence(predictions)
    classified_blocks.append({
        'bbox': bounding_box,
        'type': class_name,
        'confidence': confidence
    })
```

**Output**: Classified blocks with types and confidence scores

### 4. Style Extraction
- **Color Analysis**: Extract dominant colors, text colors, backgrounds
- **Typography**: Detect font sizes, weights (approximated)
- **Spacing**: Calculate padding and margins
- **Borders**: Identify border radius and styles

### 5. Layout Analysis
- **Hierarchy Detection**: Parent-child relationships
- **Alignment**: Row/column layouts
- **Grouping**: Related elements clustering
- **Responsive Breakpoints**: Adapt to different screen sizes

### 6. ILS Construction
**Intermediate Layout Schema** - JSON representation:
```json
{
  "root": {
    "type": "container",
    "layout": "column",
    "children": [
      {
        "type": "heading",
        "text": "Welcome",
        "style": {"fontSize": "24px"}
      },
      {
        "type": "button",
        "text": "Click Me",
        "style": {"backgroundColor": "#007bff"}
      }
    ]
  }
}
```

### 7. Code Generation
Based on ILS, generate code for each framework:

**HTML + Tailwind**:
```html
<div class="flex flex-col gap-4">
  <h1 class="text-2xl font-bold">Welcome</h1>
  <button class="bg-blue-500 px-4 py-2 rounded">Click Me</button>
</div>
```

**React**:
```jsx
function Component() {
  return (
    <div className="flex flex-col gap-4">
      <h1 className="text-2xl font-bold">Welcome</h1>
      <button className="bg-blue-500 px-4 py-2 rounded">Click Me</button>
    </div>
  );
}
```

**Flutter**:
```dart
Column(
  children: [
    Text('Welcome', style: TextStyle(fontSize: 24)),
    ElevatedButton(onPressed: () {}, child: Text('Click Me')),
  ],
)
```

---

## 💻 Implementation Details

### Backend Stack

**Framework**: FastAPI  
**Language**: Python 3.8+  

**Key Dependencies**:
- `tensorflow>=2.13.0` - Model inference
- `opencv-python>=4.8.0` - Image processing
- `numpy>=1.21.0` - Numerical operations
- `pillow>=10.0.0` - Image handling
- `fastapi>=0.100.0` - Web framework
- `uvicorn[standard]>=0.20.0` - ASGI server

**Directory Structure**:
```
backend/
├── app_new.py              # Main FastAPI application
├── config.py               # Configuration management
├── requirements.txt        # Dependencies
├── run_backend.ps1         # Automated setup script
├── models/
│   └── ui_classification_model.h5  # Trained model
└── utils/
    ├── tf_classifier.py    # TensorFlow integration
    ├── detection.py        # OpenCV detection
    ├── ils_builder.py      # Layout schema builder
    ├── style_analyzer.py   # Style extraction
    ├── generator_html_css_enhanced.py
    ├── generator_tailwind_enhanced.py
    ├── generator_react_enhanced.py
    └── generator_flutter_enhanced.py
```

### Frontend Stack

**Framework**: React 18  
**Build Tool**: Vite  
**Styling**: TailwindCSS  

**Key Features**:
- Drag & drop file upload
- Real-time progress tracking
- Multiple code output tabs
- Copy to clipboard functionality
- Live preview (HTML/Tailwind)
- Responsive design
- Dark mode UI

**Directory Structure**:
```
frontend/
├── src/
│   ├── App.jsx             # Main application component
│   ├── config.js           # API configuration
│   ├── components/
│   │   ├── Notification.jsx
│   │   ├── ProgressBar.jsx
│   │   ├── Tooltip.jsx
│   │   └── HelpPanel.jsx
│   └── hooks/
│       └── useKeyboardShortcuts.js
├── package.json
└── vite.config.mts
```

---

## 🚀 Setup and Deployment

### Prerequisites
- Python 3.8 or higher
- Node.js 16 or higher
- Trained model file (`ui_classification_model.h5`)

### Installation Steps

**1. Clone Repository**
```bash
git clone https://github.com/piyushsayare8/figma-to-multicode-generator.git
cd figma-to-multicode-generator
```

**2. Place Trained Model**
```bash
cp ui_classification_model.h5 backend/models/
```

**3. Setup Backend**
```bash
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows
pip install -r requirements.txt
```

**4. Setup Frontend**
```bash
cd frontend
npm install
```

**5. Run Application**

**Terminal 1 (Backend)**:
```bash
cd backend
uvicorn app_new:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 (Frontend)**:
```bash
cd frontend
npm run dev
```

**6. Access Application**
- Frontend: `http://localhost:5173`
- API Docs: `http://localhost:8000/docs`

---

## 📊 Performance Metrics

### Model Performance
- **Training Accuracy**: ~95% (varies based on dataset)
- **Inference Time**: ~50-100ms per image
- **Confidence Threshold**: 0.5 (adjustable)

### System Performance
- **Average Processing Time**: 1-3 seconds per screenshot
- **Supported Image Formats**: PNG, JPG, JPEG, BMP, WEBP
- **Max Image Size**: 10MB (configurable)
- **Concurrent Requests**: Supports multiple simultaneous uploads

---

## 🎨 User Interface Features

### Enhanced UX
- 🎨 Modern dark theme with glass morphism
- 📁 Drag & drop file upload
- ⚡ Real-time progress tracking
- 🔔 Smart toast notifications
- 💡 Interactive tooltips
- ⌨️ Keyboard shortcuts
- 📱 Fully responsive design

### Keyboard Shortcuts
| Shortcut | Action |
|----------|--------|
| `Ctrl + O` | Open file dialog |
| `Ctrl + Enter` | Generate code |
| `Ctrl + C` | Copy current code |
| `1-5` | Switch between tabs |

---

## 🔧 Configuration Options

### Backend Configuration (`config.py`)

```python
# Server Settings
HOST = "0.0.0.0"
PORT = 8000

# File Upload Limits
MAX_IMAGE_SIZE_MB = 10
ALLOWED_IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ...]

# Model Configuration
MODEL_PATH = "backend/models/ui_classification_model.h5"

# CORS Settings
ALLOWED_ORIGINS = ["http://localhost:5173", ...]
```

### Frontend Configuration (`src/config.js`)

```javascript
export const API_BASE_URL = "http://localhost:8000";
```

---

## 🧪 Testing

### Manual Testing
1. Upload simple UI screenshots (login forms, buttons)
2. Verify element detection accuracy
3. Check code quality and formatting
4. Test across different frameworks
5. Validate responsive behavior

### API Testing
```bash
# Test health endpoint
curl http://localhost:8000/health

# Test analysis endpoint
curl -X POST "http://localhost:8000/analyze" \
  -F "file=@test_ui.png"
```

---

## 📈 Future Enhancements

### Planned Features
1. **Advanced UI Elements**
   - Dropdowns, modals, navigation bars
   - Complex form layouts
   - Dynamic components

2. **Multi-Page Support**
   - Detect and link multiple screens
   - Generate routing code
   - State management integration

3. **Design System Integration**
   - Support for popular design systems
   - Custom component libraries
   - Theme customization

4. **Improved AI**
   - Larger training dataset
   - Better accuracy for edge cases
   - Text recognition (OCR) enhancement

5. **Export Options**
   - Direct export to CodeSandbox
   - GitHub repository generation
   - Figma plugin integration

---

## 🤝 Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests if applicable
5. Submit a pull request

---

## 📝 Documentation

- **Quick Start**: `QUICKSTART.md`
- **Model Integration**: `backend/MODEL_INTEGRATION.md`
- **API Documentation**: `http://localhost:8000/docs` (when running)
- **Main README**: `README.md`

---

## 🙏 Acknowledgments

- TensorFlow/Keras for ML framework
- OpenCV for computer vision
- FastAPI for backend framework
- React and Vite for frontend
- TailwindCSS for styling

---

## 📄 License

This project is licensed under the MIT License.

---

## 📧 Contact

**Repository**: [github.com/piyushsayare8/figma-to-multicode-generator](https://github.com/piyushsayare8/figma-to-multicode-generator)

---

**Built with ❤️ using AI, Computer Vision, and Modern Web Technologies**
