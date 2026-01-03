"""
Fallback Contour Detection
=========================
Enhanced fallback methods for receipt detection when standard methods fail.
"""

import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)


class FallbackContourDetection:
    """Enhanced fallback for full receipt detection"""
    
    def __init__(self, debug=False):
        self.debug = debug
    
    def enhanced_fallback_detection(self, image):
        """Enhanced fallback for full receipt detection"""
        logger.info("[FALLBACK] Using enhanced fallback detection")
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        h, w = gray.shape[:2]
        
        # Strategy 1: Look for the largest bright rectangular region
        # Assume receipt is the brightest part of the image
        
        # Create mask for bright areas
        bright_thresh = int(np.percentile(gray, 85))  # Top 15% of brightness
        _, bright_mask = cv2.threshold(gray, bright_thresh, 255, cv2.THRESH_BINARY)
        
        # Find the largest bright contour
        contours, _ = cv2.findContours(bright_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            # Find largest contour by area
            largest_contour = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(largest_contour)
            
            # Must be substantial part of image
            if area > (h * w * 0.3):
                # Convert to rectangle
                peri = cv2.arcLength(largest_contour, True)
                approx = cv2.approxPolyDP(largest_contour, 0.05 * peri, True)
                
                if len(approx) >= 4:
                    # Take first 4 points if more than 4
                    return approx[:4]
        
        # Strategy 2: Edge-based with more aggressive parameters
        blurred = cv2.GaussianBlur(gray, (7, 7), 0)
        edges = cv2.Canny(blurred, 20, 100)
        
        # Dilate edges to connect gaps
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        dilated = cv2.dilate(edges, kernel, iterations=3)
        
        # Find contours
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in sorted(contours, key=cv2.contourArea, reverse=True):
            area = cv2.contourArea(contour)
            if area < (h * w * 0.2):  # Too small
                continue
            
            # Try to approximate to rectangle
            peri = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.08 * peri, True)
            
            if len(approx) == 4:
                return approx
        
        # Strategy 3: Use image borders as fallback (assume full image is receipt)
        logger.warning("[FALLBACK] Using full image bounds")
        border_margin = 20  # Small margin from edges
        
        fallback_contour = np.array([
            [[border_margin, border_margin]],
            [[w - border_margin, border_margin]], 
            [[w - border_margin, h - border_margin]],
            [[border_margin, h - border_margin]]
        ], dtype=np.int32)
        
        return fallback_contour
    
    def find_largest_rectangular_contour(self, binary_image, min_area_ratio=0.1):
        """Find the largest contour that can be approximated as a rectangle"""
        contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return None
        
        h, w = binary_image.shape[:2]
        image_area = h * w
        
        best_contour = None
        best_area = 0
        
        for contour in contours:
            area = cv2.contourArea(contour)
            
            # Must be significant size
            if area < image_area * min_area_ratio:
                continue
            
            # Try to approximate as rectangle
            peri = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
            
            if len(approx) == 4 and area > best_area:
                best_contour = approx
                best_area = area
        
        return best_contour