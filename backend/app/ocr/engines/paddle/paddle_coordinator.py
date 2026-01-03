"""
PaddleOCR Coordinator
====================
PaddleOCR-specific processing coordination with multiple strategies.

PIPELINE HIERARCHY:
    ocr_service.py (API Entry)
        ↓
    pipeline/ocr_orchestrator.py (MAIN PIPELINE)
        ↓
    pipeline/processing_coordinator.py (Multi-Strategy Coordination)
        ↓  
    engines/paddle/paddle_coordinator.py (THIS FILE - PaddleOCR Engine)
        ↓
    engines/paddle/paddle_engine.py (PaddleOCR Wrapper)

PURPOSE:
- Handles PaddleOCR-specific processing strategies
- Manages multiple image preprocessing approaches  
- Coordinates OCR execution with quality scoring
- Different from pipeline/ocr_orchestrator.py which is the main pipeline
"""

import os
import cv2
import logging
from typing import List, Tuple
import numpy as np
import json
import datetime
import traceback

from app.core.constants import DEBUG_IMAGE_DIR, DEBUG_SAVE_FILES
from .paddle_engine import get_ocr_engine
from .preprocessing_selector import PreprocessingSelector
# OCR Enhancement strategies have been archived to follow V0.2.5 approach
from .text_correction import CroatianTextCorrector

logger = logging.getLogger(__name__)


def calculate_adaptive_threshold(items, debug=False):
    """
    Automatically calculate optimal y_threshold based on actual receipt data.

    Strategy:
    1. Sort all text boxes by Y position (top to bottom)
    2. Calculate vertical gaps between consecutive boxes
    3. Separate "small gaps" (within same line) from "large gaps" (between lines)
    4. Use 90th percentile of small gaps as threshold

    This adapts to:
    - Different font sizes (receipts with large vs small text)
    - Different receipt formats (tight vs loose spacing)
    - OCR misalignment (slight vertical variations)

    Args:
        items: List of dicts with 'y_center', 'x1', 'text' keys
        debug: Enable debug logging

    Returns:
        float: Optimal y_threshold in pixels

    Example:
        Items at Y: [50, 52, 55, 78, 80, 82, 105, ...]
        Gaps:       [2,  3,  23, 2,  2,  23, ...]
        Small gaps: [2, 3, 2, 2] (within same line)
        Large gaps: [23, 23] (between lines)
        90th percentile of [2,3,2,2] = 3
        Threshold: 3 + safety margin = ~18
    """
    if not items or len(items) < 2:
        if debug:
            logger.debug("[AUTO-THRESHOLD] Not enough items, using fallback=15")
        return 15.0  # Fallback for empty receipts

    # Sort by Y position (top to bottom)
    sorted_items = sorted(items, key=lambda x: x['y_center'])

    # Calculate gaps between consecutive items
    gaps = []
    for i in range(len(sorted_items) - 1):
        gap = abs(sorted_items[i+1]['y_center'] - sorted_items[i]['y_center'])
        if gap > 0.1:  # Ignore items at exactly same Y
            gaps.append(gap)

    if not gaps:
        if debug:
            logger.debug("[AUTO-THRESHOLD] No gaps found, using fallback=15")
        return 15.0

    # Filter out extreme outliers (gaps > 50px are definitely line breaks)
    # We only want to analyze "reasonable" gaps to find within-line threshold
    reasonable_gaps = [g for g in gaps if g < 50]

    if not reasonable_gaps:
        if debug:
            logger.debug("[AUTO-THRESHOLD] All gaps are large, using fallback=15")
        return 15.0

    # Use 90th percentile of reasonable gaps
    # This means: "90% of items within a line have gaps <= this value"
    threshold = np.percentile(reasonable_gaps, 90)

    # Apply safety bounds:
    # - Minimum: 8px (don't merge items closer than 8px)
    # - Maximum: 30px (don't merge items farther than 30px)
    threshold = max(8.0, min(30.0, threshold))

    if debug:
        logger.debug(f"[AUTO-THRESHOLD] Analyzed {len(gaps)} gaps")
        logger.debug(f"[AUTO-THRESHOLD] Reasonable gaps (<50px): {sorted(reasonable_gaps)[:20]}")
        logger.debug(f"[AUTO-THRESHOLD] 90th percentile: {np.percentile(reasonable_gaps, 90):.1f}px")
        logger.debug(f"[AUTO-THRESHOLD] Final threshold (with bounds): {threshold:.1f}px")

    return float(threshold)


