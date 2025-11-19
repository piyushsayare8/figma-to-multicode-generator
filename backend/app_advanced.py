"""
ADVANCED Figma to Multicode Generator - Pixel-Perfect UI Replication.

This version extracts:
1. Geometric shapes (OpenCV detection)
2. Element types (TensorFlow classification)
3. Visual styling (colors, borders, shadows, fonts)
4. Text content (OCR extraction)
5. Exact positioning and sizing

Result: Generated code that visually matches the original design.
"""

import logging
import traceback
from pathlib import Path
from typing import Dict, Any, Optional, List
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import numpy as np
from PIL import Image
import cv2
import io

from config import Config, UI_ELEMENT_TYPES
from utils.detection import detect_blocks
from utils.tf_classifier import load_model, classify_blocks
from utils.visual_style_extractor import VisualStyleExtractor
from utils.text_extractor import create_text_extractor
from utils.ils_builder import build_ils
from utils.style_analyzer import analyze_style

# Import advanced generators (we'll create these)
try:
    from utils.generator_pixel_perfect import (
        generate_pixel_perfect_html_css,
        generate_pixel_perfect_tailwind,
        generate_pixel_perfect_react,
        generate_pixel_perfect_flutter
    )
    PIXEL_PERFECT_AVAILABLE = True
except ImportError:
    # Fallback to enhanced generators
    from utils.generator_html_css_enhanced import generate_plain_html_and_css
    from utils.generator_tailwind_enhanced import generate_tailwind_html
    from utils.generator_react_enhanced import generate_react_component
    from utils.generator_flutter_enhanced import generate_flutter_code
    PIXEL_PERFECT_AVAILABLE = False
    logging.warning("Pixel-perfect generators not available, using enhanced versions")

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format=Config.LOG_FORMAT
)
logger = logging.getLogger(__name__)

# Global variables
_model: Optional[Any] = None
_text_extractor: Optional[Any] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    # Startup
    logger.info("Starting ADVANCED Figma to Multicode Generator API...")
    global _model, _text_extractor
    
    # Load TensorFlow model
    try:
        _model = load_model()
        logger.info("✓ Model loaded successfully")
    except Exception as e:
        logger.warning(f"Model loading failed: {e}. Using fallback classifier.")
    
    # Initialize text extractor
    try:
        _text_extractor = create_text_extractor()
        logger.info(f"✓ Text extractor initialized (method: {_text_extractor.ocr_method})")
    except Exception as e:
        logger.warning(f"Text extractor initialization failed: {e}")
        _text_extractor = None
    
    yield
    
    # Shutdown
    logger.info("Shutting down API...")


