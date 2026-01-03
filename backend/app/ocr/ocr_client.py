"""
OCR Client Service
==================
HTTP client for communicating with the OCR Processor microservice.

This module provides a clean interface for the API container to send images
to the OCR Processor container for text extraction. It handles:
- Image serialization and HTTP transmission
- Response parsing and validation
- Error handling and fallbacks
- Connection health monitoring

Architecture:
    API Container → OCR Client (this) → HTTP → OCR Processor Container

The OCR Processor runs PaddleOCR in a separate container to isolate
heavy ML dependencies from the lightweight API service.

Usage:
    from app.ocr.ocr_client import ocr_client

    # Process image (numpy array or file path)
    result = await ocr_client.process_image(image_array)

    # Check if OCR service is available
    is_healthy = await ocr_client.health_check()
"""

import httpx
import logging
import io
import numpy as np
from PIL import Image
from typing import Dict, Any, Union
from app.config import OCR_PROCESSOR_URL

logger = logging.getLogger(__name__)


class OCRClient:
    """
    Client for communicating with the OCR Processor microservice.

    This client handles all HTTP communication with the separate OCR processor
    container, allowing the API service to remain lightweight while delegating
    heavy OCR processing to a dedicated service.
    """

    def __init__(self, base_url: str = ""):
        """
        Initialize OCR client.

        Args:
            base_url: URL of OCR processor service (defaults to OCR_PROCESSOR_URL env var)
        """
        self.base_url = base_url or OCR_PROCESSOR_URL or "http://ocr-processor:8001"
        self.timeout = 120.0  # OCR can take time, especially on first request

        logger.info(f"[OCR CLIENT] Initialized with base URL: {self.base_url}")

    async def health_check(self) -> bool:
        """
        Check if OCR processor service is healthy and available.

        Returns:
            bool: True if service is healthy, False otherwise
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/health")

                if response.status_code == 200:
                    logger.debug("[OCR CLIENT] Health check passed")
                    return True
                else:
                    logger.warning(
                        f"[OCR CLIENT] Health check failed with status {response.status_code}"
                    )
                    return False

        except Exception as e:
            logger.error(f"[OCR CLIENT] Health check failed: {e}")
            return False

    async def process_image(
        self, image: Union[np.ndarray, str], filename: str = "receipt.jpg"
    ) -> Dict[str, Any]:
        """
        Send image to OCR processor for text extraction.

        Args:
            image: Image as numpy array (OpenCV format) or file path string
            filename: Original filename (for logging)

        Returns:
            dict: OCR result with structure:
                {
                    "success": bool,
                    "lines": List[str],
                    "confidence": float,
                    "processing_time_ms": float,
                    "line_count": int,
                    "error": str (if failed)
                }
        """
        try:
            logger.info(f"[OCR CLIENT] Sending image to OCR processor: {filename}")

            # Convert image to bytes for HTTP transmission
            image_bytes = self._image_to_bytes(image)

            # Prepare multipart file upload
            files = {"file": (filename, image_bytes, "image/jpeg")}

            # Send HTTP POST to OCR processor
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/extract-text", files=files
                )

                # Parse response
                if response.status_code == 200:
                    result = response.json()
                    logger.info(
                        f"[OCR CLIENT] OCR completed successfully - "
                        f"{result.get('line_count', 0)} lines extracted in "
                        f"{result.get('processing_time_ms', 0):.2f}ms"
                    )
                    return result
                else:
                    error_msg = f"OCR processor returned status {response.status_code}"
                    logger.error(f"[OCR CLIENT] {error_msg}")
                    return {
                        "success": False,
                        "error": error_msg,
                        "lines": [],
                        "confidence": 0.0,
                    }

        except httpx.TimeoutException:
            error_msg = "OCR processor request timed out"
            logger.error(f"[OCR CLIENT] {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "lines": [],
                "confidence": 0.0,
            }

        except Exception as e:
            error_msg = f"Failed to communicate with OCR processor: {str(e)}"
            logger.error(f"[OCR CLIENT] {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "lines": [],
                "confidence": 0.0,
            }

    def _image_to_bytes(self, image: Union[np.ndarray, str]) -> bytes:
        """
        Convert image to bytes for HTTP transmission.

        Args:
            image: Numpy array (OpenCV format) or file path

        Returns:
            bytes: JPEG-encoded image data
        """
        try:
            # If image is a file path, read it
            if isinstance(image, str):
                with open(image, "rb") as f:
                    return f.read()

            # If image is numpy array, convert to JPEG bytes
            elif isinstance(image, np.ndarray):
                # Convert BGR (OpenCV) to RGB (PIL)
                if len(image.shape) == 3 and image.shape[2] == 3:
                    # Assume BGR from OpenCV
                    image_rgb = image[:, :, ::-1]
                else:
                    image_rgb = image

                # Convert to PIL Image
                pil_image = Image.fromarray(image_rgb)

                # Encode as JPEG
                buffer = io.BytesIO()
                pil_image.save(buffer, format="JPEG", quality=95)
                return buffer.getvalue()

        except Exception as e:
            logger.error(f"[OCR CLIENT] Failed to convert image to bytes: {e}")
            raise


# Global OCR client instance
ocr_client = OCRClient()


# Convenience functions for backward compatibility
async def process_image_via_ocr_service(
    image: Union[np.ndarray, str],
) -> Dict[str, Any]:
    """
    Process image using OCR processor microservice.

    This is a convenience function that uses the global ocr_client instance.

    Args:
        image: Image as numpy array or file path

    Returns:
        dict: OCR result from processor service
    """
    return await ocr_client.process_image(image)


async def check_ocr_service_health() -> bool:
    """
    Check if OCR processor service is available.

    Returns:
        bool: True if service is healthy
    """
    return await ocr_client.health_check()
