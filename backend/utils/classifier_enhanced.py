"""
CNN-based UI element classifier - PRODUCTION READY INTERFACE.

This module provides a pluggable CNN interface with:
  - Clean BlockClassifierCNN class structure
  - preprocess_crop() helper for model input
  - Smart geometry-based fallback heuristics
  - Clear TODO markers for your model integration

PLUGGABLE DESIGN: You can replace the CNN implementation by:
  1. Implementing BlockClassifierCNN.forward()
  2. Loading weights in load_model()
  3. Ensuring preprocess_crop() matches your input requirements
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import cv2
from pathlib import Path

from config import Config

logger = logging.getLogger(__name__)

# ============================================================================
# CONSTANTS
# ============================================================================

# Expected input size for CNN (TODO: adjust to match your trained model)
CNN_INPUT_SIZE = 128  # 128x128 pixels

# UI element types (TODO: must match your training label order)
UI_ELEMENT_TYPES = [
    "button",
    "text_input",
    "text",
    "heading",
    "image",
    "card",
    "checkbox",
    "radio",
    "dropdown",
    "link",
    "label",
    "unknown"
]

FALLBACK_TYPE = "unknown"

# Optional imports
try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    TORCH_AVAILABLE = True
except ImportError:
    logger.warning("PyTorch not available - using stub classifier only")
    TORCH_AVAILABLE = False
    torch = None
    nn = None


# ============================================================================
# CNN MODEL CLASS (PLUGGABLE)
# ============================================================================

if TORCH_AVAILABLE:
    class BlockClassifierCNN(nn.Module):
        """
        Convolutional Neural Network for UI block classification.
        
        TODO: Replace this architecture with your trained model!
        
        This is a simple CNN template. When you have a trained model:
          1. Copy its architecture here OR
          2. Load it directly as a torchscript model OR
          3. Use your own custom nn.Module class
        
        Expected input: [batch, 3, CNN_INPUT_SIZE, CNN_INPUT_SIZE]
        Expected output: [batch, num_classes] logits
        """
        
        def __init__(self, num_classes: int = len(UI_ELEMENT_TYPES)):
            super(BlockClassifierCNN, self).__init__()
            
            # TODO: Define your CNN architecture here
            # Example simple architecture (replace with your own):
            
            self.conv1 = nn.Conv2d(3, 32, kernel_size=3, padding=1)
            self.bn1 = nn.BatchNorm2d(32)
            self.pool1 = nn.MaxPool2d(2, 2)  # 128 -> 64
            
            self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
            self.bn2 = nn.BatchNorm2d(64)
            self.pool2 = nn.MaxPool2d(2, 2)  # 64 -> 32
            
            self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
            self.bn3 = nn.BatchNorm2d(128)
            self.pool3 = nn.MaxPool2d(2, 2)  # 32 -> 16
            
            self.conv4 = nn.Conv2d(128, 256, kernel_size=3, padding=1)
            self.bn4 = nn.BatchNorm2d(256)
            self.pool4 = nn.MaxPool2d(2, 2)  # 16 -> 8
            
            # Fully connected layers
            self.fc1 = nn.Linear(256 * 8 * 8, 512)
            self.dropout1 = nn.Dropout(0.5)
            self.fc2 = nn.Linear(512, 256)
            self.dropout2 = nn.Dropout(0.3)
            self.fc3 = nn.Linear(256, num_classes)
        
        def forward(self, x):
            """
            Forward pass through the network.
            
            Args:
                x: Input tensor [batch, 3, CNN_INPUT_SIZE, CNN_INPUT_SIZE]
                
            Returns:
                Logits tensor [batch, num_classes]
            """
            # TODO: Implement your forward pass
            # This is a simple example - replace with your architecture
            
            x = self.pool1(F.relu(self.bn1(self.conv1(x))))
            x = self.pool2(F.relu(self.bn2(self.conv2(x))))
            x = self.pool3(F.relu(self.bn3(self.conv3(x))))
            x = self.pool4(F.relu(self.bn4(self.conv4(x))))
            
            x = x.view(x.size(0), -1)  # Flatten
            
            x = F.relu(self.fc1(x))
            x = self.dropout1(x)
            x = F.relu(self.fc2(x))
            x = self.dropout2(x)
            x = self.fc3(x)
            
            return x
else:
    # Dummy class when PyTorch not available
    class BlockClassifierCNN:
        def __init__(self, *args, **kwargs):
            raise ImportError("PyTorch not available")


# ============================================================================
# PREPROCESSING
# ============================================================================

def preprocess_crop(image_bgr: np.ndarray, rect: Dict[str, int]) -> np.ndarray:
    """
    Preprocess a cropped block for CNN input.
    
    TODO: Adjust this function to match your model's input requirements!
    
    Args:
        image_bgr: Full image in BGR format
        rect: Block rectangle {x, y, w, h}
        
    Returns:
        Preprocessed tensor ready for CNN [3, CNN_INPUT_SIZE, CNN_INPUT_SIZE]
        (CHW format, values in [0, 1], normalized)
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
    
    # Resize to expected input size
    resized = cv2.resize(crop, (CNN_INPUT_SIZE, CNN_INPUT_SIZE), 
                        interpolation=cv2.INTER_LINEAR)
    
    # Convert BGR to RGB
    rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
    
    # Convert to float and normalize to [0, 1]
    normalized = rgb.astype(np.float32) / 255.0
    
    # TODO: Apply additional normalization if your model expects it
    # Example: ImageNet normalization
    # mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
    # std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
    # normalized = (normalized - mean) / std
    
    # Convert to CHW format (channels first)
    chw = np.transpose(normalized, (2, 0, 1))
    
    return chw


