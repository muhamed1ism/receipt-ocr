"""
Application-wide constants
"""
import os

# OCR Configuration
OCR_DEFAULT_CONFIDENCE_THRESHOLD = 0.5
OCR_MIN_TEXT_LENGTH = 10
OCR_DEBUG_ENABLED = True

# Image Processing
IMAGE_MAX_WIDTH = 2048
IMAGE_MAX_HEIGHT = 2048
IMAGE_QUALITY_THRESHOLD = 50.0

# Debug Settings
DEBUG_IMAGE_DIR = "debug_images"
DEBUG_SAVE_INTERMEDIATE = True

# Debug File Saving Control
# Controls whether debug files (images + JSON) are saved to disk
# Production: Set to False (default) - logs only, no file saving
# Development: Set to True to save debug files for troubleshooting
# Usage: Set environment variable DEBUG_SAVE_FILES=True to enable
DEBUG_SAVE_FILES = os.environ.get("DEBUG_SAVE_FILES", "False").lower() in ("true", "1", "yes")

# Receipt Parsing
RECEIPT_MIN_ITEMS = 1
RECEIPT_MAX_ITEMS = 100
TOTAL_VALIDATION_TOLERANCE = 0.01

# File Extensions
SUPPORTED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']

# Logging
LOG_FORMAT = '[%(asctime)s] [%(levelname)-8s] %(name)s - %(message)s'
LOG_LEVEL_DEFAULT = 'INFO'

# Processing Timeouts (seconds)
OCR_TIMEOUT = 30
IMAGE_PROCESSING_TIMEOUT = 10
PARSING_TIMEOUT = 5
