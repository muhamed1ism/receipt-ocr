"""
Contour Validation Methods
=========================
Methods for validating and converting contours for receipt detection.
"""

import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)


class ContourValidator:
    """Handles contour validation and conversion"""
    
    def __init__(self):
        pass
    
    def validate_full_receipt_contour(self, contour, image_shape):
        """Validate that contour represents a full receipt"""
        
        if contour is None or len(contour) != 4:
            return False
        
        # Check area
        area = cv2.contourArea(contour)
        image_area = image_shape[0] * image_shape[1]
        area_ratio = area / image_area

        if not (0.1 <= area_ratio <= 0.95):  # Allow smaller receipts (was 0.2-0.9)
            logger.debug(f"[VALIDATE] Area ratio {area_ratio:.3f} out of range (0.1-0.95)")
            return False
        
        # Check aspect ratio
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = h / w if w > 0 else 0
        
        if not (1.0 <= aspect_ratio <= 5.0):  # Must be reasonable
            logger.debug(f"[VALIDATE] Aspect ratio {aspect_ratio:.2f} out of range")
            return False
        
        return True
    
    def contour_to_rectangle(self, contour):
        """Convert any contour to best 4-point rectangle"""
        
        # Method 1: Polygon approximation
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
        
        if len(approx) == 4:
            return approx
        
        # Method 2: Minimum area rectangle
        rect = cv2.minAreaRect(contour)
        box = cv2.boxPoints(rect)
        box = np.array(box, dtype=np.int32)
        
        # Convert to standard contour format
        return box.reshape(4, 1, 2)
    
    def order_points(self, pts):
        """Order points in clockwise order starting from top-left"""
        # Sort the points based on their x-coordinates
        xSorted = pts[np.argsort(pts[:, 0]), :]
        
        # Grab the left-most and right-most points from the sorted x-coordinate points
        leftMost = xSorted[:2, :]
        rightMost = xSorted[2:, :]
        
        # Now, sort the left-most coordinates according to their y-coordinates
        # to grab the top-left and bottom-left points
        leftMost = leftMost[np.argsort(leftMost[:, 1]), :]
        (tl, bl) = leftMost
        
        # Sort the right-most coordinates according to their y-coordinates
        # to grab the top-right and bottom-right points  
        rightMost = rightMost[np.argsort(rightMost[:, 1]), :]
        (tr, br) = rightMost
        
        # Return the coordinates in top-left, top-right, bottom-right, and bottom-left order
        return np.array([tl, tr, br, bl], dtype="float32")