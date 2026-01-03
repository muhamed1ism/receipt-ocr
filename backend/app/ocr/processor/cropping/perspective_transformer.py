"""
Perspective Transformation for Receipt Cropping
==============================================
Handles perspective correction and image transformation.
"""

import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)


class PerspectiveTransformer:
    """Handles perspective transformation for receipt cropping"""
    
    def __init__(self, debug=False):
        self.debug = debug
    
    def calculate_output_dimensions(self, corners):
        """Calculate optimal output dimensions from corner points"""
        ordered_corners = self.order_points(corners)
        (tl, tr, br, bl) = ordered_corners
        
        # Calculate width by taking maximum of top and bottom edge lengths
        width_top = np.linalg.norm(tr - tl)
        width_bottom = np.linalg.norm(br - bl)
        width = max(int(width_top), int(width_bottom))
        
        # Calculate height by taking maximum of left and right edge lengths
        height_left = np.linalg.norm(bl - tl)
        height_right = np.linalg.norm(br - tr)
        height = max(int(height_left), int(height_right))
        
        # Ensure minimum dimensions for OCR
        width = max(width, 200)
        height = max(height, 300)
        
        # Limit maximum dimensions to prevent memory issues
        if width > 2000:
            scale_factor = 2000 / width
            width = 2000
            height = int(height * scale_factor)
        
        if height > 3000:
            scale_factor = 3000 / height
            height = 3000
            width = int(width * scale_factor)
        
        return width, height
    
    def apply_perspective_transform(self, image, contour):
        """Apply perspective transformation to straighten the receipt"""
        
        if contour is None or len(contour) != 4:
            logger.error("[PERSPECTIVE] Invalid contour for transformation")
            return None
        
        # Order the corner points consistently
        if contour.shape == (4, 1, 2):
            corners = contour.reshape(4, 2)
        else:
            corners = contour
        
        ordered_corners = self.order_points(corners.astype(np.float32))
        
        # Calculate output dimensions
        width, height = self.calculate_output_dimensions(ordered_corners)
        
        # Define destination points for a clean rectangle
        dst_corners = np.array([
            [0, 0],                    # top-left
            [width - 1, 0],          # top-right
            [width - 1, height - 1], # bottom-right
            [0, height - 1]          # bottom-left
        ], dtype="float32")
        
        # Calculate perspective transformation matrix
        transform_matrix = cv2.getPerspectiveTransform(ordered_corners, dst_corners)
        
        # Apply the transformation
        try:
            warped = cv2.warpPerspective(image, transform_matrix, (width, height))
            
            if self.debug:
                logger.info(f"[PERSPECTIVE] Transformed to {width}x{height}")
                logger.debug(f"[PERSPECTIVE] Source corners: {ordered_corners}")
                logger.debug(f"[PERSPECTIVE] Dest corners: {dst_corners}")
            
            return warped
            
        except Exception as e:
            logger.error(f"[PERSPECTIVE] Transformation failed: {str(e)}")
            return None
    
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
    
    def get_transform_info(self, contour, output_width, output_height):
        """Get information about the transformation that would be applied"""
        if contour is None or len(contour) != 4:
            return None
        
        corners = contour.reshape(4, 2) if contour.shape == (4, 1, 2) else contour
        ordered_corners = self.order_points(corners.astype(np.float32))
        
        # Calculate original dimensions
        original_width, original_height = self.calculate_output_dimensions(ordered_corners)
        
        # Calculate scale factors
        width_scale = output_width / original_width
        height_scale = output_height / original_height
        
        return {
            'original_corners': ordered_corners,
            'original_dimensions': (original_width, original_height),
            'output_dimensions': (output_width, output_height),
            'scale_factors': (width_scale, height_scale),
            'area_original': cv2.contourArea(corners.astype(np.int32)),
            'area_output': output_width * output_height
        }