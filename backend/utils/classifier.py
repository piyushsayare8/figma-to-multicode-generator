"""
Unified UI element classifier with CNN model support and fallback.

This module provides a clean API for UI element classification:
1. Loads trained CNN model (ui_classification_model.h5) if available
2. Falls back to geometric heuristics if model not found
3. Provides clear logging and diagnostics

Author: Figma to Multicode Generator Team
"""

import logging
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass
import numpy as np
import cv2
from pathlib import Path

logger = logging.getLogger(__name__)

# Try to import TensorFlow
try:
    import tensorflow as tf
    from tensorflow.keras.models import load_model as keras_load_model
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False
    tf = None


# ============================================================================
# CONFIGURATION
# ============================================================================

# TODO: Update these to match YOUR trained model's specifications
# Model input size (width, height) - default is 224x224 for most CNNs
MODEL_INPUT_SIZE = (224, 224)

# Class names mapping (index → class name)
# TODO: Update this list to match your model's training labels in exact order
CLASS_NAMES = [
    'background',       # Index 0
    'button',          # Index 1
    'card',            # Index 2
    'heading',         # Index 3
    'image_block',     # Index 4
    'input_field',     # Index 5
    'link',            # Index 6
    'password_input',  # Index 7
    'text_block'       # Index 8
]

# Confidence threshold for CNN predictions
CONFIDENCE_THRESHOLD = 0.3

# Fallback type for ambiguous predictions
FALLBACK_TYPE = "unknown"


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class Block:
    """Raw detected block (from detection.py)."""
    id: str
    x: int
    y: int
    w: int
    h: int


@dataclass
class TypedBlock:
    """Block with classification result."""
    id: str
    x: int
    y: int
    w: int
    h: int
    type: str           # Classified element type
    confidence: float   # Confidence score (0.0 to 1.0)
    source: str         # "cnn" or "fallback"


# ============================================================================
# MODEL LOADING
# ============================================================================

def load_model(config: Optional[Dict] = None) -> Optional[Any]:
    """
    Load the trained CNN model for UI classification.
    
    Args:
        config: Optional configuration dict with 'model_path' key
        
    Returns:
        Loaded Keras model or None if not available
        
    Examples:
        >>> model = load_model()
        >>> if model:
        >>>     print("CNN model loaded")
        >>> else:
        >>>     print("Using fallback classifier")
    """
    if not TF_AVAILABLE:
        logger.warning("TensorFlow not available - install with: pip install tensorflow>=2.13.0")
        logger.info("UI classifier model: FALLBACK mode (geometric heuristics)")
        return None
    
    # Determine model path
    model_path = None
    if config and 'model_path' in config:
        model_path = Path(config['model_path'])
    else:
        # Default: look in backend/models/ui_classification_model.h5
        backend_dir = Path(__file__).parent.parent
        model_path = backend_dir / "models" / "ui_classification_model.h5"
    
    # Try to load the model
    if not model_path.exists():
        logger.warning(f"Model file not found at: {model_path}")
        logger.info("UI classifier model: FALLBACK mode (geometric heuristics)")
        logger.info("To use CNN classifier, place your trained model at: backend/models/ui_classification_model.h5")
        return None
    
    try:
        logger.info(f"Loading trained CNN model from: {model_path}")
        model = keras_load_model(str(model_path), compile=False)
        
        # Verify model input shape
        expected_shape = (None, MODEL_INPUT_SIZE[0], MODEL_INPUT_SIZE[1], 3)
        actual_shape = model.input_shape
        
        if actual_shape != expected_shape:
            logger.warning(f"Model input shape mismatch: expected {expected_shape}, got {actual_shape}")
            logger.warning("Update MODEL_INPUT_SIZE in classifier.py to match your model")
        
        # Verify output shape
        num_classes = model.output_shape[-1]
        if num_classes != len(CLASS_NAMES):
            logger.warning(f"Model output classes ({num_classes}) != CLASS_NAMES length ({len(CLASS_NAMES)})")
            logger.warning("Update CLASS_NAMES in classifier.py to match your model's training labels")
        
        logger.info(f"✓ UI classifier model: LOADED successfully")
        logger.info(f"  Input shape: {actual_shape}")
        logger.info(f"  Output classes: {num_classes}")
        logger.info(f"  Class mapping: {CLASS_NAMES}")
        
        return model
        
    except Exception as e:
        logger.error(f"Failed to load model from {model_path}: {e}")
        logger.info("UI classifier model: FALLBACK mode (geometric heuristics)")
        return None


