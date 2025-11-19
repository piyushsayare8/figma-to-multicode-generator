"""
TensorFlow/Keras-based UI element classifier using trained model.

This module integrates the trained ui_classification_model.h5 for 
production use in the Figma to Multicode Generator project.
"""

import logging
from typing import Dict, List, Tuple, Optional, Any
import numpy as np
import cv2
from pathlib import Path

logger = logging.getLogger(__name__)

# Try to import TensorFlow
try:
    import tensorflow as tf
    from tensorflow.keras.models import load_model
    from tensorflow.keras.preprocessing import image as keras_image
    TF_AVAILABLE = True
    logger.info("TensorFlow is available for model inference")
except ImportError:
    TF_AVAILABLE = False
    logger.warning("TensorFlow not available - using fallback classifier")
    tf = None


# ============================================================================
# CONSTANTS
# ============================================================================

# Class names from your trained model (must match training order)
CLASS_NAMES = [
    'background', 
    'button', 
    'card', 
    'heading', 
    'image_block', 
    'input_field', 
    'link', 
    'password_input', 
    'text_block'
]

# Model expects 224x224 input
MODEL_INPUT_SIZE = 224

# Confidence threshold for predictions
CONFIDENCE_THRESHOLD = 0.5

# Fallback type for low confidence predictions
FALLBACK_TYPE = "unknown"


# ============================================================================
# UI CLASSIFIER CLASS
# ============================================================================

class TensorFlowUIClassifier:
    """
    TensorFlow/Keras-based UI element classifier.
    
    Loads and uses the trained ui_classification_model.h5 for inference.
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize the classifier with the trained model.
        
        Args:
            model_path: Path to the .h5 model file. If None, looks for default.
        """
        self.model = None
        self.model_loaded = False
        
        if not TF_AVAILABLE:
            logger.error("TensorFlow not available. Install with: pip install tensorflow")
            return
        
        # Determine model path
        if model_path is None:
            # Look for model in backend directory
            backend_dir = Path(__file__).parent.parent
            model_path = backend_dir / "models" / "ui_classification_model.h5"
            
            # Also check root directory
            if not model_path.exists():
                model_path = backend_dir.parent / "ui_classification_model.h5"
        else:
            model_path = Path(model_path)
        
        # Load the model
        try:
            if model_path.exists():
                logger.info(f"Loading trained model from: {model_path}")
                self.model = load_model(str(model_path))
                self.model_loaded = True
                logger.info(f"✓ Model loaded successfully from {model_path}")
            else:
                logger.warning(f"Model file not found at: {model_path}")
                logger.warning("Will use fallback geometric classifier")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            logger.warning("Will use fallback geometric classifier")
    
    def preprocess_crop(self, image_bgr: np.ndarray, rect: Dict[str, int]) -> np.ndarray:
        """
        Preprocess a cropped block for model input.
        
        Args:
            image_bgr: Full image in BGR format
            rect: Block rectangle {x, y, w, h}
            
        Returns:
            Preprocessed array ready for model [1, 224, 224, 3]
        """
        x, y, w, h = rect['x'], rect['y'], rect['w'], rect['h']
        
        # Ensure coordinates are within bounds
        img_h, img_w = image_bgr.shape[:2]
        x = max(0, min(x, img_w - 1))
        y = max(0, min(y, img_h - 1))
        w = max(1, min(w, img_w - x))
        h = max(1, min(h, img_h - y))
        
        # Extract crop
        crop = image_bgr[y:y+h, x:x+w]
        
        if crop.size == 0:
            # Create blank image if crop failed
            crop = np.zeros((10, 10, 3), dtype=np.uint8)
        
        # Resize to model input size (224x224)
        resized = cv2.resize(crop, (MODEL_INPUT_SIZE, MODEL_INPUT_SIZE), 
                            interpolation=cv2.INTER_LINEAR)
        
        # Convert BGR to RGB
        rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        
        # Convert to float and normalize to [0, 1]
        normalized = rgb.astype(np.float32) / 255.0
        
        # Add batch dimension
        batch = np.expand_dims(normalized, axis=0)
        
        return batch
    
    def predict(self, image_bgr: np.ndarray, rect: Dict[str, int]) -> Tuple[str, float, Dict[str, float]]:
        """
        Predict the UI element class for a given block.
        
        Args:
            image_bgr: Full image in BGR format
            rect: Block rectangle {x, y, w, h}
            
        Returns:
            Tuple of (predicted_class, confidence, all_probabilities)
        """
        if not self.model_loaded or self.model is None:
            # Use fallback geometric classifier
            return self._fallback_classify(image_bgr, rect)
        
        try:
            # Preprocess the crop
            img_array = self.preprocess_crop(image_bgr, rect)
            
            # Predict
            predictions = self.model.predict(img_array, verbose=0)
            
            # Get the class with highest probability
            class_idx = np.argmax(predictions[0])
            confidence = float(predictions[0][class_idx])
            predicted_class = CLASS_NAMES[class_idx]
            
            # Create probability dictionary
            probabilities = {CLASS_NAMES[i]: float(predictions[0][i]) 
                           for i in range(len(CLASS_NAMES))}
            
            # Map class names to UI element types
            predicted_class = self._map_to_ui_type(predicted_class)
            
            # Use fallback if confidence is too low
            if confidence < CONFIDENCE_THRESHOLD:
                logger.debug(f"Low confidence ({confidence:.2f}) for prediction, using fallback")
                return self._fallback_classify(image_bgr, rect)
            
            return predicted_class, confidence, probabilities
            
        except Exception as e:
            logger.error(f"Error during prediction: {e}")
            return self._fallback_classify(image_bgr, rect)
    
    def _map_to_ui_type(self, class_name: str) -> str:
        """
        Map trained model class names to UI element types.
        
        Args:
            class_name: Class name from model prediction
            
        Returns:
            Mapped UI element type
        """
        mapping = {
            'background': 'container',
            'button': 'button',
            'card': 'card',
            'heading': 'heading',
            'image_block': 'image',
            'input_field': 'text_input',
            'link': 'link',
            'password_input': 'text_input',
            'text_block': 'text'
        }
        return mapping.get(class_name, 'unknown')
    
    def _fallback_classify(self, image_bgr: np.ndarray, rect: Dict[str, int]) -> Tuple[str, float, Dict[str, float]]:
        """
        Fallback geometric-based classification.
        
        Args:
            image_bgr: Full image
            rect: Block rectangle
            
        Returns:
            Tuple of (predicted_type, confidence, probabilities)
        """
        x, y, w, h = rect['x'], rect['y'], rect['w'], rect['h']
        
        # Ensure valid bounds
        img_h, img_w = image_bgr.shape[:2]
        x = max(0, min(x, img_w - 1))
        y = max(0, min(y, img_h - 1))
        w = max(1, min(w, img_w - x))
        h = max(1, min(h, img_h - y))
        
        crop = image_bgr[y:y+h, x:x+w]
        
        if crop.size == 0:
            return FALLBACK_TYPE, 0.1, {}
        
        # Geometric features
        aspect_ratio = w / h if h > 0 else 1.0
        area = w * h
        
        # Simple heuristics
        predicted_type = FALLBACK_TYPE
        confidence = 0.3
        
        if aspect_ratio > 3.0:
            predicted_type = "text"
            confidence = 0.6
        elif aspect_ratio < 0.5:
            predicted_type = "image"
            confidence = 0.5
        elif 0.8 < aspect_ratio < 1.2 and area < 10000:
            predicted_type = "button"
            confidence = 0.5
        elif aspect_ratio > 1.5 and h < 50:
            predicted_type = "text_input"
            confidence = 0.5
        elif area > 50000:
            predicted_type = "container"
            confidence = 0.4
        else:
            predicted_type = "text"
            confidence = 0.4
        
        return predicted_type, confidence, {}