# Initialize FastAPI app
app = FastAPI(
    title="Advanced Figma to Multicode Generator",
    description="Pixel-perfect UI replication with visual style extraction and OCR",
    version="3.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models
class UIBlock(BaseModel):
    """Represents a detected UI block with visual styling."""
    x: int
    y: int
    w: int
    h: int
    type: str
    text: Optional[str] = None
    style: Optional[Dict[str, Any]] = None


class AnalysisResult(BaseModel):
    """Result of UI analysis with code generation."""
    layout: List[UIBlock]
    ils: Dict[str, Any]
    outputs: Dict[str, Any]


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    model_loaded: bool
    text_extraction: str
    pixel_perfect_mode: bool


@app.get("/", tags=["Info"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Advanced Figma to Multicode Generator API",
        "version": "3.0.0",
        "features": [
            "Geometric shape detection (OpenCV)",
            "Element classification (TensorFlow/CNN)",
            "Visual style extraction (colors, borders, shadows)",
            "Text content extraction (OCR)",
            "Pixel-perfect code generation",
            "Multi-framework support (HTML/CSS, Tailwind, React, Flutter)"
        ],
        "endpoints": {
            "/analyze": "POST - Analyze UI screenshot and generate code",
            "/health": "GET - Health check",
            "/docs": "GET - Interactive API documentation"
        }
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        model_loaded=_model is not None and hasattr(_model, 'model_loaded') and _model.model_loaded,
        text_extraction=_text_extractor.ocr_method if _text_extractor else "none",
        pixel_perfect_mode=PIXEL_PERFECT_AVAILABLE
    )


@app.post("/analyze", response_model=AnalysisResult, tags=["Analysis"])
async def analyze_image(file: UploadFile = File(...)):
    """
    Analyze UI screenshot and generate pixel-perfect code.
    
    Process:
    1. Detect UI blocks (OpenCV)
    2. Classify elements (TensorFlow)
    3. Extract visual styling (colors, borders, shadows)
    4. Extract text content (OCR)
    5. Build enhanced ILS with all extracted data
    6. Generate pixel-perfect code for multiple frameworks
    """
    try:
        # Validate file
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be an image"
            )
        
        # Read image
        contents = await file.read()
        if len(contents) > Config.MAX_IMAGE_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Image too large. Maximum size: {Config.MAX_IMAGE_SIZE_MB}MB"
            )
        
        logger.info(f"Processing image: {file.filename} ({len(contents)} bytes)")
        
        # Convert to OpenCV format
        image_pil = Image.open(io.BytesIO(contents)).convert("RGB")
        image_np = np.array(image_pil)
        image_bgr = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
        
        logger.info(f"Image size: {image_bgr.shape}")
        
        # STEP 1: Detect geometric blocks
        logger.debug("Detecting UI blocks...")
        geometric_blocks = detect_blocks(image_bgr)
        logger.info(f"✓ Detected {len(geometric_blocks)} geometric blocks")
        
        # STEP 2: Classify blocks
        logger.debug("Classifying blocks...")
        typed_blocks = classify_blocks(image_bgr, geometric_blocks, _model)
        logger.info(f"✓ Classified {len(typed_blocks)} blocks")
        
        # STEP 3: Extract visual styling
        logger.debug("Extracting visual styles...")
        style_extractor = VisualStyleExtractor(image_bgr)
        for block in typed_blocks:
            block['visual_style'] = style_extractor.extract_block_style(block)
        logger.info(f"✓ Extracted visual styles for all blocks")
        
        # STEP 4: Extract text content (if OCR available)
        if _text_extractor and _text_extractor.ocr_method != "none":
            logger.debug("Extracting text with OCR...")
            text_map = _text_extractor.extract_all_text(image_bgr, typed_blocks)
            for idx, text in text_map.items():
                if idx < len(typed_blocks):
                    typed_blocks[idx]['extracted_text'] = text
            logger.info(f"✓ Extracted text from {len(text_map)} blocks")
        else:
            logger.debug("OCR not available, skipping text extraction")
        
        # STEP 5: Analyze page-level style
        logger.debug("Analyzing page-level style...")
        style_info = analyze_style(image_bgr, typed_blocks)
        
        # STEP 6: Build enhanced ILS
        logger.debug("Building enhanced ILS...")
        ils = build_ils(typed_blocks, style_info)
        
        # Add extracted data to ILS
        ils['image_dimensions'] = {
            'width': image_bgr.shape[1],
            'height': image_bgr.shape[0]
        }
        ils['pixel_perfect'] = True
        
        # STEP 7: Generate pixel-perfect code
        logger.debug("Generating pixel-perfect code...")
        
        if PIXEL_PERFECT_AVAILABLE:
            html_tailwind = generate_pixel_perfect_tailwind(ils, typed_blocks)
            html_plain, css = generate_pixel_perfect_html_css(ils, typed_blocks)
            react_code = generate_pixel_perfect_react(ils, typed_blocks)
            flutter_code = generate_pixel_perfect_flutter(ils, typed_blocks)
        else:
            # Fallback to enhanced generators
            html_tailwind = generate_tailwind_html(ils)
            html_plain, css = generate_plain_html_and_css(ils)
            react_code = generate_react_component(ils)
            flutter_code = generate_flutter_code(ils)
        
        # Prepare response
        ui_blocks = [
            UIBlock(
                x=block["x"],
                y=block["y"],
                w=block["w"],
                h=block["h"],
                type=block["type"],
                text=block.get("extracted_text"),
                style=block.get("visual_style")
            )
            for block in typed_blocks
        ]
        
        outputs = {
            "html_tailwind": html_tailwind,
            "html_plain": html_plain,
            "css": css,
            "react": react_code,
            "dart": flutter_code
        }
        
        logger.info("✓ Analysis completed successfully (pixel-perfect mode)")
        
        return AnalysisResult(
            layout=ui_blocks,
            ils=ils,
            outputs=outputs
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in analyze_image: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )


if __name__ == "__main__":
    uvicorn.run(
        "app_advanced:app",
        host=Config.HOST,
        port=Config.PORT,
        reload=Config.is_development(),
        workers=Config.WORKERS if Config.is_production() else 1
    )
