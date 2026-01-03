"""
Contour Quality Scoring
======================
Scoring functions for receipt contour detection quality.
"""

import logging

import cv2
import numpy as np

logger = logging.getLogger(__name__)


class ContourScorer:
    """Handles contour quality scoring for receipt detection"""
    
    def __init__(self):
        pass
    
    def score_contour(self, contour, image_area, image_shape, gray_image):
        """
        Score contour for receipt detection - prioritizes white receipt areas over dark backgrounds.
        This fixes the wood grain detection issue by heavily favoring white areas.
        """
        area = cv2.contourArea(contour)
        if area < 10000:  # Must be substantial for receipt
            return 0.0
        
        # Get bounding rectangle
        x, y, w, h = cv2.boundingRect(contour)
        h_img, w_img = image_shape
        
        score = 0.0
        
        # 1. WHITENESS SCORE - CRITICAL for fixing wood grain / table detection
        mask = np.zeros((h_img, w_img), np.uint8)
        cv2.drawContours(mask, [contour], -1, (255,), -1)
        mean_intensity = cv2.mean(gray_image, mask=mask)[0]

        # STRENGTHENED: Much stronger whiteness bias to favor receipts over dark backgrounds
        if mean_intensity > 200:  # Very white (receipt paper)
            score += 100.0  # Doubled from 50
        elif mean_intensity > 170:  # Medium-high white
            score += 60.0  # New tier
        elif mean_intensity > 150:  # Medium white
            score += 30.0  # Increased from 20
        elif mean_intensity < 140:  # Dark areas (likely background/table)
            score -= 100.0  # Much heavier penalty (was -30)
        
        # 2. SIZE SCORE
        area_ratio = area / image_area
        if 0.3 <= area_ratio <= 0.8:  # Good size for receipt
            score += 30.0
        elif 0.1 <= area_ratio <= 0.9:  # Acceptable size
            score += 10.0
        else:
            score -= 20.0  # Too small or too large
        
        # 3. ASPECT RATIO SCORE (receipts are typically tall)
        aspect_ratio = h / w if w > 0 else 0
        if 1.2 <= aspect_ratio <= 4.0:  # Good receipt proportions
            score += 25.0
        elif 0.8 <= aspect_ratio <= 5.0:  # Acceptable proportions
            score += 10.0
        else:
            score -= 15.0
        
        # 4. POSITION SCORE (receipts usually centered)
        center_x, center_y = x + w//2, y + h//2
        img_center_x, img_center_y = w_img//2, h_img//2
        
        distance_from_center = np.sqrt((center_x - img_center_x)**2 + (center_y - img_center_y)**2)
        max_distance = np.sqrt(w_img**2 + h_img**2) / 2
        center_score = 15.0 * (1 - distance_from_center / max_distance)
        score += center_score
        
        # 5. SHAPE REGULARITY SCORE
        peri = cv2.arcLength(contour, True)
        if peri > 0:
            circularity = 4 * np.pi * area / (peri * peri)
            if 0.3 <= circularity <= 0.8:  # Rectangle-like shapes
                score += 10.0
        
        # 6. EDGE CONTRAST SCORE (receipts have high contrast with background)
        # Sample pixels around the contour edge
        edge_samples = self._sample_edge_contrast(gray_image, contour)
        if edge_samples > 40:  # High contrast edges
            score += 15.0
        elif edge_samples > 20:  # Medium contrast
            score += 5.0
        
        logger.debug(f"[CONTOUR SCORE] Area: {area}, Mean intensity: {mean_intensity:.1f}, "
                    f"Aspect: {aspect_ratio:.2f}, Score: {score:.1f}")
        
        return max(score, 0.0)
    
    def _sample_edge_contrast(self, gray_image, contour, sample_points=20):
        """Sample contrast around contour edges"""
        if len(contour) < sample_points:
            return 0
        
        # Sample points along the contour
        indices = np.linspace(0, len(contour)-1, sample_points, dtype=int)
        total_contrast = 0
        
        for idx in indices:
            point = contour[idx][0]
            x, y = point[0], point[1]
            
            # Ensure point is within image bounds
            h, w = gray_image.shape
            if 2 <= x < w-2 and 2 <= y < h-2:
                # Sample 3x3 region around point
                region = gray_image[y-1:y+2, x-1:x+2]
                if region.size > 0:
                    contrast = np.std(region)
                    total_contrast += contrast
        
        return total_contrast / sample_points if sample_points > 0 else 0


# Backward compatibility function
def score_receipt_contour(contour, image_area, image_shape, gray_image):
    """Backward compatibility wrapper for contour scoring"""
    scorer = ContourScorer()
    return scorer.score_contour(contour, image_area, image_shape, gray_image)