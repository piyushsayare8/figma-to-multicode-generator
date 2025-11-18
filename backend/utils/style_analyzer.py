"""
Style Analyzer - Color, Spacing, and Typography Extraction.

This module extracts visual style information from UI screenshots using pure
OpenCV and NumPy operations. It provides:
  - Global color palette extraction (k-means clustering)
  - Per-block style hints (background color, border radius, variant)
  - Spacing and layout rhythm estimation
  - Typography scale approximation

NO external ML models - only deterministic image processing.
"""

import logging
from typing import List, Dict, Any, Tuple, Optional
import cv2
import numpy as np
from collections import Counter

logger = logging.getLogger(__name__)

# ============================================================================
# CONSTANTS - All thresholds and configuration
# ============================================================================

# Color analysis
KMEANS_CLUSTERS = 5  # Number of dominant colors to extract
KMEANS_ATTEMPTS = 3
KMEANS_MAX_ITER = 100
MIN_COLOR_PROMINENCE = 0.05  # Minimum 5% of pixels to be considered dominant

# Background detection
EDGE_SAMPLE_WIDTH = 20  # Pixels from edge to sample for background
BACKGROUND_UNIFORMITY_THRESHOLD = 30  # Max std dev for uniform background

# Per-block style
SOLID_FILL_THRESHOLD = 0.7  # 70% uniform color = solid fill
BORDER_RADIUS_SMALL = 4
BORDER_RADIUS_MEDIUM = 12
BORDER_RADIUS_LARGE = 24
BORDER_RADIUS_FULL = 999  # For pills/rounded buttons

# Spacing analysis
SPACING_SMALL = 8
SPACING_MEDIUM = 16
SPACING_LARGE = 24
MIN_BLOCKS_FOR_SPACING = 3  # Need at least 3 blocks to infer spacing

# Typography scale (based on block height)
FONT_SIZE_CAPTION = 12
FONT_SIZE_BODY = 16
FONT_SIZE_HEADING_SMALL = 20
FONT_SIZE_HEADING_LARGE = 32

# Layout detection
COLUMN_DETECTION_TOLERANCE = 40  # Pixels tolerance for column alignment


# ============================================================================
# COLOR ANALYSIS
# ============================================================================

def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
    """Convert RGB tuple to hex color string."""
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"


def extract_dominant_colors(image_bgr: np.ndarray, k: int = KMEANS_CLUSTERS) -> List[Tuple[str, float]]:
    """
    Extract dominant colors using k-means clustering.
    
    Args:
        image_bgr: Input image in BGR format
        k: Number of clusters (dominant colors)
        
    Returns:
        List of (hex_color, prominence) tuples sorted by prominence
    """
    # Reshape image to list of pixels
    pixels = image_bgr.reshape((-1, 3))
    pixels = np.float32(pixels)
    
    # Apply k-means clustering
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, KMEANS_MAX_ITER, 0.2)
    _, labels, centers = cv2.kmeans(
        pixels, k, None, criteria, KMEANS_ATTEMPTS, cv2.KMEANS_PP_CENTERS
    )
    
    # Convert BGR centers to RGB
    centers = np.uint8(centers)
    centers_rgb = centers[:, [2, 1, 0]]  # BGR to RGB
    
    # Count cluster sizes (prominence)
    label_counts = Counter(labels.flatten())
    total_pixels = len(labels)
    
    # Create color prominence list
    colors = []
    for idx, center_rgb in enumerate(centers_rgb):
        count = label_counts[idx]
        prominence = count / total_pixels
        
        if prominence >= MIN_COLOR_PROMINENCE:
            hex_color = rgb_to_hex(tuple(center_rgb))
            colors.append((hex_color, prominence))
    
    # Sort by prominence (descending)
    colors.sort(key=lambda x: x[1], reverse=True)
    
    return colors


