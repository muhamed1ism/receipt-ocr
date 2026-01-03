"""
Receipt Cropper - Refactored
============================
Main coordinator for receipt cropping using modular strategies.
"""

import cv2
import numpy as np
import logging
import os
from app.core.constants import DEBUG_IMAGE_DIR, DEBUG_SAVE_FILES
from .cropping import PerspectiveTransformer, CroppingContourValidator

logger = logging.getLogger(__name__)


class ReceiptCropper:
    """Main receipt cropper using modular components"""
    
    def __init__(self, debug=True):
        self.debug = debug
        self.debug_dir = DEBUG_IMAGE_DIR
        os.makedirs(self.debug_dir, exist_ok=True)
        
        # Initialize specialized components
        self.validator = CroppingContourValidator()
        self.transformer = PerspectiveTransformer(debug=debug)
    
    def save_debug_image(self, image, name):
        """Save debug image if debug mode AND DEBUG_SAVE_FILES are enabled"""
        if self.debug and DEBUG_SAVE_FILES:
            path = os.path.join(self.debug_dir, name if name.endswith(".png") else name + ".png")
            cv2.imwrite(path, image)
            logger.debug(f"[CROPPER] Saved debug image: {path}")
        elif self.debug and not DEBUG_SAVE_FILES:
            logger.debug(f"[CROPPER] Skipping debug image '{name}' (DEBUG_SAVE_FILES=False)")
    
    def crop_receipt(self, image, contour):
        """
        Main method to crop receipt from image using detected contour.
        
        Returns cropped and straightened receipt image.
        """
        if image is None:
            logger.error("[CROPPER] No input image provided")
            return None
        
        if contour is None:
            logger.error("[CROPPER] No contour provided for cropping")
            return None
        
        logger.info("[CROPPER] Starting receipt cropping process")
        
        # Save debug image showing input with contour
        if self.debug:
            debug_img = image.copy()
            cv2.drawContours(debug_img, [contour], -1, (0, 255, 0), 2)
            self.save_debug_image(debug_img, "cropper_input_with_contour.png")
        
        # Step 1: Validate and prepare contour
        if not self.validator.validate_contour(contour):
            logger.warning("[CROPPER] Invalid contour, trying fallback crop")
            return self.fallback_crop(image, contour)
        
        prepared_contour = self.validator.prepare_contour_for_cropping(contour)
        if prepared_contour is None:
            logger.warning("[CROPPER] Could not prepare contour, trying fallback crop")  
            return self.fallback_crop(image, contour)
        
        # Step 2: Apply perspective transformation
        cropped_image = self.transformer.apply_perspective_transform(image, prepared_contour)

        if cropped_image is None:
            logger.warning("[CROPPER] Perspective transform failed, trying fallback crop")
            return self.fallback_crop(image, contour)

        # Step 3: Basic quality validation (without enhancement)
        h, w = cropped_image.shape[:2]
        if w < 100 or h < 150:
            logger.warning(f"[CROPPER] Cropped image very small: {w}x{h}")

        # Save clean cropped result (V0.2.5 style - no enhancement)
        self.save_debug_image(cropped_image, "cropper_result.png")

        logger.info(f"[CROPPER] Successfully cropped to clean image: {w}x{h} (V0.2.5 style)")
        return cropped_image
    
    def fallback_crop(self, image, contour):
        """Fallback cropping using bounding rectangle (V0.2.5 style - no enhancement)"""
        logger.warning("[CROPPER] Using fallback bounding rectangle crop")

        try:
            # Get bounding rectangle
            x, y, w, h = cv2.boundingRect(contour)
            
            # Add small margin if possible
            margin = 5
            x = max(0, x - margin)
            y = max(0, y - margin)
            w = min(image.shape[1] - x, w + 2 * margin)
            h = min(image.shape[0] - y, h + 2 * margin)
            
            # Crop the image
            cropped = image[y:y+h, x:x+w]
            
            self.save_debug_image(cropped, "cropper_fallback.png")
            
            logger.info(f"[CROPPER] Fallback crop: {w} x {h}")
            return cropped
            
        except Exception as e:
            logger.error(f"[CROPPER] Fallback crop failed: {e}")
            return image  # Return original image as last resort
    
    def get_crop_info(self, original_image, cropped_image, contour):
        """Get basic information about the cropping operation (V0.2.5 style)"""
        if any(img is None for img in [original_image, cropped_image]) or contour is None:
            return {}

        # Basic crop information without enhancement metrics
        orig_h, orig_w = original_image.shape[:2]
        crop_h, crop_w = cropped_image.shape[:2]
        contour_area = cv2.contourArea(contour)

        return {
            'original_size': (orig_w, orig_h),
            'cropped_size': (crop_w, crop_h),
            'contour_area': contour_area,
            'size_reduction_ratio': (crop_w * crop_h) / (orig_w * orig_h),
            'crop_type': 'clean_v0.2.5_style'
        }
    
    def order_points(self, pts):
        """Order points for consistency - delegates to validator"""
        return self.validator.order_points(pts)
    
    def validate_contour(self, contour):
        """Validate contour - delegates to validator"""
        return self.validator.validate_contour(contour)