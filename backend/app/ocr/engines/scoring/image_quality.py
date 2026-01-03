"""
Image Quality Scoring
====================
Scoring functions for image quality assessment for OCR processing.
"""

import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)


class ImageQualityScorer:
    """Handles image quality scoring for OCR processing"""
    
    def __init__(self):
        pass
    
    def score_image_quality(self, image: np.ndarray, debug_name: str = "") -> float:
        """
        Score image quality for OCR processing.
        Higher scores indicate better quality for text recognition.
        
        This prioritizes high-quality images with good sharpness and contrast.
        """
        if image is None or image.size == 0:
            return 0.0
            
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        score = 0.0
        
        # 1. SHARPNESS SCORE (Laplacian variance) - Key metric for text clarity
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        if laplacian_var > 1000:  # Very sharp
            sharpness_score = 50.0
        elif laplacian_var > 500:
            sharpness_score = 30.0
        elif laplacian_var > 100:
            sharpness_score = 15.0
        else:
            sharpness_score = 0.0
        
        score += sharpness_score
        
        # 2. CONTRAST SCORE (Standard deviation) - Text needs good contrast
        contrast = np.std(gray)
        if contrast > 60:  # High contrast (black text on white)
            contrast_score = 30.0
        elif contrast > 40:
            contrast_score = 20.0
        elif contrast > 25:
            contrast_score = 10.0
        else:
            contrast_score = 0.0
        
        score += contrast_score
        
        # 3. EDGE STRENGTH - Clean text has strong, defined edges
        edges = cv2.Canny(gray, 50, 150)
        edge_pixels = np.count_nonzero(edges)
        edge_density = edge_pixels / (gray.shape[0] * gray.shape[1])
        
        if 0.05 <= edge_density <= 0.25:  # Good amount of edges (text-like)
            edge_score = 20.0
        elif 0.02 <= edge_density <= 0.35:
            edge_score = 10.0
        else:
            edge_score = 0.0  # Too few or too many edges
        
        score += edge_score
        
        # 4. BRIGHTNESS DISTRIBUTION - Text should have bimodal distribution
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        hist_norm = hist.flatten() / hist.sum()
        
        # Look for peaks in dark (text) and light (background) regions
        dark_peak = np.max(hist_norm[0:100])   # Dark region (0-100)
        light_peak = np.max(hist_norm[150:256])  # Light region (150-255)
        
        if dark_peak > 0.02 and light_peak > 0.02:  # Both peaks present
            distribution_score = 15.0
        elif light_peak > 0.05:  # At least light background
            distribution_score = 8.0
        else:
            distribution_score = 0.0
        
        score += distribution_score
        
        # 5. NOISE ASSESSMENT - Less noise is better
        # Use morphological opening to detect noise
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        opened = cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel)
        noise_level = np.mean(np.abs(gray.astype(float) - opened.astype(float)))
        
        if noise_level < 2.0:  # Very clean
            noise_score = 10.0
        elif noise_level < 5.0:  # Acceptable
            noise_score = 5.0
        else:
            noise_score = 0.0  # Too noisy
        
        score += noise_score
        
        # 6. RESOLUTION/SIZE BONUS - Larger images generally better for OCR
        pixel_count = gray.shape[0] * gray.shape[1]
        if pixel_count > 1000000:  # > 1MP
            size_score = 5.0
        elif pixel_count > 500000:  # > 0.5MP
            size_score = 3.0
        elif pixel_count > 200000:  # > 0.2MP
            size_score = 1.0
        else:
            size_score = 0.0
        
        score += size_score
        
        # Debug logging
        if debug_name:
            logger.debug(f"[IMAGE QUALITY] {debug_name}: "
                        f"Sharpness={laplacian_var:.1f} ({sharpness_score:.1f}), "
                        f"Contrast={contrast:.1f} ({contrast_score:.1f}), "
                        f"Edges={edge_density:.3f} ({edge_score:.1f}), "
                        f"Total={score:.1f}")
        
        return score
    
    def is_image_suitable_for_ocr(self, image: np.ndarray, min_score: float = 50.0) -> bool:
        """Check if image quality is suitable for OCR processing"""
        score = self.score_image_quality(image)
        return score >= min_score
    
    def get_quality_metrics(self, image: np.ndarray) -> dict:
        """Get detailed quality metrics for an image"""
        if image is None or image.size == 0:
            return {}
        
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Calculate metrics
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        contrast = np.std(gray)
        
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.count_nonzero(edges) / (gray.shape[0] * gray.shape[1])
        
        brightness = np.mean(gray)
        
        return {
            'sharpness': laplacian_var,
            'contrast': contrast,
            'edge_density': edge_density,
            'brightness': brightness,
            'resolution': gray.shape,
            'pixel_count': gray.shape[0] * gray.shape[1],
            'quality_score': self.score_image_quality(image)
        }


# Backward compatibility function
def score_image_quality(image: np.ndarray, debug_name: str = "") -> float:
    """Backward compatibility wrapper for image quality scoring"""
    scorer = ImageQualityScorer()
    return scorer.score_image_quality(image, debug_name)