# ============================================================================
# SMART GEOMETRY-BASED STUB (FALLBACK)
# ============================================================================

class SmartGeometryClassifier:
    """
    Improved heuristic classifier using geometry + basic image features.
    
    Used when CNN model is not available or as fallback.
    """
    
    def classify_block(self, image_bgr: np.ndarray, rect: Dict[str, int]) -> Tuple[str, float]:
        """
        Classify a single block using heuristics.
        
        Args:
            image_bgr: Full image
            rect: Block rectangle
            
        Returns:
            (predicted_type, confidence)
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
            return FALLBACK_TYPE, 0.1
        
        # Geometric features
        aspect_ratio = w / h if h > 0 else 1.0
        area = w * h
        perimeter = 2 * (w + h)
        
        # Image features
        gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        mean_intensity = np.mean(gray)
        std_intensity = np.std(gray)
        
        # Edge density (complexity)
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / (w * h) if (w * h) > 0 else 0
        
        # Color variance
        color_std = np.std(crop)
        
        # Classification rules (heuristic decision tree)
        
        # Button: compact, moderate aspect ratio, often solid color
        if (1.5 < aspect_ratio < 5.0 and 
            15 < h < 60 and 
            color_std < 50 and 
            area < 15000):
            return "button", 0.7
        
        # Text input: wide, low height, rectangular
        if (aspect_ratio > 3.0 and 
            10 < h < 50 and 
            edge_density < 0.1):
            return "text_input", 0.75
        
        # Heading: moderate width, small height, text-like
        if (h < 40 and 
            w > 100 and 
            aspect_ratio > 2.0 and 
            edge_density > 0.05):
            return "heading", 0.6
        
        # Text: similar to heading but smaller or different aspect
        if (h < 50 and 
            aspect_ratio > 1.2 and 
            edge_density > 0.03):
            return "text", 0.6
        
        # Image: large area, high variance
        if (area > 20000 and 
            color_std > 30):
            return "image", 0.65
        
        # Card: large, moderate aspect, structured
        if (area > 10000 and 
            0.7 < aspect_ratio < 2.0 and 
            edge_density > 0.05):
            return "card", 0.6
        
        # Checkbox/Radio: small, square-ish
        if (area < 1500 and 
            0.7 < aspect_ratio < 1.3):
            if color_std < 20:
                return "checkbox", 0.55
            else:
                return "radio", 0.5
        
        # Label: small text-like
        if (h < 25 and 
            w < 200 and 
            edge_density > 0.02):
            return "label", 0.5
        
        # Link: small, text-like, often underlined (high edge at bottom)
        if (h < 30 and 
            50 < w < 300 and 
            edge_density > 0.03):
            return "link", 0.5
        
        # Default fallback
        return FALLBACK_TYPE, 0.3
    
    def predict(self, image_bgr: np.ndarray, blocks: List[Dict[str, int]]) -> List[Dict[str, Any]]:
        """
        Predict types for all blocks.
        
        Args:
            image_bgr: Full image
            blocks: List of block rectangles
            
        Returns:
            List of predictions with type and confidence
        """
        predictions = []
        
        for block in blocks:
            pred_type, confidence = self.classify_block(image_bgr, block)
            predictions.append({
                "type": pred_type,
                "confidence": confidence
            })
        
        return predictions


# ============================================================================
# MODEL LOADING
# ============================================================================

def load_model() -> Optional[Any]:
    """
    Load the CNN classifier model.
    
    TODO: Configure model loading for your trained weights!
    
    Steps to integrate your model:
      1. Train your CNN and save as .pth or .pt file
      2. Set MODEL_PATH in config.py to point to your weights
      3. Ensure BlockClassifierCNN architecture matches your trained model
      4. Uncomment and adjust the loading code below
    
    Returns:
        Loaded model wrapper or SmartGeometryClassifier fallback
    """
    logger.info("Attempting to load CNN classifier...")
    
    if not TORCH_AVAILABLE:
        logger.warning("PyTorch not available - using geometry-based classifier")
        return SmartGeometryClassifier()
    
    # TODO: Configure your model path
    if not hasattr(Config, 'MODEL_PATH') or not Config.MODEL_PATH:
        logger.warning("MODEL_PATH not configured - using geometry-based classifier")
        return SmartGeometryClassifier()
    
    model_path = Path(Config.MODEL_PATH)
    
    if not model_path.exists():
        logger.warning(f"Model file not found: {model_path} - using geometry-based classifier")
        return SmartGeometryClassifier()
    
    try:
        # TODO: UNCOMMENT AND ADJUST THIS SECTION WHEN YOU HAVE A TRAINED MODEL
        
        # device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        # logger.info(f"Using device: {device}")
        
        # # Initialize model
        # model = BlockClassifierCNN(num_classes=len(UI_ELEMENT_TYPES))
        
        # # Load weights
        # checkpoint = torch.load(model_path, map_location=device)
        
        # # Handle different checkpoint formats
        # if isinstance(checkpoint, dict):
        #     if 'model_state_dict' in checkpoint:
        #         model.load_state_dict(checkpoint['model_state_dict'])
        #     elif 'state_dict' in checkpoint:
        #         model.load_state_dict(checkpoint['state_dict'])
        #     else:
        #         model.load_state_dict(checkpoint)
        # else:
        #     model.load_state_dict(checkpoint)
        
        # model.to(device)
        # model.eval()
        
        # logger.info("CNN model loaded successfully!")
        
        # # Wrap model in CNNClassifierWrapper
        # return CNNClassifierWrapper(model, device)
        
        # For now, return geometry classifier
        logger.warning("CNN loading code not implemented - using geometry-based classifier")
        return SmartGeometryClassifier()
        
    except Exception as e:
        logger.error(f"Failed to load CNN model: {e}")
        logger.warning("Falling back to geometry-based classifier")
        return SmartGeometryClassifier()


class CNNClassifierWrapper:
    """
    Wrapper for PyTorch CNN model to match interface.
    
    TODO: Use this when you have a trained model loaded.
    """
    
    def __init__(self, model, device):
        self.model = model
        self.device = device
    
    def predict(self, image_bgr: np.ndarray, blocks: List[Dict[str, int]]) -> List[Dict[str, Any]]:
        """
        Predict using CNN model.
        
        Args:
            image_bgr: Full image
            blocks: List of block rectangles
            
        Returns:
            List of predictions with type and confidence
        """
        if not TORCH_AVAILABLE:
            return SmartGeometryClassifier().predict(image_bgr, blocks)
        
        predictions = []
        
        try:
            with torch.no_grad():
                for block in blocks:
                    # Preprocess crop
                    input_tensor = preprocess_crop(image_bgr, block)
                    
                    # Add batch dimension and move to device
                    input_batch = torch.from_numpy(input_tensor).unsqueeze(0).to(self.device)
                    
                    # Forward pass
                    logits = self.model(input_batch)
                    
                    # Get probabilities
                    probs = F.softmax(logits, dim=1)
                    confidence, predicted_idx = torch.max(probs, 1)
                    
                    # Map to class name
                    idx = predicted_idx.item()
                    conf = confidence.item()
                    
                    if idx < len(UI_ELEMENT_TYPES):
                        pred_type = UI_ELEMENT_TYPES[idx]
                    else:
                        pred_type = FALLBACK_TYPE
                        conf = 0.1
                    
                    predictions.append({
                        "type": pred_type,
                        "confidence": conf
                    })
            
            return predictions
            
        except Exception as e:
            logger.error(f"CNN prediction failed: {e}")
            # Fallback to geometry classifier
            return SmartGeometryClassifier().predict(image_bgr, blocks)


# ============================================================================
# MAIN CLASSIFICATION INTERFACE
# ============================================================================

def classify_blocks(model: Optional[Any], 
                   image_bgr: np.ndarray, 
                   blocks: List[Dict[str, int]]) -> List[Dict[str, Any]]:
    """
    Classify detected blocks using loaded model.
    
    This is the main interface called by app.py.
    
    Args:
        model: Loaded classifier from load_model()
        image_bgr: Original image in BGR format
        blocks: List of block rectangles with x, y, w, h
        
    Returns:
        List of typed blocks with added 'type' and 'confidence' keys
    """
    if not blocks:
        logger.debug("No blocks to classify")
        return []
    
    try:
        # Use model if available, otherwise fallback
        if model is None:
            logger.warning("No model provided, using geometry classifier")
            model = SmartGeometryClassifier()
        
        # Get predictions
        predictions = model.predict(image_bgr, blocks)
        
        # Combine with block coordinates
        typed_blocks = []
        for block, pred in zip(blocks, predictions):
            typed_block = block.copy()
            typed_block['type'] = pred['type']
            typed_block['confidence'] = pred['confidence']
            typed_blocks.append(typed_block)
        
        # Log summary
        type_counts = {}
        for block in typed_blocks:
            t = block['type']
            type_counts[t] = type_counts.get(t, 0) + 1
        
        logger.info(f"Classification complete: {type_counts}")
        
        return typed_blocks
        
    except Exception as e:
        logger.error(f"Classification failed: {e}")
        # Return blocks with fallback type
        return [
            {**block, 'type': FALLBACK_TYPE, 'confidence': 0.1}
            for block in blocks
        ]


# ============================================================================
# CLI TEST UTILITY
# ============================================================================

if __name__ == "__main__":
    """
    Test classifier on a sample image.
    
    Usage:
        python classifier_enhanced.py <image_path>
    """
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python classifier_enhanced.py <image_path>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    image = cv2.imread(image_path)
    
    if image is None:
        print(f"Error: Could not load image from {image_path}")
        sys.exit(1)
    
    print(f"Loaded image: {image.shape}")
    
    # Create dummy blocks for testing
    h, w = image.shape[:2]
    test_blocks = [
        {"x": w//4, "y": h//4, "w": w//2, "h": 50},
        {"x": w//4, "y": h//2, "w": w//2, "h": 40},
        {"x": w//3, "y": 2*h//3, "w": w//4, "h": 35},
    ]
    
    # Load model and classify
    model = load_model()
    typed_blocks = classify_blocks(model, image, test_blocks)
    
    print("\nClassification Results:")
    print("="*60)
    for i, block in enumerate(typed_blocks):
        print(f"Block {i+1}: type={block['type']}, confidence={block['confidence']:.2f}")
        print(f"  Position: x={block['x']}, y={block['y']}, w={block['w']}, h={block['h']}")
