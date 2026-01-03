"""
Contour Detection Methods
========================
Different strategies for detecting receipt contours in images.
"""

from .binary_methods import BinaryContourMethods
from .fallback_detection import FallbackContourDetection
from .contour_validator import ContourValidator

__all__ = [
    'BinaryContourMethods',
    'FallbackContourDetection', 
    'ContourValidator'
]