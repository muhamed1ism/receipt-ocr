"""
OCR Execution Module
====================
Handles PaddleOCR execution with Croatian text correction.

This module coordinates:
- Image preprocessing (CLAHE)
- OCR execution with proper RGB format
- Text box merging into complete lines
- Croatian text correction
- Fallback strategies
"""

import logging
from typing import Callable, List, Tuple

import cv2
import numpy as np

from .paddle_engine import get_ocr_engine
from .simplified_preprocessing import SimplifiedPreprocessing
from .text_correction import CroatianTextCorrector
from .bosnian_text_correction import BosnianTextCorrector
from .text_merging import merge_horizontal_text_boxes

logger = logging.getLogger(__name__)

# Minimum text length to consider a result valid
MIN_TEXT_LENGTH = 3


def ensure_rgb_image(image: np.ndarray, debug: bool = False) -> np.ndarray:
    """
    Ensure image is in RGB format with 3 channels for PaddleOCR.

    PaddleOCR expects RGB format (not BGR). This function converts
    grayscale images to RGB.

    Args:
        image: Input image (grayscale or color)
        debug: Enable debug logging

    Returns:
        RGB image with 3 channels
    """
    if len(image.shape) == 2:  # Grayscale image (height, width)
        rgb_image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        if debug:
            logger.debug(f"Converted grayscale to RGB: {rgb_image.shape}")
        return rgb_image
    elif len(image.shape) == 3 and image.shape[2] == 1:  # Single channel
        rgb_image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        if debug:
            logger.debug(f"Converted single channel to RGB: {rgb_image.shape}")
        return rgb_image
    elif len(image.shape) == 3 and image.shape[2] == 3:
        # Already 3 channels - assume it's in the correct format
        return image
    else:
        raise ValueError(f"Unsupported image shape: {image.shape}")


def quick_country_detection(image: np.ndarray, debug: bool = False) -> str:
    """
    Quick pre-OCR country detection based on business ID patterns.

    Performs fast OCR scan to detect Bosnian (JIB/PIB/IBFM) vs Croatian (OIB)
    business identifiers. This helps determine if Croatian text corrections
    should be applied.

    Args:
        image: Receipt image as numpy array
        debug: Enable debug logging

    Returns:
        str: "BA" (Bosnia), "HR" (Croatia), or "UNKNOWN"
    """
    import re

    try:
        # Get OCR engine for quick scan
        ocr_engine = get_ocr_engine(lang="hr")

        # Ensure proper image format
        rgb_image = ensure_rgb_image(image.copy(), debug=False)

        # Run quick OCR - just need first ~15 lines to find business IDs
        ocr_result = ocr_engine.ocr.predict(rgb_image)

        if not ocr_result or not ocr_result[0]:
            if debug:
                logger.debug("[COUNTRY DETECTION] No OCR result, returning UNKNOWN")
            return "UNKNOWN"

        # Extract text from OCR result
        texts: list[str] = []
        result_obj = ocr_result[0]

        # PaddleOCR 2.6.x format
        if isinstance(result_obj, list):
            for line in result_obj[:15]:
                if isinstance(line, (list, tuple)) and len(line) >= 2:
                    text_info = line[1]
                    text = (
                        text_info[0]
                        if isinstance(text_info, (list, tuple))
                        else text_info
                    )
                    texts.append(str(text).upper())

        # PaddleOCR 3.x format
        elif isinstance(result_obj, dict) and "rec_texts" in result_obj:
            for text in result_obj["rec_texts"][:15]:
                texts.append(str(text).upper())

        else:
            if debug:
                logger.debug(
                    f"[COUNTRY DETECTION] Unsupported OCR result format: {type(result_obj)}"
                )
            return "UNKNOWN"

        combined_text = " ".join(texts)

        # Check for Bosnian indicators (priority - more specific)
        bosnian_patterns = [
            r"\bJIB\d",  # Jedinstveni Identifikacioni Broj (followed by digits, no space)
            r"\bPIB\d",  # Poreski Identifikacioni Broj (followed by digits, no space)
            r"\bIBFM\b",  # Fiscal device ID
            r"\bBFMBP\d",  # IBFM with BP prefix (e.g., BFMBP002450)
            r"\bSB\b",  # Sistem Broj (JIB alias)
            r"\bMB\b",  # Matični Broj (JIB alias)
            r"\bPB\b",  # Poreski Broj (PIB alias)
            r"\bFISKALNI\s+RACUN\b",  # Bosnian fiscal receipt
            r"\bKONFIG\s*FISCAL\b",  # Config fiscal
            r"\bCONFIG\s*FISCAL\b",  # Config fiscal (alternative spelling)
        ]

        bosnian_cities = [
            "MOSTAR",
            "SARAJEVO",
            "BANJA LUKA",
            "TUZLA",
            "ZENICA",
            "JABLANICA",
        ]

        for pattern in bosnian_patterns:
            if re.search(pattern, combined_text):
                if debug:
                    logger.debug(
                        f"[COUNTRY DETECTION] Found Bosnian pattern: {pattern} → BA"
                    )
                return "BA"

        for city in bosnian_cities:
            if city in combined_text:
                if debug:
                    logger.debug(f"[COUNTRY DETECTION] Found Bosnian city: {city} → BA")
                return "BA"

        # Check for Croatian indicators
        croatian_patterns = [
            r"\bOIB\b",  # Osobni Identifikacioni Broj (11 digits)
            r"\bZKI\b",  # Zaštitni Kod Izdavatelja
            r"\bJIR\b",  # Jedinstveni Identifikator Računa
        ]

        croatian_cities = ["SPLIT", "ZAGREB", "RIJEKA", "DUBROVNIK", "OSIJEK", "ZADAR"]

        for pattern in croatian_patterns:
            if re.search(pattern, combined_text):
                if debug:
                    logger.debug(
                        f"[COUNTRY DETECTION] Found Croatian pattern: {pattern} → HR"
                    )
                return "HR"

        for city in croatian_cities:
            if city in combined_text:
                if debug:
                    logger.debug(
                        f"[COUNTRY DETECTION] Found Croatian city: {city} → HR"
                    )
                return "HR"

        # No clear indicators found
        if debug:
            logger.debug("[COUNTRY DETECTION] No clear indicators → UNKNOWN")
        return "UNKNOWN"

    except Exception as e:
        logger.warning(f"[COUNTRY DETECTION] Failed: {e} → UNKNOWN")
        return "UNKNOWN"


