"""
Image Loading Utilities
=======================
Utilities for loading and converting image files for OCR processing.

This module handles:
- FastAPI UploadFile to OpenCV image conversion
- Image format validation and error handling
- Memory-efficient image loading
- Support for multiple image formats (JPEG, PNG, etc.)

Supported Formats:
- JPEG (.jpg, .jpeg)
- PNG (.png)
- BMP (.bmp)  
- TIFF (.tiff, .tif)
- WebP (.webp)

Image Processing:
- Automatic format detection
- Color space conversion (maintains RGB/BGR for OCR)
- Memory-efficient buffer processing
- Error handling for corrupted images

Usage:
    from app.ocr.image_loader import load_image
    from fastapi import UploadFile
    
    @app.post("/upload")
    async def upload_receipt(file: UploadFile):
        cv2_image = await load_image(file)
        # Process with OCR...
"""

import numpy as np
import cv2
from fastapi import UploadFile, HTTPException

async def load_image(file: UploadFile):
    """
    Reads and decodes an uploaded image file into OpenCV format.
    """
    contents = await file.read()
    npimg = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    if img is None:
        raise HTTPException(status_code=400, detail="Image could not be read")
    return img
