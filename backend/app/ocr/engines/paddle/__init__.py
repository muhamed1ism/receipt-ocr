"""
PaddleOCR Engine Implementation
==============================
Modular PaddleOCR engine with specialized components.

Module Structure:
- paddle_engine.py: Core PaddleOCR wrapper
- ocr_execution.py: OCR execution and result processing
- text_merging.py: Text box spatial analysis and merging
- text_correction.py: Croatian text correction
- simplified_preprocessing.py: CLAHE-only preprocessing
"""

from .paddle_engine import PaddleOCREngine
from .text_correction import CroatianTextCorrector
from .ocr_execution import run_ocr_on_image, ensure_rgb_image
from .simplified_preprocessing import SimplifiedPreprocessing
from .text_merging import merge_horizontal_text_boxes, calculate_adaptive_threshold

__all__ = [
    'PaddleOCREngine',
    'CroatianTextCorrector',
    'run_ocr_on_image',  # Main entry point
    'SimplifiedPreprocessing',
    'merge_horizontal_text_boxes',
    'calculate_adaptive_threshold',
    'ensure_rgb_image',
]