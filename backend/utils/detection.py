"""
OpenCV-based block detection for UI elements.

This module provides production-ready image processing to detect rectangular
UI components using OpenCV contour detection and filtering techniques.
"""

import logging
from typing import List, Dict, Tuple
import cv2
import numpy as np
from config import Config

logger = logging.getLogger(__name__)

def preprocess_image(image_bgr: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Preprocess the image for better contour detection.
    
    Args:
        image_bgr: Input image in BGR format
        
    Returns:
        Tuple of (gray image, binary image for contour detection)
    """
    # Convert to grayscale
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Apply adaptive thresholding for better edge detection
    binary = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
    )
    
    # Optional: Apply morphological operations to connect nearby components
    kernel = np.ones((3, 3), np.uint8)
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
    
    return gray, binary

def filter_contours(contours: List[np.ndarray], image_shape: Tuple[int, int]) -> List[np.ndarray]:
    """
    Filter contours based on area, aspect ratio, and other criteria.
    
    Args:
        contours: List of OpenCV contours
        image_shape: Shape of the original image (height, width)
        
    Returns:
        List of filtered contours
    """
    filtered = []
    image_area = image_shape[0] * image_shape[1]
    
    for contour in contours:
        area = cv2.contourArea(contour)
        
        # Filter by area (absolute and relative)
        if area < Config.DETECTION_MIN_AREA:
            continue
            
        if area > Config.DETECTION_MAX_AREA:
            continue
            
        # Don't allow contours that are too large relative to image
        if area > image_area * 0.8:
            continue
        
        # Get bounding rectangle
        x, y, w, h = cv2.boundingRect(contour)
        
        # Filter by aspect ratio
        aspect_ratio = w / h if h > 0 else 0
        if aspect_ratio < Config.DETECTION_MIN_ASPECT_RATIO or aspect_ratio > Config.DETECTION_MAX_ASPECT_RATIO:
            continue
            
        # Filter out very thin rectangles (likely noise)
        if w < 10 or h < 10:
            continue
            
        # Filter by solidity (how much the contour fills its convex hull)
        hull = cv2.convexHull(contour)
        hull_area = cv2.contourArea(hull)
        if hull_area > 0:
            solidity = area / hull_area
            if solidity < 0.3:  # Too irregular
                continue
        
        filtered.append(contour)
    
    return filtered

def merge_overlapping_blocks(blocks: List[Dict[str, int]], overlap_threshold: float = 0.3) -> List[Dict[str, int]]:
    """
    Merge blocks that overlap significantly.
    
    Args:
        blocks: List of block dictionaries with x, y, w, h keys
        overlap_threshold: Minimum IoU to consider blocks overlapping
        
    Returns:
        List of merged blocks
    """
    if not blocks:
        return blocks
        
    merged = []
    used = [False] * len(blocks)
    
    for i, block1 in enumerate(blocks):
        if used[i]:
            continue
            
        # Find all blocks that overlap with this one
        group = [block1]
        used[i] = True
        
        for j, block2 in enumerate(blocks[i+1:], i+1):
            if used[j]:
                continue
                
            # Calculate IoU (Intersection over Union)
            iou = calculate_iou(block1, block2)
            if iou > overlap_threshold:
                group.append(block2)
                used[j] = True
        
        # Merge the group into a single block
        if len(group) == 1:
            merged.append(group[0])
        else:
            merged_block = merge_block_group(group)
            merged.append(merged_block)
    
    return merged

def calculate_iou(block1: Dict[str, int], block2: Dict[str, int]) -> float:
    """Calculate Intersection over Union for two blocks."""
    x1_min, y1_min = block1['x'], block1['y']
    x1_max, y1_max = x1_min + block1['w'], y1_min + block1['h']
    
    x2_min, y2_min = block2['x'], block2['y']
    x2_max, y2_max = x2_min + block2['w'], y2_min + block2['h']
    
    # Calculate intersection
    int_x_min = max(x1_min, x2_min)
    int_y_min = max(y1_min, y2_min)
    int_x_max = min(x1_max, x2_max)
    int_y_max = min(y1_max, y2_max)
    
    if int_x_max <= int_x_min or int_y_max <= int_y_min:
        return 0.0
    
    intersection = (int_x_max - int_x_min) * (int_y_max - int_y_min)
    area1 = block1['w'] * block1['h']
    area2 = block2['w'] * block2['h']
    union = area1 + area2 - intersection
    
    return intersection / union if union > 0 else 0.0

def merge_block_group(blocks: List[Dict[str, int]]) -> Dict[str, int]:
    """Merge a group of blocks into a single encompassing block."""
    x_min = min(block['x'] for block in blocks)
    y_min = min(block['y'] for block in blocks)
    x_max = max(block['x'] + block['w'] for block in blocks)
    y_max = max(block['y'] + block['h'] for block in blocks)
    
    return {
        'x': x_min,
        'y': y_min,
        'w': x_max - x_min,
        'h': y_max - y_min
    }

def detect_blocks(image_bgr: np.ndarray) -> List[Dict[str, int]]:
    """
    Detect rectangular UI blocks in the image using OpenCV.
    
    This function implements a robust pipeline:
    1. Image preprocessing (blur, threshold)
    2. Contour detection
    3. Contour filtering (area, aspect ratio, solidity)
    4. Block merging for overlapping regions
    5. Sorting by position (top to bottom, left to right)
    
    Args:
        image_bgr: Input image in BGR color format (OpenCV standard)
        
    Returns:
        List of detected blocks, each with keys: x, y, w, h
        
    Raises:
        ValueError: If image is invalid or empty
    """
    if image_bgr is None or image_bgr.size == 0:
        raise ValueError("Invalid or empty image provided")
    
    logger.debug(f"Processing image of shape: {image_bgr.shape}")
    
    try:
        # Step 1: Preprocess image
        gray, binary = preprocess_image(image_bgr)
        
        # Step 2: Find contours
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        logger.debug(f"Found {len(contours)} raw contours")
        
        # Step 3: Filter contours
        filtered_contours = filter_contours(contours, image_bgr.shape[:2])
        logger.debug(f"After filtering: {len(filtered_contours)} contours")
        
        # Step 4: Convert contours to blocks
        blocks = []
        for contour in filtered_contours:
            x, y, w, h = cv2.boundingRect(contour)
            blocks.append({'x': x, 'y': y, 'w': w, 'h': h})
        
        # Step 5: Merge overlapping blocks
        merged_blocks = merge_overlapping_blocks(blocks)
        logger.debug(f"After merging: {len(merged_blocks)} blocks")
        
        # Step 6: Sort blocks by position (reading order: top to bottom, left to right)
        merged_blocks.sort(key=lambda block: (block['y'], block['x']))
        
        logger.info(f"Successfully detected {len(merged_blocks)} UI blocks")
        return merged_blocks
        
    except Exception as e:
        logger.error(f"Error in block detection: {e}")
        # Return empty list instead of crashing
        return []

def visualize_blocks(image_bgr: np.ndarray, blocks: List[Dict[str, int]]) -> np.ndarray:
    """
    Create a visualization of detected blocks on the original image.
    
    Args:
        image_bgr: Original image
        blocks: List of detected blocks
        
    Returns:
        Image with blocks drawn as rectangles
    """
    vis_image = image_bgr.copy()
    
    for i, block in enumerate(blocks):
        # Draw rectangle
        cv2.rectangle(
            vis_image,
            (block['x'], block['y']),
            (block['x'] + block['w'], block['y'] + block['h']),
            (0, 255, 0),  # Green color
            2
        )
        
        # Add block number
        cv2.putText(
            vis_image,
            str(i + 1),
            (block['x'] + 5, block['y'] + 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2
        )
    
    return vis_image