def detect_background_color(image_bgr: np.ndarray) -> str:
    """
    Detect the background color by sampling edges of the image.
    
    Args:
        image_bgr: Input image in BGR format
        
    Returns:
        Hex color string for background
    """
    h, w = image_bgr.shape[:2]
    
    # Sample pixels from all four edges
    edge_pixels = []
    
    # Top edge
    edge_pixels.append(image_bgr[:EDGE_SAMPLE_WIDTH, :])
    # Bottom edge
    edge_pixels.append(image_bgr[-EDGE_SAMPLE_WIDTH:, :])
    # Left edge
    edge_pixels.append(image_bgr[:, :EDGE_SAMPLE_WIDTH])
    # Right edge
    edge_pixels.append(image_bgr[:, -EDGE_SAMPLE_WIDTH:])
    
    # Concatenate all edge pixels
    edge_pixels = np.concatenate([ep.reshape(-1, 3) for ep in edge_pixels])
    
    # Calculate mean color
    mean_color_bgr = np.mean(edge_pixels, axis=0).astype(np.uint8)
    mean_color_rgb = mean_color_bgr[[2, 1, 0]]  # BGR to RGB
    
    return rgb_to_hex(tuple(mean_color_rgb))


def assign_color_roles(colors: List[Tuple[str, float]], background_color: str) -> Dict[str, str]:
    """
    Assign semantic roles to dominant colors.
    
    Args:
        colors: List of (hex_color, prominence) tuples
        background_color: Detected background hex color
        
    Returns:
        Dict with keys: background_color, primary_color, accent_color, text_color
    """
    roles = {
        "background_color": background_color,
        "primary_color": "#2563eb",  # Default blue
        "accent_color": "#f59e0b",   # Default amber
        "text_color": "#111827"      # Default dark gray
    }
    
    if not colors:
        return roles
    
    # Filter out background color from candidates
    candidates = [c for c in colors if c[0].lower() != background_color.lower()]
    
    if not candidates:
        return roles
    
    # Most prominent non-background color = primary
    roles["primary_color"] = candidates[0][0]
    
    # Second most prominent = accent (if exists)
    if len(candidates) > 1:
        roles["accent_color"] = candidates[1][0]
    
    # Text color: find darkest color for light backgrounds, lightest for dark
    # Simple heuristic: calculate luminance
    bg_luminance = calculate_luminance(background_color)
    
    if bg_luminance > 0.5:  # Light background
        # Find darkest color
        darkest = min(colors, key=lambda c: calculate_luminance(c[0]))
        roles["text_color"] = darkest[0]
    else:  # Dark background
        # Find lightest color
        lightest = max(colors, key=lambda c: calculate_luminance(c[0]))
        roles["text_color"] = lightest[0]
    
    return roles


def calculate_luminance(hex_color: str) -> float:
    """
    Calculate relative luminance of a color (0.0 = black, 1.0 = white).
    
    Args:
        hex_color: Hex color string (e.g., "#2563eb")
        
    Returns:
        Luminance value between 0 and 1
    """
    # Remove '#' if present
    hex_color = hex_color.lstrip('#')
    
    # Convert to RGB
    r = int(hex_color[0:2], 16) / 255.0
    g = int(hex_color[2:4], 16) / 255.0
    b = int(hex_color[4:6], 16) / 255.0
    
    # Apply gamma correction and calculate luminance
    # https://www.w3.org/TR/WCAG20/#relativeluminancedef
    def adjust(c):
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    
    r, g, b = adjust(r), adjust(g), adjust(b)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


# ============================================================================
# PER-BLOCK STYLE HINTS
# ============================================================================

