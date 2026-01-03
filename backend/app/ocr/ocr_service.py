"""
OCR Service - Main Entry Point
==============================
Primary interface for Croatian receipt OCR processing from API endpoints.

This module provides the main entry point for OCR processing, serving as a
bridge between the REST API and the complex OCR pipeline. It handles:
- Image format conversion and validation
- OCR pipeline initialization and management
- Fallback processing strategies
- Error handling and logging

Processing Pipeline:
    API Request → OCR Service → OCR Pipeline → Processing Results

Key Features:
- PaddleOCR integration for Croatian text recognition
- Automatic image preprocessing and enhancement
- Receipt boundary detection and cropping
- Multi-strategy processing with fallbacks
- Comprehensive error handling

Usage:
    from app.ocr.ocr_service import run_ocr_with_fallback

    # Process OpenCV image
    result = run_ocr_with_fallback(cv2_image)

    # Extract data
    items = result.get("items", [])
    total = result.get("total", 0.0)
"""

import logging

from app.core.constants import DEBUG_SAVE_FILES
from app.ocr.pipeline.simple_ocr_pipeline import SimpleOCRPipeline

logger = logging.getLogger(__name__)

# Create SimpleOCRPipeline instance with PaddleOCR engine
# UPDATED: Now includes auto country detection for Croatian vs Bosnian receipts
# Debug file saving controlled by DEBUG_SAVE_FILES environment variable
# Production (DEBUG_SAVE_FILES=False): Logs only, no files saved
# Development (DEBUG_SAVE_FILES=True): Saves debug images + JSON for troubleshooting
ocr_pipeline = SimpleOCRPipeline(debug=DEBUG_SAVE_FILES)


def run_ocr_with_fallback(image, debug_utility: bool = False) -> dict:
    """
    Main OCR entry point for uploaded receipt images.
    Accepts OpenCV image, returns parsed receipt data.

    UPDATED: Now using SimpleOCRPipeline with auto country detection
    """
    try:
        # Process with SimpleOCRPipeline (handles both image array and file-based internally)
        logger.info("[OCR SERVICE] Processing with SimpleOCRPipeline")
        result = ocr_pipeline.process_image(
            image, image_filename="uploaded_image.jpg", debug_utility=debug_utility
        )

        if result.get("success", False):
            logger.info("[OCR SERVICE] Processing successful")
            return result
        else:
            logger.error(
                f"[OCR SERVICE] Processing failed: {result.get('error', 'Unknown error')}"
            )
            return result

    except Exception as e:
        logger.exception("[OCR SERVICE] Critical failure in OCR pipeline")
        return {
            "success": False,
            "error": f"OCR service critical failure: {str(e)}",
            "raw_text": "",
            "parsed_data": {},
            "image_path": None,
            "confidence": 0.0,
            "ocr_attempts": 0,
            "processing_attempts": 0,
        }


def validate_ocr_result(result: dict) -> dict:
    """
    Validate and enhance OCR result with additional quality checks.
    """
    if not result.get("success", False):
        return result

    # Handle both old (parsed_data) and new (receipt) formats
    if "receipt" in result:
        receipt_data = result.get("receipt", {})
        items = receipt_data.get("items", [])
        total = receipt_data.get("total")
        store = receipt_data.get("store", "")
    else:
        # Fallback to old format
        parsed_data = result.get("parsed_data", {})
        items = parsed_data.get("items", [])
        total = parsed_data.get("total")
        store = parsed_data.get("store", "")

    # Quality validation
    quality_issues = []

    # Check if we have meaningful items
    if not items:
        quality_issues.append("no_items_found")
    elif len(items) == 1 and not items[0].get("name", "").strip():
        quality_issues.append("empty_item_names")

    # Check if total makes sense
    if total is None:
        quality_issues.append("no_total_found")
    elif total <= 0:
        quality_issues.append("invalid_total")
    elif items:
        calculated_total = sum(item.get("total", 0) for item in items)
        if calculated_total > 0 and abs(total - calculated_total) > 1.0:
            quality_issues.append("total_mismatch")

    # Check store name
    # (store variable already defined above)
    if not store or store == "Unknown Store":
        quality_issues.append("no_store_name")

    # Add quality assessment
    result["quality_issues"] = quality_issues
    result["quality_score"] = max(0, 1.0 - (len(quality_issues) * 0.2))

    # Adjust confidence based on quality issues
    original_confidence = result.get("confidence", 0.0)
    quality_penalty = len(quality_issues) * 0.1
    result["confidence"] = max(0, original_confidence - quality_penalty)

    if quality_issues:
        logger.warning(
            f"[OCR SERVICE] Quality issues detected: {', '.join(quality_issues)}"
        )
    else:
        logger.info("[OCR SERVICE] High quality result - no major issues detected")

    return result


def run_ocr_with_validation(image) -> dict:
    """
    OCR with additional validation - alternative entry point.
    """
    result = run_ocr_with_fallback(image)
    return validate_ocr_result(result)


# Backward compatibility - keeping your original function name
def run_ocr_with_fallback_legacy(image) -> dict:
    """
    Legacy function name support - calls the improved version.
    """
    return run_ocr_with_fallback(image)
