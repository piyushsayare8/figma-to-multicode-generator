"""
Configuration module for the Figma to Multicode Generator.
Manages environment-based settings and constants.
"""

import os
from typing import List, Optional
from pathlib import Path

class Config:
    """Production-style configuration management."""
    
    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    WORKERS: int = int(os.getenv("WORKERS", "1"))
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # CORS Configuration
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]
    
    # Additional origins from environment
    if os.getenv("ADDITIONAL_ORIGINS"):
        ALLOWED_ORIGINS.extend(os.getenv("ADDITIONAL_ORIGINS").split(","))
    
    # File Upload Configuration
    MAX_IMAGE_SIZE_MB: int = int(os.getenv("MAX_IMAGE_SIZE_MB", "10"))
    MAX_IMAGE_SIZE_BYTES: int = MAX_IMAGE_SIZE_MB * 1024 * 1024
    
    ALLOWED_IMAGE_EXTENSIONS: List[str] = [
        ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"
    ]
    
    ALLOWED_MIME_TYPES: List[str] = [
        "image/jpeg", "image/png", "image/gif", "image/bmp", 
        "image/tiff", "image/webp"
    ]
    
    # Model Configuration
    MODEL_PATH: Optional[Path] = None
    if os.getenv("MODEL_PATH"):
        MODEL_PATH = Path(os.getenv("MODEL_PATH"))
    else:
        MODEL_PATH = Path(__file__).parent / "models" / "block_cnn_v1.pth"
    
    # Detection Parameters
    DETECTION_MIN_AREA: int = int(os.getenv("DETECTION_MIN_AREA", "50"))  # Lowered for small UI elements
    DETECTION_MAX_AREA: int = int(os.getenv("DETECTION_MAX_AREA", "100000"))  # Increased for large sections
    DETECTION_MIN_ASPECT_RATIO: float = float(os.getenv("DETECTION_MIN_ASPECT_RATIO", "0.1"))  # Wider range
    DETECTION_MAX_ASPECT_RATIO: float = float(os.getenv("DETECTION_MAX_ASPECT_RATIO", "15.0"))  # Wider range
    
    # Style Analysis Configuration (NEW)
    ENABLE_STYLE_ANALYSIS: bool = os.getenv("ENABLE_STYLE_ANALYSIS", "true").lower() == "true"
    STYLE_KMEANS_CLUSTERS: int = int(os.getenv("STYLE_KMEANS_CLUSTERS", "5"))
    STYLE_MIN_COLOR_PROMINENCE: float = float(os.getenv("STYLE_MIN_COLOR_PROMINENCE", "0.05"))
    
    # Spacing scales (NEW)
    SPACING_SMALL: int = 8
    SPACING_MEDIUM: int = 16
    SPACING_LARGE: int = 24
    
    # Processing Configuration
    IMAGE_PROCESSING_TIMEOUT: int = int(os.getenv("IMAGE_PROCESSING_TIMEOUT", "30"))
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # API Documentation
    API_TITLE: str = "Figma to Multicode Generator API"
    API_DESCRIPTION: str = """
    A production-ready API that converts UI screenshots into multiple code formats.
    
    Features:
    - OpenCV-based block detection
    - CNN-powered UI element classification
    - Style-aware analysis (colors, spacing, typography)
    - Multi-framework code generation (HTML+Tailwind, React, Flutter, etc.)
    """
    API_VERSION: str = "2.0.0"
    
    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production environment."""
        return cls.ENVIRONMENT.lower() == "production"
    
    @classmethod
    def is_development(cls) -> bool:
        """Check if running in development environment."""
        return cls.ENVIRONMENT.lower() == "development"

# Base paths (backward compatibility)
BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "models"

# UI Element Types
UI_ELEMENT_TYPES = [
    "background",
    "button", 
    "input_field",
    "password_input",
    "text_block",
    "image_block",
    "card",
    "link",
    "checkbox",
    "radio_button",
    "select_dropdown", 
    "textarea",
    "label",
    "header",
    "footer",
    "navigation",
    "unknown"
]

# Model configuration (backward compatibility)
MODEL_PATH = Config.MODEL_PATH
CLASS_LABELS = UI_ELEMENT_TYPES

# Upload / safety limits (backward compatibility)
MAX_IMAGE_SIZE_MB = Config.MAX_IMAGE_SIZE_MB
MAX_IMAGE_SIZE_BYTES = Config.MAX_IMAGE_SIZE_BYTES
ALLOWED_EXTENSIONS = set(Config.ALLOWED_IMAGE_EXTENSIONS)
BACKEND_CORS_ORIGINS = Config.ALLOWED_ORIGINS

# ILS Schema constants
ILS_VERSION = "1.0"
DEFAULT_PAGE_TITLE = "Generated UI"
FALLBACK_ELEMENT_TYPE = "unknown"
