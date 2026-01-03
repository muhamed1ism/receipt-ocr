"""
OCR Engines Module
==================
Different OCR engines and their specialized implementations.
"""

from .paddle.paddle_engine import PaddleOCREngine
from .paddle import run_ocr_on_image
from .scoring.text_scoring import score_ocr_text
from .scoring.contour_scoring import score_receipt_contour

__all__ = ['PaddleOCREngine', 'run_ocr_on_image', 'score_ocr_text', 'score_receipt_contour']