def analyze_block_style(image_bgr: np.ndarray, rect: Dict[str, int]) -> Dict[str, Any]:
    """
    Analyze style properties of a single block.
    
    Args:
        image_bgr: Full image in BGR format
        rect: Block rectangle with keys: x, y, w, h
        
    Returns:
        Dict with style properties: bg_color, text_color, border_radius, variant
    """
    x, y, w, h = rect['x'], rect['y'], rect['w'], rect['h']
    
    # Ensure coordinates are within image bounds
    img_h, img_w = image_bgr.shape[:2]
    x = max(0, min(x, img_w - 1))
    y = max(0, min(y, img_h - 1))
    w = max(1, min(w, img_w - x))
    h = max(1, min(h, img_h - y))
    
    # Extract block region
    block = image_bgr[y:y+h, x:x+w]
    
    if block.size == 0:
        return _default_block_style()
    
    # Analyze background color
    bg_color = _extract_block_bg_color(block)
    
    # Detect if solid fill or outline variant
    variant = _detect_variant(block)
    
    # Estimate border radius
    border_radius = _estimate_border_radius(block, w, h)
    
    # Estimate text color (inverse of bg for now)
    text_color = _estimate_text_color(bg_color)
    
    return {
        "bg_color": bg_color,
        "text_color": text_color,
        "border_radius": border_radius,
        "variant": variant
    }


def _default_block_style() -> Dict[str, Any]:
    """Return default block style when extraction fails."""
    return {
        "bg_color": "#ffffff",
        "text_color": "#111827",
        "border_radius": 8,
        "variant": "solid"
    }


def _extract_block_bg_color(block: np.ndarray) -> str:
    """Extract dominant background color from block."""
    # Use center region of block (avoid edges that might be borders)
    h, w = block.shape[:2]
    center_h, center_w = int(h * 0.6), int(w * 0.6)
    start_y, start_x = (h - center_h) // 2, (w - center_w) // 2
    
    center_region = block[start_y:start_y+center_h, start_x:start_x+center_w]
    
    if center_region.size == 0:
        return "#ffffff"
    
    mean_color_bgr = np.mean(center_region.reshape(-1, 3), axis=0).astype(np.uint8)
    mean_color_rgb = mean_color_bgr[[2, 1, 0]]
    
    return rgb_to_hex(tuple(mean_color_rgb))


def _detect_variant(block: np.ndarray) -> str:
    """
    Detect if block is solid fill or outline variant.
    
    Args:
        block: Block image region
        
    Returns:
        "solid" or "outline"
    """
    # Calculate color uniformity
    std_dev = np.std(block)
    
    # Also check edge vs center contrast
    h, w = block.shape[:2]
    if h < 4 or w < 4:
        return "solid"
    
    # Sample edge pixels
    edge_pixels = np.concatenate([
        block[0, :].reshape(-1, 3),
        block[-1, :].reshape(-1, 3),
        block[:, 0].reshape(-1, 3),
        block[:, -1].reshape(-1, 3)
    ])
    
    # Sample center pixels
    center_h, center_w = h // 2, w // 2
    center_pixels = block[center_h-2:center_h+2, center_w-2:center_w+2].reshape(-1, 3)
    
    edge_mean = np.mean(edge_pixels, axis=0)
    center_mean = np.mean(center_pixels, axis=0)
    
    contrast = np.linalg.norm(edge_mean - center_mean)
    
    # High contrast + low overall std = outline variant
    if contrast > 50 and std_dev < 40:
        return "outline"
    
    return "solid"


def _estimate_border_radius(block: np.ndarray, w: int, h: int) -> int:
    """
    Estimate border radius based on corner analysis.
    
    Args:
        block: Block image region
        w: Block width
        h: Block height
        
    Returns:
        Estimated border radius in pixels
    """
    # For very small blocks, assume small radius
    if w < 20 or h < 20:
        return BORDER_RADIUS_SMALL
    
    # Check aspect ratio for pill-shaped buttons
    aspect_ratio = w / h if h > 0 else 1
    
    if 2.5 < aspect_ratio < 6 and h < 60:  # Typical button shape
        # Check if corners are rounded by sampling
        if _has_rounded_corners(block):
            return BORDER_RADIUS_FULL  # Pill shape
    
    # Check corner pixel patterns for radius estimation
    corner_roundness = _measure_corner_roundness(block)
    
    if corner_roundness > 0.7:
        return BORDER_RADIUS_LARGE
    elif corner_roundness > 0.4:
        return BORDER_RADIUS_MEDIUM
    else:
        return BORDER_RADIUS_SMALL


