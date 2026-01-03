"""
Contour Validation for Cropping
===============================
Validates and prepares contours for receipt cropping operations.
"""

import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)


class CroppingContourValidator:
    """Handles contour validation and preparation for cropping"""
    
    def __init__(self):
        pass
    
    def validate_contour(self, contour):
        """Validate that contour is suitable for cropping"""
        if contour is None:
            return False
        
        # Must be 4 points for perspective transformation
        if len(contour) != 4:
            logger.debug("[CROP VALIDATE] Contour must have exactly 4 points")
            return False
        
        # Check if points form a reasonable quadrilateral
        area = cv2.contourArea(contour)
        if area < 10000:  # Minimum area threshold
            logger.debug(f"[CROP VALIDATE] Contour area too small: {area}")
            return False
        
        return True
    
    def prepare_contour_for_cropping(self, contour):
        """
        Prepare and validate contour for reliable cropping.
        Returns properly formatted 4-point contour or None if invalid.
        """
        if contour is None:
            logger.warning("[CROP PREP] No contour provided")
            return None
        
        # Ensure contour has correct shape
        if contour.shape == (4, 1, 2):
            points = contour.reshape(4, 2)
        elif contour.shape == (4, 2):
            points = contour
        else:
            logger.warning(f"[CROP PREP] Invalid contour shape: {contour.shape}")
            return None
        
        # Convert to float32 for precision
        points = points.astype(np.float32)
        
        # Validate points are reasonable
        if not self._validate_corner_points(points):
            return None
        
        # Order points properly: TL, TR, BR, BL
        ordered_points = self.order_points(points)
        
        logger.debug(f"[CROP PREP] Prepared contour with points: {ordered_points}")
        return ordered_points.reshape(4, 1, 2).astype(np.int32)
    
    def order_points(self, pts):
        """Order points for perspective transformation: TL, TR, BR, BL"""
        pts = pts.astype(np.float32)
        rect = np.zeros((4, 2), dtype="float32")
        
        # Sum and difference method for robust corner ordering
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]  # top-left: smallest sum (x + y)
        rect[2] = pts[np.argmax(s)]  # bottom-right: largest sum (x + y)
        
        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]  # top-right: smallest difference (x - y)
        rect[3] = pts[np.argmax(diff)]  # bottom-left: largest difference (x - y)
        
        return rect
    
    def _validate_corner_points(self, points):
        """Validate that corner points form a reasonable quadrilateral"""
        # Check for duplicate points
        for i in range(len(points)):
            for j in range(i + 1, len(points)):
                if np.allclose(points[i], points[j], atol=5):
                    logger.warning("[CROP VALIDATE] Duplicate corner points detected")
                    return False
        
        # Check if points are within reasonable bounds
        # (This assumes they've been checked against image dimensions elsewhere)
        x_coords = points[:, 0]
        y_coords = points[:, 1]
        
        if np.any(x_coords < 0) or np.any(y_coords < 0):
            logger.warning("[CROP VALIDATE] Points have negative coordinates")
            return False
        
        # Check if quadrilateral is too small
        area = cv2.contourArea(points.astype(np.int32))
        if area < 5000:  # Minimum meaningful area
            logger.warning(f"[CROP VALIDATE] Quadrilateral area too small: {area}")
            return False
        
        return True