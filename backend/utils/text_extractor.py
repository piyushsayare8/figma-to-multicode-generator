"""
Advanced Text Extractor - OCR for UI Screenshots.

Extracts text content from UI screenshots using OCR (Optical Character Recognition).
This enables generating code with actual text from the design instead of placeholders.

Supports multiple OCR engines:
1. EasyOCR (primary) - No Tesseract installation needed
2. Tesseract (fallback) - If available on system
"""

import logging
from typing import List, Dict, Any, Tuple, Optional
import cv2
import numpy as np

logger = logging.getLogger(__name__)

# Try to import OCR libraries
EASYOCR_AVAILABLE = False
TESSERACT_AVAILABLE = False

try:
    import easyocr
    EASYOCR_AVAILABLE = True
    logger.info("EasyOCR is available for text detection")
except ImportError:
    logger.warning("EasyOCR not available. Install with: pip install easyocr")

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
    logger.info("Pytesseract is available for text detection")
except ImportError:
    logger.warning("Pytesseract not available. Install with: pip install pytesseract")


class TextExtractor:
    """Extract text from UI screenshots using OCR."""
    
    def __init__(self):
        """Initialize text extractor with available OCR engine."""
        self.reader = None
        self.ocr_method = "none"
        
        if EASYOCR_AVAILABLE:
            try:
                # Initialize EasyOCR reader (English only for speed)
                self.reader = easyocr.Reader(['en'], gpu=False)
                self.ocr_method = "easyocr"
                logger.info("Initialized EasyOCR reader")
            except Exception as e:
                logger.warning(f"Failed to initialize EasyOCR: {e}")
                
        if self.ocr_method == "none" and TESSERACT_AVAILABLE:
            self.ocr_method = "tesseract"
            logger.info("Using Tesseract OCR")
    
    def extract_text_from_region(
        self, 
        image_bgr: np.ndarray, 
        block: Dict[str, int]
    ) -> Optional[str]:
        """
        Extract text from a specific region of the image.
        
        Args:
            image_bgr: Full image in BGR format
            block: Block dictionary with x, y, w, h keys
            
        Returns:
            Extracted text or None if no text found
        """
        if self.ocr_method == "none":
            return None
        
        try:
            # Extract region
            x, y, w, h = block['x'], block['y'], block['w'], block['h']
            
            # Add padding for better OCR
            padding = 5
            x = max(0, x - padding)
            y = max(0, y - padding)
            w = min(image_bgr.shape[1] - x, w + 2 * padding)
            h = min(image_bgr.shape[0] - y, h + 2 * padding)
            
            crop = image_bgr[y:y+h, x:x+w]
            
            if crop.size == 0:
                return None
            
            # Preprocess for better OCR
            crop = self._preprocess_for_ocr(crop)
            
            # Extract text based on available method
            if self.ocr_method == "easyocr":
                return self._extract_easyocr(crop)
            elif self.ocr_method == "tesseract":
                return self._extract_tesseract(crop)
                
        except Exception as e:
            logger.debug(f"Error extracting text: {e}")
            return None
    
    def _preprocess_for_ocr(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for better OCR accuracy."""
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Resize if too small (OCR works better on larger text)
        min_height = 30
        if gray.shape[0] < min_height:
            scale = min_height / gray.shape[0]
            new_width = int(gray.shape[1] * scale)
            gray = cv2.resize(gray, (new_width, min_height), interpolation=cv2.INTER_CUBIC)
        
        # Apply binary thresholding
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(binary, None, 10, 7, 21)
        
        return denoised
    
    def _extract_easyocr(self, image: np.ndarray) -> Optional[str]:
        """Extract text using EasyOCR."""
        try:
            results = self.reader.readtext(image, detail=0)
            if results:
                # Join all detected text
                text = ' '.join(results).strip()
                return text if text else None
        except Exception as e:
            logger.debug(f"EasyOCR extraction failed: {e}")
        return None
    
    def _extract_tesseract(self, image: np.ndarray) -> Optional[str]:
        """Extract text using Tesseract."""
        try:
            # Use pytesseract
            text = pytesseract.image_to_string(image, config='--psm 6').strip()
            return text if text else None
        except Exception as e:
            logger.debug(f"Tesseract extraction failed: {e}")
        return None
    
    def extract_all_text(
        self, 
        image_bgr: np.ndarray, 
        blocks: List[Dict[str, Any]]
    ) -> Dict[int, str]:
        """
        Extract text from all blocks.
        
        Args:
            image_bgr: Full image
            blocks: List of detected blocks
            
        Returns:
            Dictionary mapping block index to extracted text
        """
        text_map = {}
        
        for idx, block in enumerate(blocks):
            text = self.extract_text_from_region(image_bgr, block)
            if text:
                text_map[idx] = text
                logger.debug(f"Block {idx}: extracted '{text}'")
        
        return text_map


def create_text_extractor() -> TextExtractor:
    """Factory function to create text extractor."""
    return TextExtractor()