def extract_text_from_ocr_result(
    ocr_result,
    text_corrector: CroatianTextCorrector,
    bosnian_text_corrector: BosnianTextCorrector,
    strategy_name: str,
    config_index: int = 0,
    debug: bool = False,
    skip_croatian_corrections: bool = False,
) -> Tuple[str, int, str] | None:
    """
    Extract and clean text from PaddleOCR result.

    Handles:
    - Text extraction from OCR result format (2.6.x and 3.x)
    - Horizontal text box merging
    - Croatian/Bosnian text correction
    - Text cleaning

    Args:
        ocr_result: PaddleOCR result object
        text_corrector: Croatian text corrector instance
        bosnian_text_corrector: Bosnian text corrector instance
        strategy_name: Name of preprocessing strategy used
        config_index: Configuration index for compatibility
        debug: Enable debug logging
        skip_croatian_corrections: Skip Croatian-specific corrections (for Bosnian receipts)

    Returns:
        Tuple of (cleaned_text, config_index, strategy_name) or None if extraction fails
    """
    if not ocr_result or len(ocr_result) == 0:
        return None

    try:
        result_obj = ocr_result[0]

        if result_obj is None or (
            isinstance(result_obj, (list, dict)) and len(result_obj) == 0
        ):
            if debug:
                logger.debug("Result object is None or empty")
            return None

        # PaddleOCR 2.6.x format: list of [bbox, (text, score)]
        # PaddleOCR 3.x format: dict with 'rec_texts', 'rec_scores', 'rec_boxes'

        rec_texts = []
        rec_scores = []
        rec_boxes = []

        # Try to detect format
        if isinstance(result_obj, list):
            # PaddleOCR 2.6.x format
            for item in result_obj:
                if isinstance(item, (list, tuple)) and len(item) >= 2:
                    bbox, text_info = item[0], item[1]
                    if isinstance(text_info, (list, tuple)) and len(text_info) >= 2:
                        text, confidence = text_info[0], text_info[1]
                        rec_texts.append(text)
                        rec_scores.append(confidence)
                        rec_boxes.append(bbox)

            if debug:
                logger.debug(
                    f"Parsed PaddleOCR 2.6.x format: {len(rec_texts)} text boxes"
                )

        elif hasattr(result_obj, "__getitem__") and "rec_texts" in result_obj:
            # PaddleOCR 3.x format
            rec_texts = result_obj["rec_texts"]
            rec_scores = result_obj.get("rec_scores", [])
            rec_boxes = result_obj.get("rec_boxes", [])

            if debug:
                logger.debug(
                    f"Parsed PaddleOCR 3.x format: {len(rec_texts)} text boxes"
                )

        else:
            if debug:
                logger.debug(f"Unexpected result format: {type(result_obj)}")
            return None

        if not rec_texts:
            if debug:
                logger.debug("No texts extracted from OCR result")
            return None

        if debug:
            logger.debug(f"Extracted {len(rec_texts)} text boxes from OCR")

        # Merge horizontally-aligned text boxes into complete lines
        if rec_boxes is not None and np.size(rec_boxes) > 0:
            if skip_croatian_corrections:
                # Bosnian receipt - use horizontal merging to group qty/price/total on same line
                # CRITICAL: Bosnian receipts have quantity, price, total as separate boxes on same horizontal line
                # Example: "1.000x" (left), "3.45" (middle), "3.45E" (right) must be merged as one line
                if debug:
                    logger.debug(
                        "[BOSNIAN RECEIPT] Using y-threshold merging to preserve qty/price/total grouping"
                    )
                merged_lines = merge_horizontal_text_boxes(
                    rec_texts,
                    rec_scores,
                    rec_boxes,
                    y_threshold=None,  # Auto-detect optimal threshold (will group boxes ~12px apart)
                    auto_detect=True,  # Enable auto-detection
                    debug=debug,
                )
            else:
                # Croatian receipt - use standard horizontal merging
                merged_lines = merge_horizontal_text_boxes(
                    rec_texts,
                    rec_scores,
                    rec_boxes,
                    y_threshold=None,  # Auto-detect optimal threshold
                    auto_detect=True,  # Enable auto-detection
                    debug=debug,
                )

            if debug:
                logger.debug(f"Merged into {len(merged_lines)} complete lines")
        else:
            # Fallback: use original texts if no boxes available
            merged_lines = [text.strip() for text in rec_texts if text.strip()]
            if debug:
                logger.debug("No bounding boxes available, using unmerged texts")

        # Process merged lines
        if merged_lines:
            raw_text = "\n".join(merged_lines)

            # Apply corrections based on receipt country
            if skip_croatian_corrections:
                # Bosnian receipt - apply Bosnian-specific corrections
                if debug:
                    logger.info("[BOSNIAN RECEIPT] Applying Bosnian text corrections")

                # Step 1: Apply Bosnian OCR error corrections
                corrected_text = bosnian_text_corrector.correct_bosnian_ocr_errors(
                    raw_text
                )

                # Step 2: Apply Bosnian text cleaning
                cleaned_text = bosnian_text_corrector.clean_text(corrected_text)

                if debug:
                    logger.info(
                        f"[BOSNIAN] Corrections applied: {len(raw_text)} → {len(cleaned_text)} chars"
                    )
            else:
                # Croatian receipt or unknown - apply standard Croatian corrections
                if debug:
                    logger.debug(
                        "[CROATIAN/UNKNOWN RECEIPT] Applying Croatian text corrections"
                    )
                corrected_text = text_corrector.correct_croatian_ocr_errors(raw_text)
                cleaned_text = text_corrector.clean_text(corrected_text)

            # Only accept meaningful results
            if cleaned_text and len(cleaned_text.strip()) > MIN_TEXT_LENGTH:
                if debug:
                    logger.debug(f"Extracted {len(cleaned_text)} chars")
                    logger.debug(f"Preview: {cleaned_text[:100]}...")
                return (cleaned_text, config_index, strategy_name)

        return None

    except Exception as e:
        logger.error(f"Error extracting text from OCR result: {e}")
        if debug:
            logger.debug(f"Full ocr_result structure: {ocr_result}")
        import traceback

        logger.debug(traceback.format_exc())
        return None


