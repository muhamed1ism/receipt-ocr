"""
OCR Pipeline Orchestrator (MAIN PIPELINE)
=========================================
Main orchestration logic for the complete OCR processing pipeline.

PIPELINE HIERARCHY:
    ocr_service.py (API Entry)
        ↓
    pipeline/ocr_orchestrator.py (THIS FILE - MAIN PIPELINE)
        ↓
    ┌─────────────────────────┬──────────────────────────────┐
    │ processor/core.py       │ pipeline/processing_coord.py │
    │ (Image Processing)      │ (Multi-Strategy Coordination) │
    └─────────────────────────┴──────────────────────────────┘
        ↓                              ↓
    contour.py + cropper.py     engines/paddle/paddle_coord.py
    (Boundary Detection)        (PaddleOCR Engine Specific)

PURPOSE:
- MAIN entry point for all OCR processing
- Coordinates image processing and text extraction
- Manages the complete pipeline from image → structured data
- Handles fallback strategies and error recovery
- Different from engines/paddle/paddle_coordinator.py which is engine-specific
"""

import os
import cv2
import logging
from typing import Any, Dict
from app.ocr.processor.core import ReceiptProcessor
from app.ocr.parsing.receipt_parser import ReceiptParser
from .processing_coordinator import ProcessingCoordinator
from .debug_manager import DebugManager

logger = logging.getLogger(__name__)


class OCRPipeline:
    """Main OCR processing pipeline orchestrator"""
    
    def __init__(self, debug: bool = True, use_fast: bool = False):
        self.debug = debug
        self.use_fast = use_fast
        self.processor = ReceiptProcessor(debug=debug)
        self.parser = ReceiptParser()
        self.coordinator = ProcessingCoordinator(debug=debug)
        self.debug_manager = DebugManager() if debug else None
        
        logger.info("OCR Pipeline initialized with PaddleOCR engine")

    def process_single_receipt(self, image_path: str) -> Dict[str, Any]:
        """
        Main processing function - maintains same interface as your original.
        Enhanced with better error handling and processing pipeline.
        """
        try:
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError(f"Could not load image: {image_path}")

            logger.info(f"[MAIN] Processing {image_path}")
            
            # Step 1: Process image with improved processor
            processed_images, status, processing_info = self.processor.process_receipt(img)
            
            if not processed_images:
                logger.error(f"[MAIN] No processed images returned from processor")
                return {
                    "success": False,
                    "error": "Image processing failed - no processed images",
                    "image_path": image_path,
                    "process_status": status
                }

            # Step 2: Run OCR processing through coordinator
            best_text, best_score, best_info, all_ocr_attempts = self.coordinator.run_paddleocr_processing(processed_images)
            logger.info(f"[OCR] PaddleOCR processing on {len(processed_images)} images")

            # Step 3: Validate OCR results
            if not best_text or len(best_text.strip()) < 15:
                logger.warning(f"[OCR] Insufficient text extracted from {len(processed_images)} images")
                logger.warning(f"[OCR] Tried {len(all_ocr_attempts)} OCR configurations")
                
                # Try to provide more helpful error info
                if all_ocr_attempts:
                    longest_text = max(all_ocr_attempts, key=lambda x: len(x[0]))[0]
                    logger.info(f"[OCR] Longest text found: '{longest_text[:100]}...' ({len(longest_text)} chars)")
                
                return {
                    "success": False,
                    "error": f"OCR extraction failed - insufficient text (best: {len(best_text)} chars)",
                    "image_path": image_path,
                    "attempts": len(all_ocr_attempts),
                    "process_status": status,
                    "best_text_preview": best_text[:200] if best_text else ""
                }

            # Step 4: Parse the extracted text
            logger.info(f"[PARSER] Parsing {len(best_text)} characters with confidence {best_score:.1f}")
            
            lines = best_text.strip().split('\n')
            parsed_receipt = self.parser.parse_receipt(lines, log_debug=self.debug)
            
            # Step 5: Save debug information if enabled
            if self.debug and self.debug_manager:
                self.debug_manager.save_debug_info(processed_images, best_info, best_text, best_score)
                self.debug_manager.log_ocr_results(
                    len(processed_images), best_score, len(best_text), len(all_ocr_attempts)
                )

            # Step 6: Build final result
            result = {
                "success": True,
                "image_path": image_path,
                "ocr_score": best_score,
                "text_length": len(best_text),
                "lines_count": len(lines),
                "attempts": len(all_ocr_attempts),
                "best_config": best_info[2],
                "process_status": status,
                "receipt": parsed_receipt
            }
            
            if self.debug:
                result["raw_text"] = best_text
                result["processing_info"] = processing_info
            
            logger.info(f"[MAIN] Successfully processed {image_path}: "
                       f"extracted {len(best_text)} chars, "
                       f"parsed {len(parsed_receipt.get('items', []))} items")
            
            return result
        
        except Exception as e:
            logger.error(f"[MAIN] Critical error processing {image_path}: {str(e)}")
            return {
                "success": False,
                "error": f"Processing failed: {str(e)}",
                "image_path": image_path
            }

    def process_image_array(self, image: Any) -> Dict[str, Any]:
        """Process image from numpy array or similar format"""
        try:
            logger.info("[MAIN] Processing image from array")
            
            # Step 1: Process image
            processed_images, status, processing_info = self.processor.process_receipt(image)
            
            if not processed_images:
                return {
                    "success": False,
                    "error": "Image processing failed - no processed images",
                    "process_status": status
                }

            # Step 2: Run OCR processing
            best_text, best_score, best_info, all_ocr_attempts = self.coordinator.run_paddleocr_processing(processed_images)

            # Step 3: Validate and parse
            if not best_text or len(best_text.strip()) < 15:
                return {
                    "success": False,
                    "error": f"OCR extraction failed - insufficient text (best: {len(best_text)} chars)",
                    "attempts": len(all_ocr_attempts),
                    "process_status": status
                }

            lines = best_text.strip().split('\n')
            parsed_receipt = self.parser.parse_receipt(lines, log_debug=self.debug)
            
            # Step 4: Debug output
            if self.debug and self.debug_manager:
                self.debug_manager.save_debug_info(processed_images, best_info, best_text, best_score)
            
            return {
                "success": True,
                "ocr_score": best_score,
                "text_length": len(best_text),
                "lines_count": len(lines),
                "receipt": parsed_receipt
            }
            
        except Exception as e:
            logger.error(f"[MAIN] Critical error processing image array: {str(e)}")
            return {
                "success": False,
                "error": f"Processing failed: {str(e)}"
            }