def merge_horizontal_text_boxes(rec_texts, rec_scores, rec_boxes,
                                 y_threshold=None,      # Changed from 10 to None for auto-detection
                                 auto_detect=True,      # NEW: Enable automatic threshold detection
                                 debug=False):
    """
    Merge OCR text boxes that are on the same horizontal line.

    PaddleOCR detects individual text boxes (columns), but receipts have
    tab-separated data on the same line. This function merges boxes that
    are vertically aligned into complete lines.

    Args:
        rec_texts: List of recognized text strings
        rec_scores: List of confidence scores
        rec_boxes: List/array of bounding boxes [[x1, y1, x2, y2], ...]
        y_threshold: Maximum Y-difference to consider boxes on same line (None = auto-detect)
        auto_detect: Enable automatic threshold detection based on receipt gaps
        debug: Enable debug logging

    Returns:
        List of merged text lines (strings)

    Example:
        Input:  ['kava', '2.10', '1', '2.10']  with Y coords [50, 48, 52, 49]
        Output: ['kava    2.10    1    2.10']
    """
    if not rec_texts or len(rec_texts) == 0:
        return []

    # Convert rec_boxes to numpy array if needed
    if hasattr(rec_boxes, 'tolist'):
        boxes = rec_boxes.tolist() if hasattr(rec_boxes, 'tolist') else rec_boxes
    else:
        boxes = rec_boxes

    # Create list of (text, score, box) tuples
    items = []
    for i, text in enumerate(rec_texts):
        score = rec_scores[i] if i < len(rec_scores) else 0.0
        box = boxes[i] if i < len(boxes) else None

        if box is not None and text.strip():
            # Extract coordinates - handle different box formats
            if len(box) == 4:  # [x1, y1, x2, y2]
                x1, y1, x2, y2 = box
            elif len(box) > 4:  # Polygon format [[x1,y1], [x2,y2], ...]
                # Get min/max coordinates
                xs = [p[0] for p in box] if isinstance(box[0], (list, tuple)) else [box[0], box[2]]
                ys = [p[1] for p in box] if isinstance(box[0], (list, tuple)) else [box[1], box[3]]
                x1, y1, x2, y2 = min(xs), min(ys), max(xs), max(ys)
            else:
                continue

            y_center = (y1 + y2) / 2
            items.append({
                'text': text.strip(),
                'score': score,
                'x1': x1,
                'y_center': y_center,
                'x2': x2
            })

    if not items:
        return []

    # AUTO-DETECT threshold if not manually specified
    if auto_detect and y_threshold is None:
        y_threshold = calculate_adaptive_threshold(items, debug=debug)
        if debug:
            logger.debug(f"[MERGE] Using auto-detected y_threshold={y_threshold:.1f}px")
    elif y_threshold is None:
        y_threshold = 15.0  # Fallback if auto_detect is disabled
        if debug:
            logger.debug(f"[MERGE] Using fallback y_threshold={y_threshold:.1f}px")
    else:
        if debug:
            logger.debug(f"[MERGE] Using manual y_threshold={y_threshold:.1f}px")

    # Sort by Y position (top to bottom), then X position (left to right)
    items.sort(key=lambda item: (item['y_center'], item['x1']))

    # Group items into lines based on Y-position
    lines = []
    current_line = [items[0]]
    current_y = items[0]['y_center']

    for item in items[1:]:
        y_diff = abs(item['y_center'] - current_y)

        if y_diff <= y_threshold:
            # Same line - add to current line
            current_line.append(item)
        else:
            # New line - save current line and start new one
            lines.append(current_line)
            current_line = [item]
            current_y = item['y_center']

    # Don't forget the last line
    if current_line:
        lines.append(current_line)

    # Merge each line's text with spacing
    merged_lines = []
    for line in lines:
        # Sort line items by X position (left to right)
        line.sort(key=lambda item: item['x1'])

        # Calculate spacing between items and merge with appropriate gaps
        line_text = ""
        prev_x2 = None

        for item in line:
            if prev_x2 is not None:
                # Calculate gap between previous box and current box
                gap = item['x1'] - prev_x2

                # Use spacing to approximate tabs/spaces
                if gap > 30:
                    line_text += "    "  # Large gap = tab
                elif gap > 10:
                    line_text += "  "    # Medium gap = double space
                else:
                    line_text += " "     # Small gap = single space

            line_text += item['text']
            prev_x2 = item['x2']

        merged_lines.append(line_text)

    if debug:
        logger.debug(f"[MERGE] Merged {len(items)} boxes into {len(merged_lines)} lines")
        logger.debug(f"[MERGE DEBUG] Detailed line structure:")
        for i, line in enumerate(merged_lines[:10]):  # Show first 10 lines
            logger.debug(f"  Line {i:2d}: '{line}'")

    return merged_lines