# ============================================================================
# BATCH CLASSIFICATION
# ============================================================================

def classify_blocks(image_bgr: np.ndarray, 
                   blocks: List[Dict[str, int]], 
                   classifier: Optional[TensorFlowUIClassifier] = None) -> List[Dict[str, Any]]:
    """
    Classify multiple UI blocks using the trained model.
    
    Args:
        image_bgr: Full image in BGR format
        blocks: List of block rectangles [{x, y, w, h}, ...]
        classifier: Optional pre-initialized classifier
        
    Returns:
        List of classified blocks with types and confidence scores
    """
    if classifier is None:
        classifier = TensorFlowUIClassifier()
    
    classified_blocks = []
    
    for block in blocks:
        predicted_type, confidence, probabilities = classifier.predict(image_bgr, block)
        
        classified_block = {
            'x': block['x'],
            'y': block['y'],
            'w': block['w'],
            'h': block['h'],
            'type': predicted_type,
            'confidence': confidence,
            'probabilities': probabilities
        }
        
        classified_blocks.append(classified_block)
        logger.debug(f"Block at ({block['x']},{block['y']}): {predicted_type} ({confidence:.2%})")
    
    return classified_blocks


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def load_model_instance(model_path: Optional[str] = None) -> TensorFlowUIClassifier:
    """
    Load and return a classifier instance.
    
    Args:
        model_path: Optional path to model file
        
    Returns:
        Initialized classifier
    """
    return TensorFlowUIClassifier(model_path)


# For backward compatibility
def load_model(model_path: Optional[str] = None) -> TensorFlowUIClassifier:
    """
    Load the trained model.
    
    Args:
        model_path: Path to the .h5 model file
        
    Returns:
        Initialized classifier instance
    """
    return load_model_instance(model_path)
