"""
Advanced Visual Style Extractor - Pixel-Perfect Design Replication.

Extracts detailed visual styling from UI screenshots:
- Exact colors (background, text, borders)
- Border radius detection
- Shadow detection
- Font size estimation
- Spacing and padding
- Positioning (absolute coordinates)

This enables generating code that visually matches the original design.
"""

import logging
from typing import List, Dict, Any, Tuple, Optional
import cv2
import numpy as np

logger = logging.getLogger(__name__)


class VisualStyleExtractor:
    """Extract detailed visual styling from UI blocks."""
    
    def __init__(self, image_bgr: np.ndarray):
        """
        Initialize extractor with the image.
        
        Args:
            image_bgr: Input image in BGR format
        """
        self.image_bgr = image_bgr
        self.image_height, self.image_width = image_bgr.shape[:2]
    
    def extract_block_style(self, block: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract detailed style information for a single block.
        
        Args:
            block: Block dictionary with x, y, w, h keys
            
        Returns:
            Style dictionary with colors, borders, shadows, etc.
        """
        x, y, w, h = block['x'], block['y'], block['w'], block['h']
        
        # Ensure valid bounds
        x = max(0, min(x, self.image_width - 1))
        y = max(0, min(y, self.image_height - 1))
        w = max(1, min(w, self.image_width - x))
        h = max(1, min(h, self.image_height - y))
        
        crop = self.image_bgr[y:y+h, x:x+w]
        
        if crop.size == 0:
            return self._default_style()
        
        style = {
            'position': {'x': x, 'y': y},
            'size': {'width': w, 'height': h},
            'colors': self._extract_colors(crop),
            'border': self._detect_border(crop),
            'border_radius': self._estimate_border_radius(crop, w, h),
            'shadow': self._detect_shadow(x, y, w, h),
            'font_size': self._estimate_font_size(h),
            'padding': self._estimate_padding(crop),
        }
        
        return style
    
    def _extract_colors(self, crop: np.ndarray) -> Dict[str, str]:
        """Extract dominant colors from a crop."""
        # Get background color (most common color)
        bg_color = self._get_dominant_color(crop)
        
        # Get text color (assume opposite of background)
        text_color = self._estimate_text_color(bg_color)
        
        # Get border color (sample edges)
        border_color = self._sample_edge_color(crop)
        
        return {
            'background': self._bgr_to_hex(bg_color),
            'text': text_color,
            'border': self._bgr_to_hex(border_color) if border_color is not None else None
        }
    
    def _get_dominant_color(self, crop: np.ndarray) -> Tuple[int, int, int]:
        """Get the most dominant color in the crop."""
        # Resize for faster processing
        small = cv2.resize(crop, (50, 50))
        pixels = small.reshape((-1, 3))
        
        # Use mean as dominant color (faster than k-means)
        mean_color = np.mean(pixels, axis=0).astype(int)
        
        return tuple(mean_color.tolist())
    
    def _estimate_text_color(self, bg_color: Tuple[int, int, int]) -> str:
        """Estimate text color based on background luminance."""
        # Calculate relative luminance
        b, g, r = bg_color
        luminance = 0.299 * r + 0.587 * g + 0.114 * b
        
        # Use white text on dark backgrounds, black on light
        if luminance < 128:
            return '#ffffff'
        else:
            return '#000000'
    
    def _sample_edge_color(self, crop: np.ndarray) -> Optional[Tuple[int, int, int]]:
        """Sample color from edges to detect borders."""
        h, w = crop.shape[:2]
        
        if h < 4 or w < 4:
            return None
        
        # Sample 1-pixel border around the crop
        edge_pixels = []
        edge_pixels.extend(crop[0, :].tolist())  # Top
        edge_pixels.extend(crop[-1, :].tolist())  # Bottom
        edge_pixels.extend(crop[:, 0].tolist())  # Left
        edge_pixels.extend(crop[:, -1].tolist())  # Right
        
        edge_pixels = np.array(edge_pixels)
        mean_edge = np.mean(edge_pixels, axis=0).astype(int)
        
        return tuple(mean_edge.tolist())
    
    def _detect_border(self, crop: np.ndarray) -> Dict[str, Any]:
        """Detect if the block has a visible border."""
        h, w = crop.shape[:2]
        
        if h < 4 or w < 4:
            return {'has_border': False, 'width': 0}
        
        # Sample center vs edges
        center = crop[h//4:3*h//4, w//4:3*w//4]
        
        # Get edge strip (2 pixels wide)
        edge_strip = np.concatenate([
            crop[:2, :].reshape(-1, 3),
            crop[-2:, :].reshape(-1, 3),
            crop[:, :2].reshape(-1, 3),
            crop[:, -2:].reshape(-1, 3)
        ])
        
        # Calculate color difference
        center_mean = np.mean(center, axis=(0, 1))
        edge_mean = np.mean(edge_strip, axis=0)
        
        diff = np.linalg.norm(center_mean - edge_mean)
        
        # If significant difference, there's likely a border
        has_border = diff > 30
        border_width = 1 if diff > 30 else (2 if diff > 60 else 0)
        
        return {
            'has_border': has_border,
            'width': border_width
        }
    
    def _estimate_border_radius(
        self, 
        crop: np.ndarray, 
        w: int, 
        h: int
    ) -> int:
        """Estimate border radius by checking corners."""
        if crop.size == 0 or w < 10 or h < 10:
            return 0
        
        # Convert to grayscale
        gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        
        # Check all four corners
        corner_size = min(15, w // 3, h // 3)
        corners = [
            gray[:corner_size, :corner_size],  # Top-left
            gray[:corner_size, -corner_size:],  # Top-right
            gray[-corner_size:, :corner_size],  # Bottom-left
            gray[-corner_size:, -corner_size:]  # Bottom-right
        ]
        
        # Count non-uniform corners (suggests rounding)
        rounded_corners = 0
        for corner in corners:
            std = np.std(corner)
            if std > 20:  # High variance = curved corner
                rounded_corners += 1
        
        # Estimate radius based on corner analysis
        if rounded_corners >= 3:
            if min(w, h) < 60:
                return 4  # Small radius for small elements
            elif min(w, h) < 120:
                return 8  # Medium radius
            else:
                return 12  # Large radius
        
        return 0  # Sharp corners
    
    def _detect_shadow(
        self, 
        x: int, 
        y: int, 
        w: int, 
        h: int
    ) -> Dict[str, Any]:
        """Detect if the block has a shadow."""
        # Check pixels around the block for darker regions
        padding = 5
        
        x1 = max(0, x - padding)
        y1 = max(0, y - padding)
        x2 = min(self.image_width, x + w + padding)
        y2 = min(self.image_height, y + h + padding)
        
        # Sample area around block
        if x2 > x1 and y2 > y1:
            surrounding = self.image_bgr[y1:y2, x1:x2]
            block_crop = self.image_bgr[y:y+h, x:x+w]
            
            # Compare luminance
            surr_lum = np.mean(cv2.cvtColor(surrounding, cv2.COLOR_BGR2GRAY))
            block_lum = np.mean(cv2.cvtColor(block_crop, cv2.COLOR_BGR2GRAY))
            
            has_shadow = (block_lum - surr_lum) > 15
            
            return {
                'has_shadow': has_shadow,
                'blur': 10 if has_shadow else 0,
                'spread': 2 if has_shadow else 0,
                'color': 'rgba(0, 0, 0, 0.1)' if has_shadow else None
            }
        
        return {'has_shadow': False, 'blur': 0, 'spread': 0, 'color': None}
    
    def _estimate_font_size(self, height: int) -> int:
        """Estimate font size based on element height."""
        if height < 25:
            return 12  # Small text
        elif height < 40:
            return 14  # Normal text
        elif height < 50:
            return 16  # Medium text
        elif height < 70:
            return 20  # Large text
        else:
            return 24  # Heading
    
    def _estimate_padding(self, crop: np.ndarray) -> Dict[str, int]:
        """Estimate padding inside the element."""
        h, w = crop.shape[:2]
        
        # Simple heuristic based on size
        if min(w, h) < 40:
            padding = 4
        elif min(w, h) < 80:
            padding = 8
        elif min(w, h) < 150:
            padding = 12
        else:
            padding = 16
        
        return {
            'top': padding,
            'right': padding,
            'bottom': padding,
            'left': padding
        }
    
    def _bgr_to_hex(self, bgr: Tuple[int, int, int]) -> str:
        """Convert BGR tuple to hex color."""
        b, g, r = bgr
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def _default_style(self) -> Dict[str, Any]:
        """Return default style when extraction fails."""
        return {
            'position': {'x': 0, 'y': 0},
            'size': {'width': 100, 'height': 40},
            'colors': {
                'background': '#ffffff',
                'text': '#000000',
                'border': '#cccccc'
            },
            'border': {'has_border': True, 'width': 1},
            'border_radius': 4,
            'shadow': {'has_shadow': False, 'blur': 0, 'spread': 0, 'color': None},
            'font_size': 14,
            'padding': {'top': 8, 'right': 12, 'bottom': 8, 'left': 12}
        }
