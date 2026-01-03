"""
OCR Processing Pipeline
======================
Simplified pipeline for orchestrating the complete OCR workflow.
"""

from .simple_ocr_pipeline import SimpleOCRPipeline

# Backward compatibility alias
OCRPipeline = SimpleOCRPipeline

__all__ = ['SimpleOCRPipeline', 'OCRPipeline']
