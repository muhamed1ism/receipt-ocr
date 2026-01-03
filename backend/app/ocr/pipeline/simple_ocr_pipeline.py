"""
Simple OCR Pipeline - Single Mode Processing
===========================================

Implements the ideal workflow:
Raw Image → Perfect Crop → Clean PaddleOCR → Parser → Results

Key Features:
- Single processing pipeline (no modes)
- Perfect geometric processing (98% crop accuracy)
- Clean image flow to PaddleOCR
- Minimal configuration and complexity
- 3-5 second processing target
"""

import logging
import time
import os
import cv2
import numpy as np
from typing import Dict, Any

# Core components
from app.ocr.processor.core import ReceiptProcessor
from app.ocr.parsing.receipt_parser import ReceiptParser
from app.ocr.engines.paddle import run_ocr_on_image
from app.ocr.engines.paddle.simplified_preprocessing import SimplifiedPreprocessing

# Optional debug modules - not required for production
try:
    from app.utils.unified_debug_manager import get_global_debug_manager

    DEBUG_MODULES_AVAILABLE = True
except ImportError:
    DEBUG_MODULES_AVAILABLE = False
    get_global_debug_manager = None
    save_ocr_debug_session = None

logger = logging.getLogger(__name__)


class SimpleOCRPipeline:
    """
    Simplified OCR pipeline implementing the ideal workflow.

    No modes, no variants, no consensus - just optimal processing.
    """

    def __init__(self, debug: bool = True):
        self.debug = debug

        # Configuration not needed for simplified single-mode pipeline
        self.config = None

        # Core components
        self.geometric_processor = ReceiptProcessor(debug=debug)
        self.parser = ReceiptParser()
        self.simplified_preprocessor = SimplifiedPreprocessing()

        # Get unified debug manager for session-based debugging (if available)
        # Always initialize debug manager so debug_utility can work on-demand
        if DEBUG_MODULES_AVAILABLE and get_global_debug_manager:
            self.debug_manager = get_global_debug_manager()
        else:
            self.debug_manager = None

        logger.info(
            "[SIMPLE PIPELINE] Initialized with simplified single-mode processing, quality scoring integration, and session-based debugging"
        )

    def process_image(
        self,
        image: np.ndarray,
        image_filename: str = "uploaded_image.jpg",
        debug_utility: bool = False,
        quick_mode: bool = False,
        enable_parser_debug: bool = False,
    ) -> Dict[str, Any]:
        """
        Process receipt image using the simplified workflow with integrated quality scoring.

        Args:
            image: Input receipt image
            image_filename: Original filename for debugging
            debug_utility: Save debug files to session and use enhanced scoring
            quick_mode: Skip parser, only do OCR (much faster)
            enable_parser_debug: Enable detailed parser debugging

        Returns:
            Dict containing parsed receipt data and metadata with quality metrics
        """
        start_time = time.time()

        # debug_utility enabled - use enhanced scoring and session debugging
        if debug_utility:
            logger.info(
                "[SIMPLE PIPELINE] Debug utility enabled - enhanced scoring and session debugging active"
            )

        # Start debug session if debug_utility enabled
        debug_session = None
        if self.debug_manager and debug_utility:
            if quick_mode:
                session_mode = "simplified_quick_ocr"
            else:
                session_mode = "simplified_full_processing"

            debug_session = self.debug_manager.start_session(
                mode=session_mode,
                debug_level="full",  # Always full when enabled
                image=image,
            )

        try:
            logger.info(f"[SIMPLE PIPELINE] Starting processing: {image_filename}")

            if debug_session:
                debug_session.set_stage("geometric_processing")
                debug_session.capture_resource_snapshot("pipeline_start")

            # Step 1: Perfect Geometric Processing (98% crop accuracy)
            logger.info("[SIMPLE PIPELINE] Step 1: Perfect geometric processing")
            if debug_session:
                debug_session.capture_resource_snapshot("geometric_processing_start")
                # Ensure debug manager has the active session set for geometric processor
                if self.debug_manager:
                    self.debug_manager.current_session = debug_session
                # Pass debug session to geometric processor for image saving
                self.geometric_processor.debug_session = debug_session
            processed_images, status, processing_info = (
                self.geometric_processor.process_receipt(image)
            )
            if debug_session:
                debug_session.capture_resource_snapshot("geometric_processing_end")

            if not processed_images:
                raise ValueError(f"Geometric processing failed: {status}")

            # Get the perfectly cropped, clean image
            clean_cropped_image = processed_images[0]
            logger.info(f"[SIMPLE PIPELINE] Geometric processing: {status}")

            # Save cropped image to session and capture image quality metrics
            if debug_session:
                debug_session.save_visual_debug(
                    "geometric_final_cropped",
                    clean_cropped_image,
                    "geometric_result.png",
                )
                debug_session.add_image_quality_metrics(
                    clean_cropped_image, "geometric_result"
                )
                debug_session.set_stage("ocr_processing")

            # Step 2: OCR Processing with Integrated Quality Scoring
            logger.info(
                "[SIMPLE PIPELINE] Step 2: OCR processing with integrated quality scoring"
            )
            if debug_session:
                debug_session.capture_resource_snapshot("ocr_processing_start")

            # Create debug callback for saving preprocessing images
            debug_save_callback = None
            if debug_session:

                def save_preprocessing_image(name, image):
                    """Callback to save preprocessing images to debug session"""
                    debug_session.save_visual_debug(name, image, f"{name}.png")

                debug_save_callback = save_preprocessing_image

            # Use run_ocr_on_image with CLAHE-only preprocessing
            # This uses the proven OCR workflow with auto country detection
            # Croatian corrections are ONLY applied to Croatian receipts (not Bosnian)
            # When debug_utility is enabled, request raw OCR result for debug session saving
            if debug_utility:
                ocr_results, raw_ocr_result = run_ocr_on_image(
                    clean_cropped_image,
                    lang="hr",  # Croatian/Bosnian Latin script support
                    debug=self.debug,
                    auto_detect_country=True,  # Auto-detect and skip Croatian corrections for Bosnian
                    return_raw_result=True,  # Get raw OCR result for debug session saving
                    debug_save_callback=debug_save_callback,  # Save preprocessing steps
                )
            else:
                ocr_results = run_ocr_on_image(
                    clean_cropped_image,
                    lang="hr",  # Croatian/Bosnian Latin script support
                    debug=self.debug,
                    auto_detect_country=True,  # Auto-detect and skip Croatian corrections for Bosnian
                    debug_save_callback=debug_save_callback,  # Save preprocessing steps
                )
                raw_ocr_result = None

            if debug_session:
                debug_session.capture_resource_snapshot("ocr_processing_end")

            if not ocr_results:
                raise ValueError("OCR processing returned no results")

            # Extract text from OCR results (standard format)
            # ocr_results is a list of tuples: [(full_text, config_index, config_name), ...]
            # We need to split the full_text into individual lines for the parser
            text_lines = []
            for result in ocr_results:
                if result[0].strip():
                    # Split the text into individual lines
                    lines = result[0].split("\n")
                    text_lines.extend([line.strip() for line in lines if line.strip()])

            if not text_lines:
                raise ValueError("OCR processing returned empty text")

            logger.info(
                f"[SIMPLE PIPELINE] OCR extracted {len(text_lines)} text lines using optimal strategy"
            )

            # Create raw_text for compatibility (but keep text_lines as primary)
            raw_text = "\n".join(text_lines)

            # Calculate quality metrics using the scoring system
            from app.ocr.engines.scoring.text_scoring import score_ocr_text

            quality_score = score_ocr_text(raw_text)

            # Determine quality level
            if quality_score >= 3.0:
                quality_level = "excellent"
            elif quality_score >= 2.0:
                quality_level = "good"
            elif quality_score >= 1.0:
                quality_level = "fair"
            else:
                quality_level = "poor"

            # Count Croatian characters
            croatian_chars = sum(1 for c in raw_text if c in "čćžšđČĆŽŠĐ")

            logger.info(
                f"[SIMPLE PIPELINE] OCR quality: {quality_level} (score: {quality_score:.3f}), Croatian chars detected: {croatian_chars}"
            )

            # Save OCR text to session and capture OCR analytics
            if debug_session:
                debug_session.save_text_data(
                    "ocr_raw_text", raw_text, "ocr_extracted_text.txt"
                )
                debug_session.add_ocr_analytics("PaddleOCR", ocr_results, None)
                # Save quality metrics
                debug_session.save_json_data(
                    {
                        "ocr_quality_metrics": {
                            "quality_score": quality_score,
                            "quality_level": quality_level,
                            "strategy": "optimal",
                            "text_length": len(raw_text),
                            "croatian_chars": croatian_chars,
                        }
                    },
                    "ocr_quality_analysis.json",
                )
                debug_session.set_stage("parsing")

            # Step 3: Parsing (skip if quick mode)
            if quick_mode:
                logger.info("[SIMPLE PIPELINE] Step 3: Skipped (quick mode - OCR only)")
                parsed_receipt = {
                    "store": "Quick OCR Mode",
                    "items": [],
                    "total": None,
                    "raw_text": raw_text,
                    "text_lines": text_lines,
                    "quick_mode": True,
                }
            else:
                logger.info("[SIMPLE PIPELINE] Step 3: Universal parsing")
                if debug_session:
                    debug_session.capture_resource_snapshot("parsing_start")
                parsed_receipt = self.parser.parse_receipt(
                    text_lines, log_debug=enable_parser_debug
                )
                if debug_session:
                    debug_session.capture_resource_snapshot("parsing_end")

            # Calculate processing time
            processing_time = time.time() - start_time

            # Save parsing results to session and capture final resource snapshot
            if debug_session:
                debug_session.capture_resource_snapshot("pipeline_complete")
                debug_session.save_json_data(
                    {
                        "parsed_receipt": parsed_receipt,
                        "processing_metadata": {
                            "processing_time": processing_time,
                            "text_lines_count": len(text_lines),
                            "geometric_status": status,
                            "ocr_quality_score": quality_score,
                            "ocr_quality_level": quality_level,
                            "croatian_chars_detected": croatian_chars,
                        },
                    },
                    "parsing_results.json",
                )

            # Save OCR boxes visualization and detailed data to debug session
            if debug_session and raw_ocr_result:
                try:
                    # Save boxes visualization
                    debug_session.save_boxes_visualization(
                        clean_cropped_image, raw_ocr_result
                    )

                    # Extract raw OCR text (before corrections)
                    raw_text_lines = []
                    ocr_data = []
                    for idx, line in enumerate(raw_ocr_result):
                        box = line[0]
                        text, confidence = line[1]
                        raw_text_lines.append(text)
                        ocr_data.append(
                            {
                                "index": idx,
                                "text": text,
                                "confidence": float(confidence),
                                "box": [[float(p[0]), float(p[1])] for p in box],
                            }
                        )

                    raw_ocr_text = "\n".join(raw_text_lines)

                    # Save raw OCR text (before corrections)
                    debug_session.save_text_data(
                        "ocr_raw_text", raw_ocr_text, "09_ocr_raw_text.txt"
                    )

                    # Save processed text (after corrections, what parser receives)
                    debug_session.save_text_data(
                        "ocr_processed_text", raw_text, "10_ocr_processed_text.txt"
                    )

                    # Save text corrections if different
                    if raw_ocr_text != raw_text:
                        differences = []
                        raw_lines = raw_ocr_text.split("\n")
                        proc_lines = raw_text.split("\n")
                        for i, (raw_line, proc_line) in enumerate(
                            zip(raw_lines, proc_lines)
                        ):
                            if raw_line != proc_line:
                                differences.append(
                                    {"line": i, "raw": raw_line, "processed": proc_line}
                                )
                        if differences:
                            debug_session.save_json_data(
                                {
                                    "total_changes": len(differences),
                                    "changes": differences,
                                },
                                "11_text_corrections_applied.json",
                            )

                    # Save OCR data with bounding boxes
                    debug_session.save_json_data(
                        {
                            "total_detections": len(raw_ocr_result),
                            "detections": ocr_data,
                        },
                        "12_ocr_raw_data.json",
                    )

                    # Save detailed quality metrics
                    avg_confidence = (
                        sum(line[1][1] for line in raw_ocr_result) / len(raw_ocr_result)
                        if raw_ocr_result
                        else 0
                    )
                    debug_session.save_json_data(
                        {
                            "total_detections": len(raw_ocr_result),
                            "average_confidence": float(avg_confidence),
                            "high_confidence_count": sum(
                                1 for line in raw_ocr_result if line[1][1] > 0.9
                            ),
                            "low_confidence_count": sum(
                                1 for line in raw_ocr_result if line[1][1] < 0.7
                            ),
                            "total_characters": len(raw_ocr_text),
                            "croatian_special_chars": croatian_chars,
                            "text_lines": len(raw_text_lines),
                        },
                        "13_ocr_quality_metrics.json",
                    )

                    logger.info(
                        f"[SIMPLE PIPELINE] Saved OCR boxes and detailed text analysis to debug session"
                    )
                except Exception as e:
                    logger.error(
                        f"[SIMPLE PIPELINE] Failed to save OCR debug data: {e}"
                    )

            # Create result
            result = {
                "success": True,
                "processing_method": "simplified_single_mode",
                "processing_time": processing_time,
                "geometric_status": status,
                "ocr_lines_count": len(text_lines),
                "receipt": parsed_receipt,
                "text_lines": text_lines,
                "raw_text": raw_text,
                "quality_metrics": {
                    "ocr_score": quality_score,
                    "quality_level": quality_level,
                    "croatian_chars_detected": croatian_chars,
                    "text_length": len(raw_text),
                    "preprocessing_strategy": "optimal_gentle_otsu",
                },
                "metadata": {
                    "workflow": "Raw Image -> Perfect Crop -> Simplified Preprocessing with Scoring -> Clean PaddleOCR -> Parser -> Results",
                    "crop_accuracy_target": 98.0,
                    "preprocessing_approach": "single_optimal_strategy_with_scoring",
                    "fake_strategy_elimination": True,
                    "scoring_system_integrated": True,
                    "croatian_optimization": True,
                    "enhanced_scoring": debug_utility,
                    "debug_utility_enabled": debug_utility,
                    "debug_session": debug_session.session_id
                    if debug_session
                    else None,
                },
            }

            # Finish debug session
            if debug_session:
                self.debug_manager.finish_session(debug_session)

            logger.info(
                f"[SIMPLE PIPELINE] SUCCESS! Processing completed in {processing_time:.2f}s"
            )
            return result

        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"[SIMPLE PIPELINE] ERROR after {processing_time:.2f}s: {e}")

            # Log error to debug session
            if debug_session:
                self.debug_manager.communicate_problem(
                    problem_type="processing_failed",
                    description=f"Processing failed: {str(e)}",
                    severity="error",
                    suggested_action="Check input image quality and format",
                )
                self.debug_manager.finish_session(debug_session)

            return {
                "success": False,
                "error": str(e),
                "processing_time": processing_time,
                "processing_method": "simplified_single_mode_failed",
                "debug_session": debug_session.session_id if debug_session else None,
            }

    def process_single_receipt(
        self, image_path: str, endpoint: str = "ocr", image_filename: str = None
    ) -> Dict[str, Any]:
        """
        Process receipt from file path - backward compatibility method.

        Args:
            image_path: Path to the receipt image file
            endpoint: Processing endpoint (for debugging info)
            image_filename: Original filename for debugging (defaults to basename of image_path)

        Returns:
            Dict containing parsed receipt data and metadata
        """
        try:
            # Load image from file
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not load image: {image_path}")

            # Extract filename if not provided
            if image_filename is None:
                image_filename = os.path.basename(image_path)

            logger.info(
                f"[SIMPLE PIPELINE] Processing file: {image_path} for endpoint: {endpoint}"
            )

            # Process using the main image processing method
            result = self.process_image(image, image_filename)

            # Add endpoint info to metadata
            if "metadata" in result:
                result["metadata"]["endpoint"] = endpoint
                result["metadata"]["source_file"] = image_path

            return result

        except Exception as e:
            logger.error(
                f"[SIMPLE PIPELINE] File processing error for {image_path}: {e}"
            )
            return {
                "success": False,
                "error": f"File processing failed: {str(e)}",
                "processing_method": "simplified_single_mode_file_failed",
                "source_file": image_path,
                "endpoint": endpoint,
            }

    def get_processing_info(self) -> Dict[str, Any]:
        """Get information about the simplified pipeline."""
        return {
            "pipeline_type": "simplified_single_mode",
            "workflow": "Raw Image -> Perfect Crop -> Simplified Preprocessing with Scoring -> Clean PaddleOCR -> Parser -> Results",
            "target_processing_time": "3-5 seconds",
            "target_crop_accuracy": "98%",
            "preprocessing_strategy": "optimal_gentle_otsu (single strategy, no fake selection)",
            "quality_scoring": "integrated Croatian-optimized OCR scoring",
            "croatian_optimization": "character bonus system (č, ć, ž, š, đ)",
            "parser": "universal (Croatian optimized)",
            "modes": "single optimal mode only",
            "complexity": "minimal with intelligent quality assessment",
            "fake_strategies_eliminated": True,
            "scoring_features": [
                "Character count and line detection",
                "Valid character ratio analysis",
                "Croatian character bonus system",
                "Quality level classification (excellent/good/fair/poor)",
                "Enhanced scoring mode for deep analysis",
            ],
        }


# Backward compatibility alias
UnifiedOCRPipeline = SimpleOCRPipeline

