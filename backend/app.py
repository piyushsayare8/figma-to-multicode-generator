"""
Main FastAPI Application - ILS v2 Architecture

This is the production entry point using the enhanced pipeline:
1. Detection (OpenCV)
2. Classification (CNN or fallback)
3. Style Analysis (colors, spacing, typography)
4. ILS v2 Building (tree-based, semantic sections)
5. Code Generation (Tailwind, HTML+CSS, React, Flutter)

Clean architecture following master prompt specifications.

Author: Figma to Multicode Generator Team
Version: 2.0
"""

import logging
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional
import io

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import cv2
import numpy as np
from PIL import Image

from config import Config

# Import our clean pipeline modules
from utils import classifier
from utils import detection
from utils import style_analyzer
from utils import ils_builder
from utils.generators import tailwind_gen

# Legacy generators (to be upgraded in future)
from utils import generator_html_css_enhanced
from utils import generator_react_enhanced
from utils import generator_flutter_enhanced

# Configure logging
logging.basicConfig(
    level=logging.INFO if Config.ENVIRONMENT == "production" else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# APPLICATION STATE
# ============================================================================

class AppState:
    """Global application state."""
    model: Optional[Any] = None
    model_loaded: bool = False


app_state = AppState()


# ============================================================================
# LIFESPAN MANAGEMENT
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Loads CNN model on startup, cleans up on shutdown.
    """
    logger.info("=" * 60)
    logger.info("FIGMA TO MULTICODE GENERATOR - Starting")
    logger.info("=" * 60)
    
    # Load CNN model
    try:
        app_state.model = classifier.load_model()
        app_state.model_loaded = app_state.model is not None
        
        if app_state.model_loaded:
            logger.info("✓ CNN model loaded successfully")
        else:
            logger.info("⚠ Running in fallback mode (geometric classifier)")
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        app_state.model = None
        app_state.model_loaded = False
    
    # Get classifier status
    status = classifier.get_classifier_status(app_state.model)
    logger.info(f"Classifier mode: {status['mode']}")
    logger.info(f"TensorFlow available: {status['tensorflow_available']}")
    
    logger.info("Application ready!")
    logger.info("=" * 60)
    
    yield  # Application runs
    
    # Cleanup
    logger.info("Shutting down...")


# ============================================================================
# FASTAPI APP
# ============================================================================

app = FastAPI(
    title="Figma to Multicode Generator",
    description="Convert UI screenshots to multi-framework code using CNN + ILS v2",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def decode_image(upload_file: UploadFile) -> np.ndarray:
    """
    Decode uploaded image to OpenCV BGR format.
    
    Args:
        upload_file: FastAPI UploadFile object
        
    Returns:
        NumPy array in BGR format
        
    Raises:
        HTTPException: If image cannot be decoded
    """
    try:
        # Read file contents
        contents = upload_file.file.read()
        
        # Decode with PIL
        pil_image = Image.open(io.BytesIO(contents))
        
        # Convert to RGB if needed
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        
        # Convert to NumPy array
        rgb_array = np.array(pil_image)
        
        # Convert RGB to BGR (OpenCV format)
        bgr_array = cv2.cvtColor(rgb_array, cv2.COLOR_RGB2BGR)
        
        logger.debug(f"Decoded image: {bgr_array.shape}")
        return bgr_array
        
    except Exception as e:
        logger.error(f"Image decode error: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/health")
async def health_check():
    """
    Health check endpoint with system status.
    
    Returns:
        System health information including model status
    """
    status = classifier.get_classifier_status(app_state.model)
    
    return {
        "status": "ok",
        "version": "2.0.0",
        "model_loaded": app_state.model_loaded,
        "classifier_mode": status["mode"],
        "tensorflow_available": status["tensorflow_available"],
        "architecture": "ILS_v2"
    }


@app.post("/analyze")
async def analyze_ui(
    file: UploadFile = File(...),
    include_debug: bool = False
) -> JSONResponse:
    """
    Main analysis endpoint - complete pipeline.
    
    Pipeline stages:
    1. Image decoding
    2. Block detection (OpenCV)
    3. Block classification (CNN or fallback)
    4. Style analysis (colors, spacing, typography)
    5. ILS v2 building (tree structure, semantic sections)
    6. Code generation (multiple frameworks)
    
    Args:
        file: Uploaded image file
        include_debug: If True, include debug information
        
    Returns:
        JSON response with layout, ILS, and generated code
    """
    logger.info(f"Analyzing UI from: {file.filename}")
    
    try:
        # ====================================================================
        # STAGE 1: IMAGE DECODING
        # ====================================================================
        image_bgr = decode_image(file)
        logger.info(f"✓ Image decoded: {image_bgr.shape}")
        
        # ====================================================================
        # STAGE 2: BLOCK DETECTION
        # ====================================================================
        raw_blocks = detection.detect_blocks(image_bgr)
        logger.info(f"✓ Detected {len(raw_blocks)} blocks")
        
        if not raw_blocks:
            raise HTTPException(
                status_code=422,
                detail="No UI elements detected in image. Try a clearer screenshot."
            )
        
        # ====================================================================
        # STAGE 3: BLOCK CLASSIFICATION
        # ====================================================================
        # Convert raw blocks to classifier.Block format
        classifier_blocks = [
            classifier.Block(
                id=f"block_{i}",
                x=b["x"],
                y=b["y"],
                w=b["w"],
                h=b["h"]
            )
            for i, b in enumerate(raw_blocks)
        ]
        
        typed_blocks = classifier.classify_blocks(
            model=app_state.model,
            image_bgr=image_bgr,
            blocks=classifier_blocks
        )
        
        cnn_count = sum(1 for b in typed_blocks if b.source == "cnn")
        fallback_count = len(typed_blocks) - cnn_count
        logger.info(f"✓ Classified {len(typed_blocks)} blocks ({cnn_count} CNN, {fallback_count} fallback)")
        
        # ====================================================================
        # STAGE 4: STYLE ANALYSIS
        # ====================================================================
        style_info = style_analyzer.analyze_style(image_bgr, typed_blocks)
        logger.info(f"✓ Style analysis complete")
        logger.debug(f"  Page colors: bg={style_info['page']['background_color']}, "
                    f"primary={style_info['page']['primary_color']}")
        
        # ====================================================================
        # STAGE 5: ILS v2 BUILDING
        # ====================================================================
        ils = ils_builder.build_ils(typed_blocks, style_info)
        logger.info(f"✓ Built ILS tree with {len(ils.get('children', []))} sections")
        
        # ====================================================================
        # STAGE 6: CODE GENERATION
        # ====================================================================
        
        # New ILS v2 generator (Tailwind)
        tailwind_code = tailwind_gen.generate_tailwind_code(ils)
        
        # Legacy generators (will be upgraded)
        # For now, convert ILS v2 to old format for compatibility
        legacy_layout = convert_ils_to_legacy(typed_blocks)
        legacy_ils = {"sections": [{"type": "content", "elements": []}]}
        
        html_css_code = generator_html_css_enhanced.generate_html_css(
            legacy_layout, legacy_ils, style_info
        )
        
        react_code = generator_react_enhanced.generate_react(
            legacy_layout, legacy_ils, style_info
        )
        
        flutter_code = generator_flutter_enhanced.generate_flutter(
            legacy_layout, legacy_ils, style_info
        )
        
        logger.info("✓ All code generated")
        
        # ====================================================================
        # BUILD RESPONSE
        # ====================================================================
        
        response_data = {
            "success": True,
            "stats": {
                "blocks_detected": len(raw_blocks),
                "blocks_classified": len(typed_blocks),
                "cnn_classifications": cnn_count,
                "fallback_classifications": fallback_count,
                "sections_detected": len(ils.get("children", []))
            },
            "layout": legacy_layout,  # For backward compatibility
            "ils": ils,  # New ILS v2 tree
            "style": style_info,
            "outputs": {
                "html_tailwind": tailwind_code,
                "html_plain": html_css_code.get("html", ""),
                "css": html_css_code.get("css", ""),
                "react": react_code,
                "dart": flutter_code
            }
        }
        
        # Add debug info if requested
        if include_debug:
            response_data["debug"] = {
                "model_loaded": app_state.model_loaded,
                "classifier_mode": "cnn" if app_state.model_loaded else "fallback",
                "typed_blocks": [
                    {
                        "id": b.id,
                        "type": b.type,
                        "confidence": b.confidence,
                        "source": b.source,
                        "rect": {"x": b.x, "y": b.y, "w": b.w, "h": b.h}
                    }
                    for b in typed_blocks
                ]
            }
        
        logger.info("=" * 60)
        logger.info("Analysis complete!")
        logger.info("=" * 60)
        
        return JSONResponse(content=response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


def convert_ils_to_legacy(typed_blocks: list) -> list:
    """Convert TypedBlock list to legacy layout format."""
    return [
        {
            "id": b.id,
            "x": b.x,
            "y": b.y,
            "w": b.w,
            "h": b.h,
            "type": b.type,
            "confidence": b.confidence
        }
        for b in typed_blocks
    ]


# ============================================================================
# MAIN ENTRY
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app:app",
        host=Config.HOST,
        port=Config.PORT,
        reload=Config.ENVIRONMENT == "development",
        log_level="info"
    )