def run_ocr_on_image(
    image: np.ndarray,
    lang: str = "hr",
    debug: bool = False,
    auto_detect_country: bool = True,
    return_raw_result: bool = False,
    debug_save_callback: Callable[..., None] | None = None,
) -> List[Tuple[str, int, str]] | Tuple[List[Tuple[str, int, str]], List]:
    """
    Enhanced OCR with PaddleOCR for Croatian and Bosnian receipts.

    Args:
        image: Input image as numpy array
        lang: Language code - defaults to 'hr' for Croatian (Latin script)
              Supports: 'hr' (Croatian), 'bs' (Bosnian), 'en', 'ch', 'fr', 'german', etc.
              Note: 'hr' and 'bs' produce identical results (same Latin dictionary)
              Use 'hr' for both Croatian and Bosnian receipts
        debug: Enable debug logging
        auto_detect_country: Automatically detect country and skip Croatian corrections for Bosnian receipts
        return_raw_result: If True, return tuple of (results, raw_ocr_result) for debug session saving
        debug_save_callback: Optional callback function(name, image) to save debug preprocessing images

    Returns:
        List of (text, config_index, config_name) tuples for compatibility
        OR if return_raw_result=True: Tuple of (results, raw_ocr_result)
    """
    if debug:
        logger.info(f"[PADDLE OCR] Processing image (shape: {image.shape})")

    # Detect receipt country early if auto-detection enabled
    skip_croatian_corrections = False
    if auto_detect_country:
        detected_country = quick_country_detection(image, debug=debug)
        skip_croatian_corrections = detected_country == "BA"
        logger.info(
            f"[PADDLE OCR] Auto-detected country: {detected_country}, skip_croatian_corrections={skip_croatian_corrections}"
        )

    results = []
    raw_ocr_result = None  # Store raw OCR result for debug session saving
    text_corrector = CroatianTextCorrector()
    bosnian_text_corrector = BosnianTextCorrector()

    # Get OCR engine first (before try block so it's available in fallback)
    try:
        ocr_engine = get_ocr_engine(lang=lang)
        if debug:
            logger.debug(f"[PADDLE OCR] OCR engine obtained for lang={lang}")
    except Exception as e:
        logger.error(f"[PADDLE OCR] Failed to initialize OCR engine: {e}")
        if return_raw_result:
            return results, []
        return results

    # Try preprocessing approach
    try:
        # Initialize components
        preprocessor = SimplifiedPreprocessing()

        if debug:
            logger.debug("Using simplified CLAHE-only preprocessing")

        # Apply CLAHE preprocessing with debug callback
        processed_image = preprocessor.preprocess_for_ocr(
            image, debug_save=debug_save_callback
        )

        if debug:
            logger.debug(
                f"CLAHE preprocessing applied - shape: {processed_image.shape}"
            )

        # CRITICAL: Ensure image is in RGB format for PaddleOCR
        processed_image = ensure_rgb_image(processed_image, debug=debug)

        # Save RGB image to debug session if callback provided
        if debug_save_callback:
            debug_save_callback("07_ocr_ready_rgb", processed_image)

        # Run OCR with preprocessed image
        if debug:
            logger.debug("Running OCR with CLAHE preprocessing")

        ocr_result = ocr_engine.ocr.predict(processed_image)

        # Store raw result for debug session saving
        if return_raw_result and ocr_result and len(ocr_result) > 0:
            raw_ocr_result = ocr_result[
                0
            ]  # PaddleOCR format: [[box, (text, confidence)], ...]

        if debug:
            logger.debug("OCR processing completed successfully")

        # Extract text from result
        extraction = extract_text_from_ocr_result(
            ocr_result,
            text_corrector,
            bosnian_text_corrector,
            strategy_name="paddle_clahe_preprocessing",
            config_index=0,
            debug=debug,
            skip_croatian_corrections=skip_croatian_corrections,
        )

        if extraction:
            results.append(extraction)
            if debug:
                logger.info(
                    f"[PADDLE OCR] CLAHE preprocessing: extracted {len(extraction[0])} chars"
                )

    except Exception as e:
        if debug:
            logger.warning(f"[PADDLE OCR] CLAHE preprocessing failed: {e}")
        import traceback

        if debug:
            logger.debug(traceback.format_exc())

    # If no good results with preprocessing, try basic OCR on original
    if not results:
        if debug:
            logger.info(
                "[PADDLE OCR] No results from preprocessing, trying original image"
            )

        try:
            # Ensure original image is in RGB format
            original_rgb = ensure_rgb_image(image.copy(), debug=debug)

            # Run OCR on original
            ocr_result = ocr_engine.ocr.predict(original_rgb)

            # Store raw result for debug session saving
            if return_raw_result and ocr_result and len(ocr_result) > 0:
                raw_ocr_result = ocr_result[
                    0
                ]  # PaddleOCR format: [[box, (text, confidence)], ...]

            # Extract text from fallback result
            extraction = extract_text_from_ocr_result(
                ocr_result,
                text_corrector,
                bosnian_text_corrector,
                strategy_name="paddle_original",
                config_index=999,
                debug=debug,
                skip_croatian_corrections=skip_croatian_corrections,
            )

            if extraction:
                results.append(extraction)
                if debug:
                    logger.info(
                        f"[PADDLE OCR] Original result: {extraction[0][:50]}..."
                    )

        except Exception as e:
            if debug:
                logger.warning(f"[PADDLE OCR] Original image failed: {e}")

    if debug:
        logger.info(f"[PADDLE OCR] Total successful extractions: {len(results)}")
        if results:
            best_result = max(results, key=lambda x: len(x[0]))
            logger.info(f"[PADDLE OCR] Best result preview: {best_result[0][:100]}...")

    # Return raw OCR result if requested (for debug session saving)
    if return_raw_result:
        if raw_ocr_result is None:
            raw_ocr_result = []
        return results, raw_ocr_result

    return results
