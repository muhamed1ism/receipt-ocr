"""
Receipt Contour Detector - Refactored
=====================================
Main coordinator for receipt contour detection using modular strategies.
"""

import cv2
import numpy as np
import logging
import os
from app.ocr.engines.scoring.contour_scoring import score_receipt_contour
from app.core.constants import DEBUG_IMAGE_DIR, DEBUG_SAVE_FILES
from .contour_methods import BinaryContourMethods, FallbackContourDetection, ContourValidator

logger = logging.getLogger(__name__)


class ReceiptContourDetector:
    """Main receipt contour detector using multiple strategies"""
    
    def __init__(self, debug=True):
        self.debug = debug
        self.debug_dir = DEBUG_IMAGE_DIR
        os.makedirs(self.debug_dir, exist_ok=True)
        
        # Initialize strategy components
        self.binary_methods = BinaryContourMethods(debug=debug)
        self.fallback_detection = FallbackContourDetection(debug=debug)
        self.validator = ContourValidator()
        
        # Store current gray image for scoring
        self._current_gray_image = None
    
    def save_debug_image(self, image, name):
        """Save debug image if debug mode AND DEBUG_SAVE_FILES are enabled"""
        if self.debug and DEBUG_SAVE_FILES:
            path = os.path.join(self.debug_dir, name if name.endswith(".png") else name + ".png")
            cv2.imwrite(path, image)
            logger.debug(f"[CONTOUR] Saved debug image: {path}")
        elif self.debug and not DEBUG_SAVE_FILES:
            logger.debug(f"[CONTOUR] Skipping debug image '{name}' (DEBUG_SAVE_FILES=False)")
    
    def find_receipt_contour(self, img):
        """Main method to find receipt contour using multiple strategies"""
        if img is None or img.size == 0:
            logger.error("[CONTOUR] Invalid input image")
            return None
        
        h, w = img.shape[:2]
        logger.info(f"[CONTOUR] Processing image {w}x{h}")
        
        # Strategy 1: Try multiple binary methods
        binary_methods, gray_image = self.binary_methods.create_binary_methods(img)
        self._current_gray_image = gray_image
        
        best_contour = self.find_best_contour(binary_methods, img)
        
        if best_contour is not None:
            logger.info("[CONTOUR] Found contour using binary methods")
            return best_contour
        
        # Strategy 2: Enhanced fallback detection
        logger.info("[CONTOUR] Binary methods failed, trying fallback")
        fallback_contour = self.fallback_detection.enhanced_fallback_detection(img)
        
        if fallback_contour is not None:
            logger.info("[CONTOUR] Found contour using fallback method")
            return fallback_contour
        
        logger.warning("[CONTOUR] All detection methods failed")
        return None
    
    def find_best_contour(self, binary_methods, original_image):
        """Find the best contour from multiple binary processing methods"""
        h, w = original_image.shape[:2]
        image_area = w * h
        
        best_contour = None
        best_score = -1
        best_method = None
        
        for method_name, binary_image in binary_methods:
            logger.debug(f"[CONTOUR] Testing method: {method_name}")
            self.save_debug_image(binary_image, f"contour_gentle_{method_name}.png")
            
            # Find contours in this binary image
            contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if not contours:
                continue
            
            # Test each contour
            for contour in contours:
                area = cv2.contourArea(contour)

                # Must be substantial (more lenient for finger-held receipts and small receipts in large images)
                if area < image_area * 0.08:  # Reduced from 0.15 to catch smaller receipts
                    continue

                # Convert to rectangle
                rect_contour = self.validator.contour_to_rectangle(contour)

                # CRITICAL FIX: Check whiteness BEFORE other validation
                # Reject dark contours (table edges, wood grain, shadows, background)
                if self._current_gray_image is not None:
                    mask = np.zeros((h, w), np.uint8)
                    cv2.drawContours(mask, [rect_contour], -1, (255,), -1)
                    mean_intensity = cv2.mean(self._current_gray_image, mask=mask)[0]
                else:
                    # Fallback if gray image not available
                    mean_intensity = 200  # Assume white

                # Receipts are WHITE paper - reject anything that's not predominantly white
                # This fixes the wood grain / table detection issue
                if mean_intensity < 140:  # Dark contours = table/background, not receipt
                    logger.debug(f"[CONTOUR] Rejecting dark contour (brightness={mean_intensity:.0f} < 140)")
                    continue

                # Validate the contour
                if not self.validator.validate_full_receipt_contour(rect_contour, (h, w)):
                    continue

                # Score this contour
                score = self.score_full_receipt_contour(rect_contour, image_area, (h, w))

                logger.debug(f"[CONTOUR] Method {method_name}: area={area}, brightness={mean_intensity:.0f}, score={score}")

                if score > best_score:
                    best_score = score
                    best_contour = rect_contour
                    best_method = method_name
        
        if best_contour is not None:
            logger.info(f"[CONTOUR] Best method: {best_method} (score: {best_score})")
            
            # Save visualization
            if self.debug:
                debug_img = original_image.copy()
                cv2.drawContours(debug_img, [best_contour], -1, (0, 255, 0), 3)
                self.save_debug_image(debug_img, f"contour_best_{best_method}.png")
        
        return best_contour
    
    def score_full_receipt_contour(self, contour, image_area, image_shape):
        """Score a contour for receipt detection quality"""
        return score_receipt_contour(contour, image_area, image_shape, self._current_gray_image)
    
    def draw_points(self, img, pts, color=(0, 0, 255)):
        """Draw points on image for debugging"""
        img_copy = img.copy()
        for i, pt in enumerate(pts):
            x, y = pt.ravel()
            cv2.circle(img_copy, (int(x), int(y)), 8, color, -1)
            cv2.putText(img_copy, str(i), (int(x-10), int(y-10)), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        return img_copy


def test_fixed_contour_detection(image_path):
    """Test function for the contour detector"""
    image = cv2.imread(image_path)
    if image is None:
        print(f"Could not load image: {image_path}")
        return
    
    detector = ReceiptContourDetector(debug=True)
    contour = detector.find_receipt_contour(image)
    
    if contour is not None:
        print("✅ Contour detected successfully!")
        print(f"Contour shape: {contour.shape}")
        print(f"Contour points: {contour.reshape(-1, 2)}")
        
        # Draw result
        result_img = detector.draw_points(image, contour.reshape(-1, 2))
        result_path = os.path.join(DEBUG_IMAGE_DIR, "contour_result.png")
        cv2.imwrite(result_path, result_img)
        print(f"Result saved to {result_path}")
    else:
        print("❌ No contour detected")