def run_ocr_on_image(image: np.ndarray, configs: List[str] = None, lang: str = 'en', 
                    debug: bool = False, image_index: int = 0) -> List[Tuple[str, int, str]]:
    """
    Enhanced OCR with PaddleOCR - maintains same interface as Tesseract version.
    
    Args:
        image: Input image as numpy array
        configs: Legacy parameter for compatibility (ignored)
        lang: Language code ('en', 'ch', 'fr', 'german', 'korean', 'japan')
        debug: Enable debug logging and image saving
        image_index: Index for debug file naming
    
    Returns:
        List of (text, config_index, config_name) tuples for compatibility
    """
    if debug:
        logger.info(f"[PADDLE OCR] Processing image #{image_index} (shape: {image.shape})")
    
    # Debug info for troubleshooting (only when debug=True)
    debug_info = None
    if debug:
        debug_info = {
            "timestamp": datetime.datetime.now().isoformat(),
            "image_shape": image.shape if hasattr(image, 'shape') else None,
            "lang": lang,
            "steps": [],
            "errors": []
        }
    
    def save_debug_info():
        # Only save debug files if DEBUG_SAVE_FILES environment variable is True
        if debug and debug_info and DEBUG_SAVE_FILES:
            debug_filename = f"debug_ocr_{image_index}_{datetime.datetime.now().strftime('%H%M%S')}.json"
            debug_path = os.path.join(DEBUG_IMAGE_DIR, debug_filename)
            os.makedirs(DEBUG_IMAGE_DIR, exist_ok=True)
            # Add function_called and debug flags for tracking
            debug_info["function_called"] = True
            debug_info["debug"] = debug
            debug_info["image_index"] = image_index
            with open(debug_path, 'w') as f:
                json.dump(debug_info, f, indent=2, default=str)
            logger.debug(f"[PADDLE OCR] Saved debug info to {debug_path}")
        elif debug and debug_info and not DEBUG_SAVE_FILES:
            # Log that we skipped saving (for troubleshooting)
            logger.debug(f"[PADDLE OCR] Debug info generated but not saved (DEBUG_SAVE_FILES=False)")
    
    results = []
    
    try:
        if debug:
            logger.debug(f"[PADDLE OCR] Getting OCR engine for lang={lang}")
            if debug_info:
                debug_info["steps"].append("Getting OCR engine")
        
        # Get OCR engine (supports Croatian with 'en' as it includes Latin characters)
        # For Croatian specifically, PaddleOCR works well with English model + postprocessing
        try:
            ocr_engine = get_ocr_engine(lang=lang)
            if debug:
                logger.debug(f"[PADDLE OCR] OCR engine obtained successfully")
                debug_info["steps"].append("Step 1 SUCCESS: OCR engine obtained")
        except Exception as e:
            error_info = {
                "step": "OCR engine initialization failed",
                "error": str(e),
                "error_type": str(type(e)),
                "traceback": traceback.format_exc()
            }
            if debug and debug_info:
                debug_info["errors"].append(error_info)
            save_debug_info()
            logger.error(f"[PADDLE OCR] Failed to initialize OCR engine: {e}")
            raise
        
        if debug:
            logger.debug("OCR engine obtained, assessing image quality")
            debug_info["steps"].append("Step 2: Starting image quality assessment")
        
        # Assess image quality to determine best preprocessing strategy
        quality_assessor = PreprocessingSelector()
        quality_metrics = quality_assessor.assess_image_quality(image)

        if debug:
            logger.debug(f"Quality metrics - Brightness: {quality_metrics['mean_brightness']:.1f}, "
                        f"Contrast: {quality_metrics['contrast']:.1f}, Sharpness: {quality_metrics['sharpness']:.1f}")
            debug_info["steps"].append("Step 3: Quality metrics obtained")
        
        # Select preprocessing strategies based on image quality
        preprocessing_strategies = quality_assessor.select_preprocessing_strategies(quality_metrics)
        if debug:
            logger.debug(f"Selected {len(preprocessing_strategies)} preprocessing strategies: {preprocessing_strategies}")
            debug_info["steps"].append(f"Step 4: Selected {len(preprocessing_strategies)} strategies")
        
        # Using V0.2.5 approach - no additional preprocessing strategies
        text_corrector = CroatianTextCorrector()
        if debug:
            logger.debug("Using V0.2.5 approach - only text correction")
            debug_info["steps"].append("Step 5: Using V0.2.5 approach - only text correction")
        
        for strategy_idx, strategy in enumerate(preprocessing_strategies):
            if debug:
                logger.debug(f"Processing strategy {strategy_idx}: {strategy}")
                debug_info["steps"].append(f"Step 6: Processing strategy {strategy_idx}: {strategy}")
            
            # V0.2.5 approach: image is already optimally preprocessed by geometric processor
            processed_image = image
            if debug:
                logger.debug(f"Using V0.2.5 preprocessed image - shape: {processed_image.shape}")
                debug_info["steps"].append(f"Step 7: Preprocessed image shape: {processed_image.shape}")
            
            # CRITICAL FIX: Ensure image has 3 channels for PaddleOCR
            if len(processed_image.shape) == 2:  # Grayscale image (height, width)
                processed_image = cv2.cvtColor(processed_image, cv2.COLOR_GRAY2BGR)
                if debug:
                    logger.debug(f"Converted grayscale to 3-channel: {processed_image.shape}")
            elif len(processed_image.shape) == 3 and processed_image.shape[2] == 1:  # Single channel
                processed_image = cv2.cvtColor(processed_image, cv2.COLOR_GRAY2BGR)
                if debug:
                    logger.debug(f"Converted single channel to 3-channel: {processed_image.shape}")
            
            if debug:
                debug_info["steps"].append(f"Step 7.5: Image shape after channel fix: {processed_image.shape}")
            
            # SAVE DEBUG IMAGE for each strategy (only if DEBUG_SAVE_FILES=True)
            if debug and DEBUG_SAVE_FILES:
                debug_dir = DEBUG_IMAGE_DIR
                os.makedirs(debug_dir, exist_ok=True)
                debug_filename = f"ocr_preprocess_{image_index}_{strategy}.png"
                debug_path = os.path.join(debug_dir, debug_filename)
                cv2.imwrite(debug_path, processed_image)
                logger.debug(f"[PADDLE OCR] Saved debug image: {debug_path}")
            elif debug and not DEBUG_SAVE_FILES:
                logger.debug(f"[PADDLE OCR] Skipping debug image save for strategy '{strategy}' (DEBUG_SAVE_FILES=False)")
            
            try:
                if debug:
                    logger.debug(f"Running OCR with strategy '{strategy}' on image #{image_index}")
                
                # Run OCR with PaddleOCR's predict method
                if debug and debug_info:
                    debug_info["steps"].append(f"Step 8: Calling OCR predict for strategy {strategy}")
                try:
                    ocr_result = ocr_engine.ocr.ocr(processed_image)
                    if debug:
                        logger.debug("OCR processing completed successfully")
                        if debug_info:
                            debug_info["steps"].append("Step 9: OCR predict completed successfully")
                            debug_info["ocr_result_type"] = str(type(ocr_result))
                            debug_info["ocr_result_length"] = len(ocr_result) if ocr_result else 0
                except Exception as predict_error:
                    error_info = {
                        "step": f"Step 8 FAILED - OCR predict for strategy {strategy}",
                        "error": str(predict_error),
                        "error_type": str(type(predict_error)),
                        "traceback": traceback.format_exc(),
                        "strategy": strategy,
                        "processed_image_shape": processed_image.shape if hasattr(processed_image, 'shape') else None
                    }
                    if debug and debug_info:
                        debug_info["errors"].append(error_info)
                        save_debug_info()
                    logger.error(f"[PADDLE OCR] OCR predict failed: {predict_error}")
                    if debug:
                        logger.debug(f"Predict error type: {type(predict_error)}")
                        logger.debug(f"Traceback: {traceback.format_exc()}")
                    raise
                
                # Log result structure when debugging
                if debug:
                    logger.debug(f"OCR result type: {type(ocr_result)}, length: {len(ocr_result) if ocr_result else 'None'}")
                    if ocr_result and len(ocr_result) > 0:
                        logger.debug(f"Result[0] type: {type(ocr_result[0])}")
                        if hasattr(ocr_result[0], 'keys'):
                            logger.debug(f"Result[0] keys: {list(ocr_result[0].keys())}")
                
                if ocr_result and len(ocr_result) > 0:
                    # Extract text from new OCRResult format
                    try:
                        result_obj = ocr_result[0]
                        if debug:
                            logger.debug(f"Result object type: {type(result_obj)}")
                            if hasattr(result_obj, 'keys'):
                                logger.debug(f"Available keys in result: {list(result_obj.keys())}")
                        
                        if result_obj is None:
                            if debug:
                                logger.debug(f"Result object is None, skipping strategy {strategy}")
                            continue  # Skip this strategy and try the next one

                        extracted_lines = []

                        # Get texts, scores, and boxes from OCRResult (v3.x format)
                        if hasattr(result_obj, '__getitem__') and 'rec_texts' in result_obj:
                            rec_texts = result_obj['rec_texts']
                            rec_scores = result_obj['rec_scores'] if 'rec_scores' in result_obj else []
                            rec_boxes = result_obj['rec_boxes'] if 'rec_boxes' in result_obj else None
                        else:
                            if debug:
                                logger.debug(f"Unexpected result format: {type(result_obj)}, skipping strategy")
                            continue  # Skip this strategy

                        if debug:
                            logger.debug(f"Extracted {len(rec_texts)} text boxes from OCR")

                        # CRITICAL FIX: Merge horizontally-aligned text boxes into complete lines
                        # This fixes the issue where columns are detected as separate boxes
                        # Use y_threshold=25 to handle slight vertical misalignment in receipts
                        if rec_boxes is not None:
                            merged_lines = merge_horizontal_text_boxes(
                                rec_texts, rec_scores, rec_boxes,
                                y_threshold=None,      # Auto-detect optimal threshold
                                auto_detect=True,      # Enable auto-detection
                                debug=debug
                            )
                            if debug:
                                logger.debug(f"Merged into {len(merged_lines)} complete lines")
                        else:
                            # Fallback: use original texts if no boxes available
                            merged_lines = [text.strip() for text in rec_texts if text.strip()]
                            if debug:
                                logger.debug("No bounding boxes available, using unmerged texts")

                    except Exception as e:
                        logger.error(f"[PADDLE OCR] Error extracting text from OCR result: {e}")
                        if debug:
                            logger.debug(f"Full ocr_result structure: {ocr_result}")
                        raise

                    # Use the merged lines (already filtered and processed)
                    if merged_lines:
                        raw_text = '\n'.join(merged_lines)
                        
                        # Apply Croatian OCR error correction
                        corrected_text = text_corrector.correct_croatian_ocr_errors(raw_text)
                        
                        # Clean the extracted Croatian text
                        cleaned_text = text_corrector.clean_text(corrected_text)
                        
                        # Only accept meaningful results
                        if cleaned_text and len(cleaned_text.strip()) > 5:
                            config_name = f"paddle_{strategy}_strategy"
                            results.append((cleaned_text, strategy_idx, config_name))
                            
                            if debug:
                                logger.info(f"[PADDLE OCR] Image #{image_index}, strategy '{strategy}': "
                                          f"extracted {len(cleaned_text)} chars")
                                logger.info(f"[PADDLE OCR] Preview: {cleaned_text[:100]}...")
                
            except Exception as e:
                error_info = {
                    "step": f"Strategy {strategy} failed",
                    "error": str(e),
                    "error_type": str(type(e)),
                    "traceback": traceback.format_exc(),
                    "strategy": strategy
                }
                if debug and debug_info:
                    debug_info["errors"].append(error_info)
                if debug:
                    logger.warning(f"[PADDLE OCR] Strategy '{strategy}' failed on image #{image_index}: {e}")
                    logger.debug(f"Exception type: {type(e)}")
                continue
        
        # If no good results with preprocessing, try basic OCR on original
        if not results:
            if debug:
                logger.info(f"[PADDLE OCR] No results from preprocessing, trying original image")
            
            try:
                # CRITICAL FIX: Ensure original image has 3 channels for PaddleOCR
                original_processed = image.copy()
                if len(original_processed.shape) == 2:  # Grayscale image (height, width)
                    original_processed = cv2.cvtColor(original_processed, cv2.COLOR_GRAY2BGR)
                    if debug:
                        logger.debug(f"Fallback - Converted grayscale to 3-channel: {original_processed.shape}")
                elif len(original_processed.shape) == 3 and original_processed.shape[2] == 1:  # Single channel
                    original_processed = cv2.cvtColor(original_processed, cv2.COLOR_GRAY2BGR)
                    if debug:
                        logger.debug(f"Fallback - Converted single channel to 3-channel: {original_processed.shape}")
                
                ocr_result = ocr_engine.ocr.ocr(original_processed)

                if ocr_result and len(ocr_result) > 0:
                    # Extract text from new OCRResult format
                    try:
                        result_obj = ocr_result[0]
                        if debug:
                            logger.debug(f"Fallback result object type: {type(result_obj)}")

                        # Get texts, scores, and boxes from OCRResult (v3.x format)
                        rec_texts = result_obj['rec_texts'] if 'rec_texts' in result_obj else []
                        rec_scores = result_obj['rec_scores'] if 'rec_scores' in result_obj else []
                        rec_boxes = result_obj['rec_boxes'] if 'rec_boxes' in result_obj else None

                        if debug:
                            logger.debug(f"Fallback extracted {len(rec_texts)} text boxes")

                        # Merge horizontally-aligned text boxes
                        # Use y_threshold=25 to handle slight vertical misalignment in receipts
                        if rec_boxes is not None:
                            merged_lines = merge_horizontal_text_boxes(
                                rec_texts, rec_scores, rec_boxes,
                                y_threshold=None,      # Auto-detect optimal threshold
                                auto_detect=True,      # Enable auto-detection
                                debug=debug
                            )
                        else:
                            merged_lines = [text.strip() for text in rec_texts if text.strip()]

                    except Exception as e:
                        logger.error(f"[PADDLE OCR] Error extracting text from fallback result: {e}")
                        if debug:
                            logger.debug(f"Full ocr_result structure: {ocr_result}")
                        raise
                    
                    # Use merged lines from fallback
                    if merged_lines:
                        raw_text = '\n'.join(merged_lines)
                        cleaned_text = text_corrector.clean_text(raw_text)
                        
                        if cleaned_text and len(cleaned_text.strip()) > 3:
                            results.append((cleaned_text, 999, "paddle_original"))
                            if debug:
                                logger.info(f"[PADDLE OCR] Original result: {cleaned_text[:50]}...")
                        
            except Exception as e:
                if debug:
                    logger.warning(f"[PADDLE OCR] Original image failed: {e}")
        
        if debug:
            logger.info(f"[PADDLE OCR] Image #{image_index} - Total successful extractions: {len(results)}")
            if results:
                best_result = max(results, key=lambda x: len(x[0]))
                logger.info(f"[PADDLE OCR] Best result preview: {best_result[0][:100]}...")
    
    except Exception as e:
        error_info = {
            "step": "Overall function failed",
            "error": str(e),
            "error_type": str(type(e)),
            "traceback": traceback.format_exc()
        }
        if debug and debug_info:
            debug_info["errors"].append(error_info)
            save_debug_info()
        logger.error(f"[PADDLE OCR] Critical error processing image #{image_index}: {e}")
    
    # Save debug info before returning
    if debug and debug_info:
        debug_info["results_count"] = len(results)
        debug_info["success"] = len(results) > 0
    save_debug_info()
    
    return results