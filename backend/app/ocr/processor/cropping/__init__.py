"""
Receipt Cropping Modules
=======================
Specialized modules for different aspects of receipt cropping.
"""

from .perspective_transformer import PerspectiveTransformer
from .contour_validator import CroppingContourValidator

__all__ = [
    'PerspectiveTransformer',
    'CroppingContourValidator'
]