# ============================================================================
# PREPROCESSING
# ============================================================================

def preprocess_crop_for_cnn(crop_bgr: np.ndarray) -> np.ndarray:
    """
    Preprocess a cropped block image for CNN inference.
    
    Args:
        crop_bgr: Cropped block image in BGR format (any size)
        
    Returns:
        Preprocessed image ready for model.predict()
        Shape: (1, height, width, 3) normalized to [0, 1]
    """
    # Resize to model input size
    resized = cv2.resize(crop_bgr, MODEL_INPUT_SIZE, interpolation=cv2.INTER_AREA)
    
    # Convert BGR to RGB
    rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
    
    # Normalize to [0, 1] range
    normalized = rgb.astype(np.float32) / 255.0
    
    # Add batch dimension
    batched = np.expand_dims(normalized, axis=0)
    
    return batched


def preprocess_batch_for_cnn(crops_bgr: List[np.ndarray]) -> np.ndarray:
    """
    Preprocess multiple crops in batch for efficient inference.
    
    Args:
        crops_bgr: List of cropped images in BGR format
        
    Returns:
        Batched array ready for model.predict()
        Shape: (N, height, width, 3) normalized to [0, 1]
    """
    if not crops_bgr:
        return np.array([])
    
    preprocessed = [preprocess_crop_for_cnn(crop)[0] for crop in crops_bgr]
    return np.array(preprocessed)


# ============================================================================
# FALLBACK GEOMETRIC CLASSIFIER
# ============================================================================

def classify_by_geometry(block: Block, image_shape: Tuple[int, int]) -> Tuple[str, float]:
    """
    Fallback classifier using geometric heuristics.
    
    Args:
        block: Block to classify
        image_shape: (height, width) of original image
        
    Returns:
        Tuple of (type, confidence_score)
    """
    w, h = block.w, block.h
    aspect = w / h if h > 0 else 1.0
    area = w * h
    image_h, image_w = image_shape
    
    # Relative position
    center_y = block.y + h / 2
    relative_y = center_y / image_h if image_h > 0 else 0.5
    
    # Button detection: moderate size, wide aspect ratio
    if 50 < w < 300 and 20 < h < 80 and 1.5 < aspect < 8:
        return "button", 0.6
    
    # Input field: similar to button but slightly different dimensions
    if 100 < w < 600 and 20 < h < 60 and 2 < aspect < 15:
        return "input_field", 0.6
    
    # Heading: near top, wide, moderate height
    if relative_y < 0.3 and w > 100 and 30 < h < 100 and aspect > 2:
        return "heading", 0.5
    
    # Card: larger rectangular area, squarish to vertical
    if area > 10000 and 0.5 < aspect < 3:
        return "card", 0.5
    
    # Image block: large, squarish
    if area > 15000 and 0.7 < aspect < 1.5:
        return "image_block", 0.5
    
    # Text block: moderate size, wide
    if 100 < w < 800 and 15 < h < 200 and aspect > 2:
        return "text_block", 0.4
    
    # Link: small, wide
    if w < 200 and h < 40 and aspect > 1.5:
        return "link", 0.4
    
    # Default: unknown
    return "unknown", 0.3


# ============================================================================
# MAIN CLASSIFICATION FUNCTION
# ============================================================================

