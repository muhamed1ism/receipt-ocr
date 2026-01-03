"""
Preprocessing Strategy Selector
===============================
Analyzes image quality to determine optimal preprocessing strategies.
Different from scoring/image_quality.py which scores processed images.
"""

import cv2
import numpy as np


class PreprocessingSelector:
    """Selects optimal preprocessing strategies based on image quality assessment"""
    
    @staticmethod
    def assess_image_quality(image: np.ndarray) -> dict:
        """Assess image quality to choose optimal preprocessing."""
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Calculate quality metrics
        mean_brightness = np.mean(gray)
        contrast = np.std(gray)
        
        # Laplacian variance for sharpness assessment
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # Quality flags
        is_dark = mean_brightness < 100
        is_low_contrast = contrast < 40
        is_blurry = laplacian_var < 100
        
        return {
            'mean_brightness': mean_brightness,
            'contrast': contrast,
            'sharpness': laplacian_var,
            'is_dark': is_dark,
            'is_low_contrast': is_low_contrast,
            'is_blurry': is_blurry
        }
    
    @staticmethod
    def select_preprocessing_strategies(quality_metrics: dict) -> list:
        """Select optimal preprocessing strategies based on quality metrics"""
        strategies = ["minimal"]  # Always start with minimal
        
        # Add additional strategies based on image quality issues
        if quality_metrics['is_dark'] or quality_metrics['is_low_contrast']:
            strategies.extend(["high_contrast", "gentle_otsu"])
        
        if quality_metrics['is_blurry']:
            strategies.append("sharp")
            
        # Always include very gentle enhancement as backup
        if "very_gentle_clahe" not in strategies:
            strategies.append("very_gentle_clahe")
            
        return strategies