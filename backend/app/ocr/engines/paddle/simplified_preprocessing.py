"""
Simplified OCR Preprocessing - CLAHE Only
==========================================

Implements CLAHE-only preprocessing for Croatian receipt OCR.

Features:
- CLAHE enhancement only (no binarization)
- Quality scoring integration
- Croatian character optimization
- Debug image saving support
- Performance monitoring
"""

import cv2
import numpy as np
import logging
from typing import Optional, Callable, Dict, Any

logger = logging.getLogger(__name__)


class SimplifiedPreprocessing:
    """
    CLAHE-only preprocessing for Croatian receipt OCR.

    Uses CLAHE (Contrast Limited Adaptive Histogram Equalization) to enhance
    contrast without binarization. This preserves more text detail for PaddleOCR.
    """

    def __init__(self):
        """Initialize the simplified preprocessing system."""
        self.strategy_name = "clahe_only"
        logger.info("[SIMPLIFIED PREPROCESSING] Initialized with CLAHE-only strategy")

    def preprocess_for_ocr(self, image: np.ndarray, debug_save: Optional[Callable] = None) -> np.ndarray:
        """
        Apply CLAHE-only preprocessing for Croatian receipt OCR.

        Uses CLAHE (Contrast Limited Adaptive Histogram Equalization) to enhance
        contrast without binarization. This preserves text detail for PaddleOCR.

        Args:
            image: Input image to preprocess
            debug_save: Optional function to save debug images (name, image)

        Returns:
            Preprocessed image ready for OCR processing
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()

        # Save debug images if function provided
        if debug_save:
            debug_save("05_preprocessing_grayscale", gray)

        # Apply CLAHE enhancement
        # clipLimit=3.0: Increased for faint thermal receipt text (was 1.3)
        # tileGridSize=(4,4): Smaller grid for better local contrast (was 8x8)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(4, 4))
        enhanced = clahe.apply(gray)

        if debug_save:
            debug_save("06_preprocessing_clahe", enhanced)

        logger.debug(f"[SIMPLIFIED PREPROCESSING] Applied {self.strategy_name} to {image.shape} image")
        return enhanced

    def process_with_scoring(self, image: np.ndarray, ocr_engine, debug_save: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Process image with preprocessing and use PaddleOCR's confidence scores.

        This method combines preprocessing and OCR, using PaddleOCR's built-in
        confidence scoring instead of custom scoring algorithms.

        Args:
            image: Input image to process
            ocr_engine: OCR engine function to use
            debug_save: Optional debug image saving function

        Returns:
            Dictionary containing text, PaddleOCR confidence scores, and metadata
        """
        try:
            # 1. Apply CLAHE preprocessing
            preprocessed = self.preprocess_for_ocr(image, debug_save)

            # 2. Run OCR (PaddleOCR returns confidence scores automatically)
            ocr_results = ocr_engine(preprocessed)

            if not ocr_results or len(ocr_results) == 0:
                logger.warning("[SIMPLIFIED PREPROCESSING] OCR returned no results")
                return {
                    "success": False,
                    "text": "",
                    "confidence": 0.0,
                    "strategy": self.strategy_name,
                    "error": "No OCR results"
                }

            # Extract text and confidence from PaddleOCR results
            # PaddleOCR format: [[[bbox], (text, confidence)], ...]
            text_lines = []
            confidences = []

            if isinstance(ocr_results, list) and len(ocr_results) > 0:
                for result in ocr_results[0] if isinstance(ocr_results[0], list) else [ocr_results[0]]:
                    if isinstance(result, (list, tuple)) and len(result) >= 2:
                        text_data = result[1]
                        if isinstance(text_data, (list, tuple)) and len(text_data) >= 2:
                            text_lines.append(text_data[0])
                            confidences.append(float(text_data[1]))

            text = '\n'.join(text_lines) if text_lines else ""
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

            # Determine quality level based on PaddleOCR confidence
            if avg_confidence >= 0.9:
                quality_level = "excellent"
            elif avg_confidence >= 0.75:
                quality_level = "good"
            elif avg_confidence >= 0.5:
                quality_level = "fair"
            else:
                quality_level = "poor"

            logger.info(f"[SIMPLIFIED PREPROCESSING] OCR completed - PaddleOCR confidence: {avg_confidence:.3f} ({quality_level}), "
                       f"Text length: {len(text)}, Lines: {len(text_lines)}")

            return {
                "success": True,
                "text": text,
                "confidence": avg_confidence,
                "quality_level": quality_level,
                "strategy": self.strategy_name,
                "text_length": len(text),
                "line_count": len(text_lines),
                "croatian_chars": sum(1 for c in text if c in 'čćžšđČĆŽŠĐ'),
                "ocr_results": ocr_results
            }

        except Exception as e:
            logger.error(f"[SIMPLIFIED PREPROCESSING] Processing failed: {e}")
            return {
                "success": False,
                "text": "",
                "confidence": 0.0,
                "strategy": self.strategy_name,
                "error": str(e)
            }

    def get_strategy_info(self) -> Dict[str, Any]:
        """
        Get information about the preprocessing strategy being used.

        Returns:
            Dictionary with strategy details
        """
        return {
            "name": self.strategy_name,
            "description": "CLAHE-only preprocessing for Croatian receipts",
            "components": [
                "Grayscale conversion",
                "CLAHE enhancement (clipLimit=1.3, tileGridSize=8x8)"
            ],
            "optimized_for": [
                "Croatian characters (č, ć, ž, š, đ)",
                "Thermal receipt paper",
                "Store receipt formats",
                "Croatian retail chains"
            ],
            "performance": {
                "speed": "fast",
                "quality": "optimal",
                "reliability": "high"
            }
        }

    def assess_preprocessing_quality(self, original_image: np.ndarray,
                                   preprocessed_image: np.ndarray) -> Dict[str, Any]:
        """
        Assess the quality improvement from preprocessing.

        Args:
            original_image: Original input image
            preprocessed_image: Image after preprocessing

        Returns:
            Quality assessment metrics
        """
        try:
            # Convert to grayscale for comparison
            if len(original_image.shape) == 3:
                orig_gray = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
            else:
                orig_gray = original_image.copy()

            if len(preprocessed_image.shape) == 3:
                proc_gray = cv2.cvtColor(preprocessed_image, cv2.COLOR_BGR2GRAY)
            else:
                proc_gray = preprocessed_image.copy()

            # Calculate quality metrics
            orig_contrast = np.std(orig_gray)
            proc_contrast = np.std(proc_gray)

            orig_brightness = np.mean(orig_gray)
            proc_brightness = np.mean(proc_gray)

            # Sharpness using Laplacian variance
            orig_sharpness = cv2.Laplacian(orig_gray, cv2.CV_64F).var()
            proc_sharpness = cv2.Laplacian(proc_gray, cv2.CV_64F).var()

            return {
                "contrast_improvement": proc_contrast > orig_contrast,
                "brightness_optimization": abs(proc_brightness - 127) < abs(orig_brightness - 127),
                "sharpness_change": proc_sharpness / orig_sharpness if orig_sharpness > 0 else 1.0,
                "metrics": {
                    "original": {
                        "contrast": orig_contrast,
                        "brightness": orig_brightness,
                        "sharpness": orig_sharpness
                    },
                    "processed": {
                        "contrast": proc_contrast,
                        "brightness": proc_brightness,
                        "sharpness": proc_sharpness
                    }
                },
                "overall_improvement": (
                    proc_contrast > orig_contrast and
                    abs(proc_brightness - 127) < abs(orig_brightness - 127)
                )
            }

        except Exception as e:
            logger.error(f"[SIMPLIFIED PREPROCESSING] Quality assessment failed: {e}")
            return {
                "error": str(e),
                "overall_improvement": False
            }


# Global instance for easy access
simplified_preprocessor = SimplifiedPreprocessing()