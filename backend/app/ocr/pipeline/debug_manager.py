"""
OCR Debug Manager
================
Handles debug information saving and logging for OCR pipeline.
"""

import os
import cv2
import logging
from typing import List, Tuple, Any
from app.core.constants import DEBUG_IMAGE_DIR, DEBUG_SAVE_FILES

logger = logging.getLogger(__name__)


class DebugManager:
    """Manages debug output for OCR pipeline"""
    
    def __init__(self, debug_dir: str = DEBUG_IMAGE_DIR):
        self.debug_dir = debug_dir
        os.makedirs(self.debug_dir, exist_ok=True)
    
    def save_debug_info(self, processed_images: List[Any], best_info: Tuple,
                       best_text: str, best_score: float):
        """Save debug information for analysis (only if DEBUG_SAVE_FILES=True)."""
        # Only save if DEBUG_SAVE_FILES environment variable is True
        if not DEBUG_SAVE_FILES:
            logger.debug("[DEBUG] Skipping debug file save (DEBUG_SAVE_FILES=False)")
            return

        try:
            # Save the best OCR source image
            if best_info[0].startswith("image_"):
                index = int(best_info[0].split("_")[-1])
                if 0 <= index < len(processed_images):
                    best_img = processed_images[index]
                    debug_path = os.path.join(self.debug_dir, "final_best_ocr_source.png")
                    cv2.imwrite(debug_path, best_img)
                    logger.debug(f"[DEBUG] Saved best OCR source image: {debug_path}")

            # Save OCR text result
            result_path = os.path.join(self.debug_dir, "best_ocr_result.txt")
            with open(result_path, 'w', encoding='utf-8') as f:
                f.write(f"OCR Score: {best_score}\n")
                f.write(f"Config: {best_info[2]}\n")
                f.write(f"Source: {best_info[0]}\n")
                f.write(f"Text Length: {len(best_text)} characters\n")
                f.write(f"Lines: {len(best_text.splitlines())}\n")
                f.write("\n" + "="*50 + "\n")
                f.write("EXTRACTED TEXT:\n")
                f.write("="*50 + "\n")
                f.write(best_text)
            logger.debug(f"[DEBUG] Saved OCR text result: {result_path}")

        except Exception as e:
            logger.warning(f"[DEBUG] Could not save debug info: {e}")
    
    def log_processing_step(self, step_name: str, details: str, success: bool = True):
        """Log a processing step with details"""
        status = "SUCCESS" if success else "FAILED"
        logger.info(f"[{step_name.upper()}] {status} - {details}")
    
    def log_ocr_results(self, image_count: int, best_score: float, 
                       text_length: int, all_attempts: int):
        """Log OCR processing results summary"""
        logger.info(f"[OCR SUMMARY] Processed {image_count} images, "
                   f"{all_attempts} total attempts, "
                   f"best score: {best_score:.2f}, "
                   f"text length: {text_length} chars")