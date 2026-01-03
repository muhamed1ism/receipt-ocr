"""
OCR Service Wrapper
===================
Smart wrapper that routes OCR requests to either:
1. OCR Processor microservice (containerized deployment)
2. Local OCR pipeline (development/fallback)

This module automatically detects the deployment environment and routes
OCR processing accordingly, ensuring the API works in both:
- Production: Containerized deployment with separate OCR processor
- Development: Local processing with PaddleOCR directly

Architecture Decision:
    if OCR_PROCESSOR_URL is set and reachable:
        → Use OCR Client (microservice architecture)
    else:
        → Use Local OCR Pipeline (monolithic fallback)

Usage:
    from app.ocr.ocr_service_wrapper import process_receipt_image

    # This function automatically routes to the right implementation
    result = await process_receipt_image(image)
"""

import logging
import os
import asyncio
from typing import Dict, Any, Union
import numpy as np
from app.config import OCR_PROCESSOR_URL

logger = logging.getLogger(__name__)

# Global flag to track which mode we're using
_USE_OCR_CLIENT = None
_OCR_MODE_CHECKED = False


async def _check_ocr_processor_available() -> bool:
    """
    Check if OCR processor microservice is available.

    Returns:
        bool: True if OCR processor is reachable
    """
    global _USE_OCR_CLIENT, _OCR_MODE_CHECKED

    # Only check once per application startup
    if _OCR_MODE_CHECKED:
        return bool(_USE_OCR_CLIENT)

    # If OCR_PROCESSOR_URL is not set, use local processing
    if not OCR_PROCESSOR_URL:
        logger.info("[OCR WRAPPER] OCR_PROCESSOR_URL not set - using local OCR pipeline")
        _USE_OCR_CLIENT = False
        _OCR_MODE_CHECKED = True
        return False

    # Try to reach OCR processor
    try:
        from app.ocr.ocr_client import check_ocr_service_health

        is_healthy = await check_ocr_service_health()

        if is_healthy:
            logger.info(f"[OCR WRAPPER] OCR processor available at {OCR_PROCESSOR_URL} - using microservice mode")
            _USE_OCR_CLIENT = True
        else:
            logger.warning(f"[OCR WRAPPER] OCR processor at {OCR_PROCESSOR_URL} is not healthy - falling back to local processing")
            _USE_OCR_CLIENT = False

        _OCR_MODE_CHECKED = True
        return _USE_OCR_CLIENT

    except Exception as e:
        logger.warning(f"[OCR WRAPPER] Cannot reach OCR processor: {e} - falling back to local processing")
        _USE_OCR_CLIENT = False
        _OCR_MODE_CHECKED = True
        return False


async def process_receipt_image(
    image: Union[np.ndarray, str],
    debug_utility: bool = False
) -> Dict[str, Any]:
    """
    Process receipt image using the best available OCR method.

    This function automatically detects whether to use:
    - OCR Processor microservice (containerized deployment)
    - Local OCR pipeline (development/fallback)

    Args:
        image: Image as numpy array (OpenCV format) or file path
        debug_utility: Enable debug session saving (saves to ocr_debug_sessions/)

    Returns:
        dict: OCR processing result with structure matching original format
    """
    # Check which OCR mode to use
    use_client = await _check_ocr_processor_available()

    if use_client:
        # Use OCR Client (microservice)
        return await _process_via_client(image, debug_utility)
    else:
        # Use local OCR pipeline (fallback)
        return await _process_locally(image, debug_utility)


async def _process_via_client(image: Union[np.ndarray, str], debug_utility: bool = False) -> Dict[str, Any]:
    """
    Process image via OCR processor microservice.

    Args:
        image: Image as numpy array or file path
        debug_utility: Enable debug session saving (Note: not supported in microservice mode yet)

    Returns:
        dict: OCR result converted to standard format
    """
    try:
        from app.ocr.ocr_client import process_image_via_ocr_service

        logger.info("[OCR WRAPPER] Processing via OCR microservice")

        # Call OCR processor container
        ocr_result = await process_image_via_ocr_service(image)

        # OCR processor returns raw OCR lines, we need to parse them
        # Import parser here to convert OCR text to structured receipt data
        from app.ocr.parsing.receipt_parser import ReceiptParser

        if ocr_result.get("success"):
            lines = ocr_result.get("lines", [])
            confidence = ocr_result.get("confidence", 0.0)

            logger.info(f"[OCR WRAPPER] Received {len(lines)} lines from OCR processor, parsing...")

            # Parse the OCR lines into structured receipt data
            parser = ReceiptParser()
            parsed_data = parser.parse_receipt(lines, log_debug=False)

            # Combine results
            return {
                "success": True,
                "receipt": parsed_data,
                "raw_text": "\n".join(lines),
                "confidence": confidence,
                "processing_time_ms": ocr_result.get("processing_time_ms", 0),
                "line_count": len(lines),
                "ocr_method": "microservice"
            }
        else:
            logger.error(f"[OCR WRAPPER] OCR processor failed: {ocr_result.get('error')}")
            return {
                "success": False,
                "error": ocr_result.get("error", "OCR processor failed"),
                "receipt": {},
                "raw_text": "",
                "confidence": 0.0,
                "ocr_method": "microservice"
            }

    except Exception as e:
        logger.error(f"[OCR WRAPPER] Client processing failed: {e}, falling back to local")
        # If client fails, try local processing as fallback
        return await _process_locally(image, debug_utility=debug_utility)


async def _process_locally(
    image: Union[np.ndarray, str],
    debug_utility: bool = False
) -> Dict[str, Any]:
    """
    Process image using local OCR pipeline.

    This is used in development or as a fallback when OCR processor is unavailable.

    Args:
        image: Image as numpy array or file path
        debug_utility: Enable debug session saving

    Returns:
        dict: OCR result from local pipeline
    """
    try:
        from app.ocr.ocr_service import run_ocr_with_fallback
        from functools import partial

        logger.info("[OCR WRAPPER] Processing via local OCR pipeline")

        # Run local OCR in thread pool to avoid blocking
        # run_ocr_with_fallback is synchronous, so wrap it
        loop = asyncio.get_event_loop()
        # Use partial to pass debug_utility parameter
        ocr_func = partial(run_ocr_with_fallback, image, debug_utility)
        result = await loop.run_in_executor(None, ocr_func)

        # Add OCR method indicator
        if isinstance(result, dict):
            result["ocr_method"] = "local"

        return result

    except ImportError as e:
        # This happens in API container where PaddleOCR is not installed
        logger.error(f"[OCR WRAPPER] Local OCR not available (dependencies missing): {e}")
        return {
            "success": False,
            "error": "OCR processor unavailable and local OCR dependencies not installed",
            "receipt": {},
            "raw_text": "",
            "confidence": 0.0,
            "ocr_method": "unavailable"
        }
    except Exception as e:
        logger.error(f"[OCR WRAPPER] Local processing failed: {e}")
        return {
            "success": False,
            "error": f"Local OCR processing failed: {str(e)}",
            "receipt": {},
            "raw_text": "",
            "confidence": 0.0,
            "ocr_method": "local"
        }


# Backward compatible function name
async def run_ocr_with_fallback_async(image: Union[np.ndarray, str]) -> Dict[str, Any]:
    """
    Async version of run_ocr_with_fallback for backward compatibility.

    Args:
        image: Image as numpy array or file path

    Returns:
        dict: OCR processing result
    """
    return await process_receipt_image(image)
