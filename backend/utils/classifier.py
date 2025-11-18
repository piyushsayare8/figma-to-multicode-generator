"""
CNN-based UI element classifier with production-ready interface.

This module provides a pluggable interface for loading and using CNN models
to classify detected UI blocks. The interface is designed to be easily
replaceable with your own trained models.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import os
from pathlib import Path

from config import Config, UI_ELEMENT_TYPES, FALLBACK_ELEMENT_TYPE

logger = logging.getLogger(__name__)

# Optional imports - will gracefully degrade if not available
try:
    import torch
    import torch.nn as nn
    import torchvision.transforms as transforms
    TORCH_AVAILABLE = True
except ImportError:
    logger.warning("PyTorch not available - using stub classifier")
    TORCH_AVAILABLE = False

try:
    import tensorflow as tf
    TF_AVAILABLE = True
except ImportError:
    logger.warning("TensorFlow not available")
    TF_AVAILABLE = False

class StubClassifier:
    """
    Stub classifier for development and testing.
    
    This classifier assigns types based on simple heuristics when no
    trained model is available.
    """
    
    def predict(self, block_images: List[np.ndarray]) -> List[str]:
        """
        Predict UI element types based on simple heuristics.
        
        Args:
            block_images: List of cropped block images
            
        Returns:
            List of predicted types
        """
        predictions = []
        
        for img in block_images:
            if img.size == 0:
                predictions.append(FALLBACK_ELEMENT_TYPE)
                continue
                
            h, w = img.shape[:2]
            aspect_ratio = w / h if h > 0 else 1.0
            area = h * w
            
            # Simple heuristic classification
            if aspect_ratio > 3.0 and h < 50:
                # Wide and short - likely input field
                predictions.append("input_field")
            elif aspect_ratio < 0.7 and area < 5000:
                # Tall and narrow - likely button
                predictions.append("button")
            elif aspect_ratio > 2.0 and area > 10000:
                # Wide and large - likely header or card
                predictions.append("card")
            elif h < 30:
                # Short - likely text
                predictions.append("text_block")
            elif area > 20000:
                # Large - likely image
                predictions.append("image_block")
            else:
                predictions.append(FALLBACK_ELEMENT_TYPE)
        
        return predictions

class PyTorchClassifier:
    """
    PyTorch-based CNN classifier interface.
    
    TODO: Replace this with your actual PyTorch model implementation.
    """
    
    def __init__(self, model_path: Path):
        """Initialize the PyTorch classifier."""
        self.model_path = model_path
        self.model = None
        self.transform = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu') if TORCH_AVAILABLE else None
        
        if TORCH_AVAILABLE:
            # Default transforms - adjust based on your model requirements
            self.transform = transforms.Compose([
                transforms.ToPILImage(),
                transforms.Resize((64, 64)),  # Adjust size as needed
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
            ])
    
    def load(self) -> bool:
        """
        Load the PyTorch model.
        
        Returns:
            True if model loaded successfully, False otherwise
        """
        if not TORCH_AVAILABLE:
            return False
            
        try:
            if not self.model_path.exists():
                logger.error(f"Model file not found: {self.model_path}")
                return False
            
            # TODO: Replace with your actual model loading code
            # Example:
            # self.model = YourModelClass(num_classes=len(UI_ELEMENT_TYPES))
            # checkpoint = torch.load(self.model_path, map_location=self.device)
            # self.model.load_state_dict(checkpoint['model_state_dict'])
            # self.model.eval()
            # self.model.to(self.device)
            
            logger.warning("PyTorch model loading not implemented - using stub")
            return False
            
        except Exception as e:
            logger.error(f"Failed to load PyTorch model: {e}")
            return False
    
    def predict(self, block_images: List[np.ndarray]) -> List[str]:
        """
        Predict UI element types using PyTorch model.
        
        Args:
            block_images: List of cropped block images (BGR format)
            
        Returns:
            List of predicted types
        """
        if self.model is None or not TORCH_AVAILABLE:
            logger.warning("Model not loaded, falling back to stub")
            return StubClassifier().predict(block_images)
        
        try:
            predictions = []
            
            with torch.no_grad():
                for img_bgr in block_images:
                    if img_bgr.size == 0:
                        predictions.append(FALLBACK_ELEMENT_TYPE)
                        continue
                    
                    # Convert BGR to RGB
                    img_rgb = img_bgr[:, :, ::-1]
                    
                    # Apply transforms
                    img_tensor = self.transform(img_rgb).unsqueeze(0).to(self.device)
                    
                    # Get prediction
                    outputs = self.model(img_tensor)
                    _, predicted_idx = torch.max(outputs, 1)
                    
                    # Map index to class name
                    if predicted_idx.item() < len(UI_ELEMENT_TYPES):
                        predicted_type = UI_ELEMENT_TYPES[predicted_idx.item()]
                    else:
                        predicted_type = FALLBACK_ELEMENT_TYPE
                    
                    predictions.append(predicted_type)
            
            return predictions
            
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return [FALLBACK_ELEMENT_TYPE] * len(block_images)

def load_model() -> Optional[Any]:
    """
    Load the CNN classifier model.
    
    This function attempts to load a model in the following priority:
    1. PyTorch model (if available)
    2. TensorFlow model (if available)  
    3. Fallback to stub classifier
    
    Returns:
        Loaded model instance or None if no model could be loaded
    """
    if not Config.MODEL_PATH:
        logger.warning("No model path configured, using stub classifier")
        return StubClassifier()
    
    model_path = Path(Config.MODEL_PATH)
    
    # Try PyTorch first
    if TORCH_AVAILABLE and model_path.suffix in ['.pth', '.pt']:
        logger.info("Attempting to load PyTorch model...")
        classifier = PyTorchClassifier(model_path)
        if classifier.load():
            logger.info("PyTorch model loaded successfully")
            return classifier
    
    # Fallback to stub
    logger.info("Using stub classifier for development")
    return StubClassifier()

def extract_block_images(image_bgr: np.ndarray, blocks: List[Dict[str, int]]) -> List[np.ndarray]:
    """
    Extract cropped images for each detected block.
    
    Args:
        image_bgr: Original image in BGR format
        blocks: List of block coordinates
        
    Returns:
        List of cropped block images
    """
    block_images = []
    
    for block in blocks:
        x, y, w, h = block['x'], block['y'], block['w'], block['h']
        
        # Ensure coordinates are within image bounds
        img_h, img_w = image_bgr.shape[:2]
        x = max(0, min(x, img_w - 1))
        y = max(0, min(y, img_h - 1))
        w = max(1, min(w, img_w - x))
        h = max(1, min(h, img_h - y))
        
        # Extract the block
        block_img = image_bgr[y:y+h, x:x+w]
        
        # Handle edge case where block is empty
        if block_img.size == 0:
            # Create a small placeholder image
            block_img = np.zeros((10, 10, 3), dtype=np.uint8)
        
        block_images.append(block_img)
    
    return block_images

def classify_blocks(model: Optional[Any], image_bgr: np.ndarray, blocks: List[Dict[str, int]]) -> List[Dict[str, Any]]:
    """
    Classify detected blocks using the loaded CNN model.
    
    This is the main interface function that your app.py will call.
    
    Args:
        model: Loaded classifier model (from load_model())
        image_bgr: Original image in BGR format
        blocks: List of geometric blocks with x, y, w, h keys
        
    Returns:
        List of typed blocks with added 'type' key
    """
    if not blocks:
        logger.debug("No blocks to classify")
        return []
    
    try:
        # Extract block images
        block_images = extract_block_images(image_bgr, blocks)
        logger.debug(f"Extracted {len(block_images)} block images")
        
        # Classify using the model
        if model is None:
            logger.warning("No model available, using fallback classification")
            model = StubClassifier()
        
        predictions = model.predict(block_images)
        logger.debug(f"Generated {len(predictions)} predictions")
        
        # Combine blocks with predictions
        typed_blocks = []
        for block, prediction in zip(blocks, predictions):
            typed_block = block.copy()
            typed_block['type'] = prediction
            typed_blocks.append(typed_block)
        
        # Log classification summary
        type_counts = {}
        for block in typed_blocks:
            block_type = block['type']
            type_counts[block_type] = type_counts.get(block_type, 0) + 1
        
        logger.info(f"Classification summary: {type_counts}")
        
        return typed_blocks
        
    except Exception as e:
        logger.error(f"Classification failed: {e}")
        # Return blocks with fallback type
        return [
            {**block, 'type': FALLBACK_ELEMENT_TYPE}
            for block in blocks
        ]

def validate_model_file(model_path: Path) -> Tuple[bool, str]:
    """
    Validate that a model file is accessible and appears valid.
    
    Args:
        model_path: Path to the model file
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not model_path.exists():
        return False, f"Model file not found: {model_path}"
    
    if not model_path.is_file() and not model_path.is_dir():
        return False, f"Model path is neither file nor directory: {model_path}"
    
    try:
        # Check if file is readable
        with open(model_path, 'rb') as f:
            f.read(100)  # Read first 100 bytes
        return True, "Model file appears valid"
    except PermissionError:
        return False, f"Permission denied reading model file: {model_path}"
    except Exception as e:
        return False, f"Error accessing model file: {e}"