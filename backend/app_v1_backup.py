"""
Main FastAPI application for the Figma to Multicode Generator.

This module provides a production-ready API server that converts UI screenshots
into multiple code formats using a hybrid OpenCV + CNN pipeline.
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
from utils.classifier import load_model, classify_blocks
from utils.ils_builder import build_ils
from utils.generator_html_css_new import generate_html_css
from utils.generator_tailwind import generate_tailwind
from utils.generator_react import generate_react
from utils.generator_flutter import generate_flutter

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format=Config.LOG_FORMAT
)
logger = logging.getLogger(__name__)

# Global variable to store the loaded model
_model: Optional[Any] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    # Startup
    logger.info("Starting Figma to Multicode Generator API...")
    global _model
    
    try:
        _model = load_model()
        logger.info("Model loaded successfully")
    except Exception as e:
        logger.warning(f"Failed to load model: {e}")
        logger.warning("API will run with stub classifier")
        _model = None
    
    yield
    
    # Shutdown
    logger.info("Shutting down API...")

# Create FastAPI application
app = FastAPI(
    title=Config.API_TITLE,
    description=Config.API_DESCRIPTION,
    version=Config.API_VERSION,
    docs_url="/docs" if not Config.is_production() else None,
    redoc_url="/redoc" if not Config.is_production() else None,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Response Models
class UIBlock(BaseModel):
    """Represents a detected UI block with coordinates and type."""
    x: int = Field(..., description="X coordinate of the block")
    y: int = Field(..., description="Y coordinate of the block") 
    w: int = Field(..., description="Width of the block")
    h: int = Field(..., description="Height of the block")
    type: str = Field(..., description="Classified type of the UI element")

class AnalysisResult(BaseModel):
    """Complete analysis result containing layout, ILS, and generated outputs."""
    layout: List[UIBlock] = Field(..., description="Detected UI blocks with types")
    ils: Dict[str, Any] = Field(..., description="Intermediate Layout Schema")
    outputs: Dict[str, str] = Field(..., description="Generated code in multiple formats")

class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Service status")
    model_loaded: bool = Field(..., description="Whether ML model is loaded")
    version: str = Field(..., description="API version")

class ErrorResponse(BaseModel):
    """Standard error response."""
    detail: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Specific error code")

# Utility functions
def validate_image_file(file: UploadFile) -> None:
    """Validate uploaded image file."""
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided"
        )
    
    # Check file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in Config.ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(Config.ALLOWED_IMAGE_EXTENSIONS)}"
        )
    
    # Check content type if available
    if file.content_type and file.content_type not in Config.ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid content type: {file.content_type}"
        )

def load_and_process_image(file_content: bytes) -> np.ndarray:
    """Load and convert image to OpenCV format."""
    try:
        # Load with PIL first
        image = Image.open(io.BytesIO(file_content))
        
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Convert to numpy array
        image_rgb = np.array(image)
        
        # Convert RGB to BGR for OpenCV
        image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
        
        return image_bgr
        
    except Exception as e:
        logger.error(f"Image processing failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image format or corrupted file"
        )

# API Endpoints
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="ok",
        model_loaded=_model is not None,
        version=Config.API_VERSION
    )

@app.post("/analyze", response_model=AnalysisResult)
async def analyze_image(file: UploadFile = File(...)):
    """
    Analyze a UI screenshot and generate code in multiple formats.
    
    The pipeline:
    1. Validate and load the image
    2. Detect UI blocks using OpenCV
    3. Classify blocks using CNN (if available)
    4. Build Intermediate Layout Schema (ILS)
    5. Generate code in multiple formats
    """
    try:
        # Validate file
        validate_image_file(file)
        
        # Read file content
        file_content = await file.read()
        
        # Check file size
        if len(file_content) > Config.MAX_IMAGE_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Maximum size: {Config.MAX_IMAGE_SIZE_MB}MB"
            )
        
        # Load and process image
        logger.info(f"Processing image: {file.filename}")
        image_bgr = load_and_process_image(file_content)
        
        # Step 1: Detect blocks
        logger.debug("Detecting UI blocks...")
        geometric_blocks = detect_blocks(image_bgr)
        logger.info(f"Detected {len(geometric_blocks)} geometric blocks")
        
        # Step 2: Classify blocks
        logger.debug("Classifying blocks...")
        typed_blocks = classify_blocks(_model, image_bgr, geometric_blocks)
        logger.info(f"Classified {len(typed_blocks)} blocks")
        
        # Step 3: Build ILS
        logger.debug("Building ILS...")
        ils = build_ils(typed_blocks)
        
        # Step 4: Generate code
        logger.debug("Generating code outputs...")
        
        # Generate all output formats
        html_tailwind = generate_tailwind(ils)
        html_plain = generate_html_css(ils)
        react_code = generate_react(ils)
        flutter_code = generate_flutter(ils)
        
        # Prepare response
        ui_blocks = [
            UIBlock(x=block["x"], y=block["y"], w=block["w"], h=block["h"], type=block["type"])
            for block in typed_blocks
        ]
        
        outputs = {
            "html_tailwind": html_tailwind,
            "html_plain": html_plain,
            "react": react_code,
            "dart": flutter_code
        }
        
        logger.info("Analysis completed successfully")
        
        return AnalysisResult(
            layout=ui_blocks,
            ils=ils,
            outputs=outputs
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Log unexpected errors
        logger.error(f"Unexpected error in analyze_image: {e}")
        logger.error(traceback.format_exc())
        
        # Return generic error in production
        if Config.is_production():
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error occurred"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Internal error: {str(e)}"
            )

# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """Custom HTTP exception handler."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "error_code": getattr(exc, 'error_code', None)}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled exception: {exc}")
    logger.error(traceback.format_exc())
    
    if Config.is_production():
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error", "error_code": "INTERNAL_ERROR"}
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": str(exc), "error_code": "INTERNAL_ERROR"}
        )

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host=Config.HOST,
        port=Config.PORT,
        workers=Config.WORKERS,
        reload=Config.is_development(),
        log_level=Config.LOG_LEVEL.lower()
    )