def _has_rounded_corners(block: np.ndarray) -> bool:
    """Check if block has rounded corners."""
    h, w = block.shape[:2]
    sample_size = min(10, h // 4, w // 4)
    
    if sample_size < 3:
        return False
    
    # Sample corner regions
    corners = [
        block[0:sample_size, 0:sample_size],  # Top-left
        block[0:sample_size, -sample_size:],  # Top-right
        block[-sample_size:, 0:sample_size],  # Bottom-left
        block[-sample_size:, -sample_size:]   # Bottom-right
    ]
    
    # Check if corner pixels differ significantly from edge pixels
    rounded_corners = 0
    for corner in corners:
        corner_std = np.std(corner)
        if corner_std > 20:  # High variance suggests rounded cutoff
            rounded_corners += 1
    
    return rounded_corners >= 3


def _measure_corner_roundness(block: np.ndarray) -> float:
    """
    Measure corner roundness (0.0 = sharp, 1.0 = very rounded).
    
    Returns:
        Roundness score between 0 and 1
    """
    h, w = block.shape[:2]
    
    if h < 10 or w < 10:
        return 0.0
    
    # Convert to grayscale for edge detection
    gray = cv2.cvtColor(block, cv2.COLOR_BGR2GRAY)
    
    # Apply edge detection
    edges = cv2.Canny(gray, 50, 150)
    
    # Sample corners
    sample_size = min(15, h // 3, w // 3)
    
    corners = [
        edges[0:sample_size, 0:sample_size],
        edges[0:sample_size, -sample_size:],
        edges[-sample_size:, 0:sample_size],
        edges[-sample_size:, -sample_size:]
    ]
    
    # Count edge pixels in corners
    total_corner_pixels = 4 * sample_size * sample_size
    edge_corner_pixels = sum(np.sum(corner > 0) for corner in corners)
    
    # More edge pixels in corners = more rounded
    roundness = edge_corner_pixels / total_corner_pixels
    
    return min(1.0, roundness * 2)  # Scale up


def _estimate_text_color(bg_color: str) -> str:
    """Estimate appropriate text color based on background."""
    luminance = calculate_luminance(bg_color)
    
    # Light background -> dark text
    if luminance > 0.5:
        return "#111827"
    else:
        return "#f9fafb"


# ============================================================================
# SPACING AND LAYOUT RHYTHM
# ============================================================================

def estimate_spacing_scale(blocks: List[Dict[str, int]]) -> Dict[str, int]:
    """
    Estimate spacing scale from block positions.
    
    Args:
        blocks: List of block dictionaries with x, y, w, h
        
    Returns:
        Dict with small, medium, large spacing values
    """
    if len(blocks) < MIN_BLOCKS_FOR_SPACING:
        return {
            "small": SPACING_SMALL,
            "medium": SPACING_MEDIUM,
            "large": SPACING_LARGE
        }
    
    # Calculate vertical gaps between blocks
    vertical_gaps = []
    sorted_blocks = sorted(blocks, key=lambda b: b['y'])
    
    for i in range(len(sorted_blocks) - 1):
        current_bottom = sorted_blocks[i]['y'] + sorted_blocks[i]['h']
        next_top = sorted_blocks[i + 1]['y']
        gap = next_top - current_bottom
        
        if 0 < gap < 100:  # Reasonable gap range
            vertical_gaps.append(gap)
    
    # Calculate horizontal gaps
    horizontal_gaps = []
    sorted_blocks_x = sorted(blocks, key=lambda b: b['x'])
    
    for i in range(len(sorted_blocks_x) - 1):
        current_right = sorted_blocks_x[i]['x'] + sorted_blocks_x[i]['w']
        next_left = sorted_blocks_x[i + 1]['x']
        gap = next_left - current_right
        
        if 0 < gap < 100:
            horizontal_gaps.append(gap)
    
    all_gaps = vertical_gaps + horizontal_gaps
    
    if not all_gaps:
        return {
            "small": SPACING_SMALL,
            "medium": SPACING_MEDIUM,
            "large": SPACING_LARGE
        }
    
    # Use quartiles to estimate spacing scale
    all_gaps_sorted = sorted(all_gaps)
    q1 = all_gaps_sorted[len(all_gaps_sorted) // 4]
    q2 = all_gaps_sorted[len(all_gaps_sorted) // 2]
    q3 = all_gaps_sorted[3 * len(all_gaps_sorted) // 4]
    
    return {
        "small": max(4, int(q1)),
        "medium": max(8, int(q2)),
        "large": max(16, int(q3))
    }


def estimate_base_spacing(blocks: List[Dict[str, int]]) -> int:
    """
    Estimate the base spacing unit used in the layout.
    
    Returns:
        Base spacing in pixels (typically 8, 12, or 16)
    """
    spacing_scale = estimate_spacing_scale(blocks)
    return spacing_scale["medium"]


def detect_column_layout(blocks: List[Dict[str, int]], image_width: int) -> Dict[str, Any]:
    """
    Detect column-based layout patterns.
    
    Args:
        blocks: List of blocks with x, y, w, h
        image_width: Width of the image
        
    Returns:
        Dict with layout_mode and column_count
    """
    if len(blocks) < 2:
        return {"layout_mode": "single_column", "column_count": 1}
    
    # Group blocks by approximate x position
    x_positions = [b['x'] for b in blocks]
    x_clusters = _cluster_positions(x_positions, COLUMN_DETECTION_TOLERANCE)
    
    column_count = len(x_clusters)
    
    # Determine layout mode
    if column_count == 1:
        # Check if centered
        avg_x = np.mean([b['x'] for b in blocks])
        avg_width = np.mean([b['w'] for b in blocks])
        
        if abs(avg_x + avg_width / 2 - image_width / 2) < image_width * 0.2:
            return {"layout_mode": "centered_form", "column_count": 1}
        else:
            return {"layout_mode": "single_column", "column_count": 1}
    
    elif column_count == 2:
        return {"layout_mode": "two_column", "column_count": 2}
    
    elif column_count >= 3:
        return {"layout_mode": "grid", "column_count": column_count}
    
    return {"layout_mode": "single_column", "column_count": 1}


def _cluster_positions(positions: List[int], tolerance: int) -> List[List[int]]:
    """
    Cluster positions within tolerance.
    
    Returns:
        List of position clusters
    """
    if not positions:
        return []
    
    sorted_pos = sorted(positions)
    clusters = [[sorted_pos[0]]]
    
    for pos in sorted_pos[1:]:
        if abs(pos - clusters[-1][-1]) <= tolerance:
            clusters[-1].append(pos)
        else:
            clusters.append([pos])
    
    return clusters


# ============================================================================
# TYPOGRAPHY SCALE
# ============================================================================

def estimate_typography_scale(blocks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Estimate typography scale based on block sizes and types.
    
    Args:
        blocks: List of typed blocks with x, y, w, h, type
        
    Returns:
        Dict mapping text types to approximate font sizes
    """
    text_blocks = [b for b in blocks if b.get('type') in ['text', 'heading', 'label']]
    
    if not text_blocks:
        return {
            "heading_large": FONT_SIZE_HEADING_LARGE,
            "heading_small": FONT_SIZE_HEADING_SMALL,
            "body": FONT_SIZE_BODY,
            "caption": FONT_SIZE_CAPTION
        }
    
    # Sort by height (proxy for font size)
    heights = sorted([b['h'] for b in text_blocks])
    
    if len(heights) == 1:
        # Only one text size
        return {
            "heading_large": heights[0],
            "heading_small": heights[0],
            "body": heights[0],
            "caption": heights[0]
        }
    
    # Use quartiles
    q1 = heights[len(heights) // 4]
    q2 = heights[len(heights) // 2]
    q3 = heights[3 * len(heights) // 4]
    
    return {
        "heading_large": max(FONT_SIZE_HEADING_LARGE, heights[-1]),
        "heading_small": max(FONT_SIZE_HEADING_SMALL, q3),
        "body": max(FONT_SIZE_BODY, q2),
        "caption": max(FONT_SIZE_CAPTION, q1)
    }


# ============================================================================
# MAIN ANALYSIS FUNCTION
# ============================================================================

def analyze_style(image_bgr: np.ndarray, typed_blocks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Perform complete style analysis on image and blocks.
    
    Args:
        image_bgr: Input image in BGR format
        typed_blocks: List of blocks with x, y, w, h, type, confidence
        
    Returns:
        Dict with structure:
        {
            "page": {
                "background_color": str,
                "primary_color": str,
                "accent_color": str,
                "text_color": str,
                "base_spacing": int,
                "layout_mode": str,
                "column_count": int
            },
            "blocks": [
                {
                    "id": str,
                    "rect": {...},
                    "type": str,
                    "style": {...}
                },
                ...
            ],
            "typography": {...}
        }
    """
    logger.info(f"Analyzing style for {len(typed_blocks)} blocks")
    
    # 1. Extract dominant colors
    dominant_colors = extract_dominant_colors(image_bgr)
    logger.debug(f"Extracted {len(dominant_colors)} dominant colors")
    
    # 2. Detect background color
    background_color = detect_background_color(image_bgr)
    logger.debug(f"Background color: {background_color}")
    
    # 3. Assign color roles
    color_roles = assign_color_roles(dominant_colors, background_color)
    
    # 4. Estimate spacing
    base_spacing = estimate_base_spacing(typed_blocks)
    spacing_scale = estimate_spacing_scale(typed_blocks)
    
    # 5. Detect layout mode
    img_h, img_w = image_bgr.shape[:2]
    layout_info = detect_column_layout(typed_blocks, img_w)
    
    # 6. Analyze typography
    typography = estimate_typography_scale(typed_blocks)
    
    # 7. Analyze per-block styles
    styled_blocks = []
    for idx, block in enumerate(typed_blocks):
        block_style = analyze_block_style(image_bgr, block)
        
        styled_block = {
            "id": f"block_{idx}",
            "rect": {
                "x": block['x'],
                "y": block['y'],
                "w": block['w'],
                "h": block['h']
            },
            "type": block.get('type', 'unknown'),
            "confidence": block.get('confidence', 0.0),
            "style": block_style
        }
        
        styled_blocks.append(styled_block)
    
    # 8. Compile complete style summary
    style_summary = {
        "page": {
            **color_roles,
            "base_spacing": base_spacing,
            "spacing_scale": spacing_scale,
            **layout_info
        },
        "blocks": styled_blocks,
        "typography": typography
    }
    
    logger.info("Style analysis complete")
    return style_summary


# ============================================================================
# CLI TESTING UTILITY
# ============================================================================

if __name__ == "__main__":
    """
    CLI utility for testing style analysis on a local image.
    
    Usage:
        python style_analyzer.py <path_to_image>
    """
    import sys
    import json
    
    if len(sys.argv) < 2:
        print("Usage: python style_analyzer.py <path_to_image>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    # Load image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Could not load image from {image_path}")
        sys.exit(1)
    
    print(f"Loaded image: {image.shape}")
    
    # Create dummy blocks for testing (you can replace with actual detection)
    h, w = image.shape[:2]
    dummy_blocks = [
        {"x": w//4, "y": h//4, "w": w//2, "h": 50, "type": "button"},
        {"x": w//4, "y": h//2, "w": w//2, "h": 40, "type": "text_input"},
        {"x": w//4, "y": h//2 + 60, "w": w//2, "h": 40, "type": "text_input"},
    ]
    
    # Analyze style
    style_info = analyze_style(image, dummy_blocks)
    
    # Print results
    print("\n" + "="*60)
    print("STYLE ANALYSIS RESULTS")
    print("="*60)
    print(json.dumps(style_info, indent=2))
    
    # Save to file
    output_path = image_path.rsplit('.', 1)[0] + '_style.json'
    with open(output_path, 'w') as f:
        json.dump(style_info, f, indent=2)
    
    print(f"\nStyle analysis saved to: {output_path}")
