"""
OCR Scoring Modules
==================
Different scoring strategies for OCR quality assessment.
"""

from .text_scoring import OCRTextScorer
from .contour_scoring import ContourScorer
from .receipt_scoring import ReceiptScorer

# Maintain backward compatibility with existing imports
from .text_scoring import score_ocr_text
from .contour_scoring import score_receipt_contour
from .receipt_scoring import score_croatian_receipt_quality

__all__ = [
    'OCRTextScorer',
    'ContourScorer',
    'ReceiptScorer',
    'score_ocr_text',
    'score_receipt_contour',
    'score_croatian_receipt_quality'
]