def classify_blocks(
    model: Optional[Any],
    image_bgr: np.ndarray,
    blocks: List[Block]
) -> List[TypedBlock]:
    """
    Classify a list of detected blocks using CNN or fallback.
    
    Args:
        model: Loaded Keras model or None for fallback
        image_bgr: Original image in BGR format
        blocks: List of detected blocks from detection.py
        
    Returns:
        List of TypedBlock with classification results
        
    Examples:
        >>> model = load_model()
        >>> typed_blocks = classify_blocks(model, image, blocks)
        >>> for block in typed_blocks:
        >>>     print(f"{block.type} (confidence: {block.confidence:.2f})")
    """
    if not blocks:
        logger.debug("No blocks to classify")
        return []
    
    typed_blocks = []
    image_shape = image_bgr.shape[:2]
    
    # ========================================================================
    # CNN CLASSIFICATION PATH
    # ========================================================================
    if model is not None:
        logger.debug(f"Classifying {len(blocks)} blocks using CNN model")
        
        # Extract crops
        crops = []
        valid_blocks = []
        
        for block in blocks:
            x, y, w, h = block.x, block.y, block.w, block.h
            
            # Ensure coordinates are within image bounds
            x = max(0, min(x, image_bgr.shape[1] - 1))
            y = max(0, min(y, image_bgr.shape[0] - 1))
            x2 = max(x + 1, min(x + w, image_bgr.shape[1]))
            y2 = max(y + 1, min(y + h, image_bgr.shape[0]))
            
            if x2 > x and y2 > y:
                crop = image_bgr[y:y2, x:x2]
                if crop.size > 0:
                    crops.append(crop)
                    valid_blocks.append(block)
        
        if not crops:
            logger.warning("No valid crops extracted from blocks")
            return []
        
        # Batch preprocess
        batch = preprocess_batch_for_cnn(crops)
        
        # Run inference
        try:
            predictions = model.predict(batch, verbose=0)
            
            # Process predictions
            for block, pred in zip(valid_blocks, predictions):
                class_idx = int(np.argmax(pred))
                confidence = float(pred[class_idx])
                
                # Use CNN prediction if confidence is high enough
                if confidence >= CONFIDENCE_THRESHOLD and 0 <= class_idx < len(CLASS_NAMES):
                    pred_type = CLASS_NAMES[class_idx]
                    source = "cnn"
                else:
                    # Fallback to geometric if confidence too low
                    pred_type, confidence = classify_by_geometry(block, image_shape)
                    source = "fallback"
                
                typed_blocks.append(TypedBlock(
                    id=block.id,
                    x=block.x,
                    y=block.y,
                    w=block.w,
                    h=block.h,
                    type=pred_type,
                    confidence=confidence,
                    source=source
                ))
            
            cnn_count = sum(1 for b in typed_blocks if b.source == "cnn")
            fallback_count = len(typed_blocks) - cnn_count
            logger.debug(f"Classified: {cnn_count} by CNN, {fallback_count} by fallback")
            
        except Exception as e:
            logger.error(f"CNN inference failed: {e}")
            logger.info("Falling back to geometric classifier for all blocks")
            # Fall through to fallback path
            model = None
    
    # ========================================================================
    # FALLBACK CLASSIFICATION PATH
    # ========================================================================
    if model is None:
        logger.debug(f"Classifying {len(blocks)} blocks using geometric heuristics")
        
        for block in blocks:
            pred_type, confidence = classify_by_geometry(block, image_shape)
            
            typed_blocks.append(TypedBlock(
                id=block.id,
                x=block.x,
                y=block.y,
                w=block.w,
                h=block.h,
                type=pred_type,
                confidence=confidence,
                source="fallback"
            ))
    
    return typed_blocks


# ============================================================================
# DIAGNOSTICS
# ============================================================================

def get_classifier_status(model: Optional[Any]) -> Dict[str, Any]:
    """
    Get diagnostic information about the classifier state.
    
    Args:
        model: Loaded model or None
        
    Returns:
        Dictionary with status information
    """
    return {
        "tensorflow_available": TF_AVAILABLE,
        "model_loaded": model is not None,
        "mode": "cnn" if model is not None else "fallback",
        "model_input_size": MODEL_INPUT_SIZE,
        "num_classes": len(CLASS_NAMES),
        "class_names": CLASS_NAMES,
        "confidence_threshold": CONFIDENCE_THRESHOLD
    }
