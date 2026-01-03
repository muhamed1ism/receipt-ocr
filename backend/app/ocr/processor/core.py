"""
Receipt Processor (Image Processing Core)
========================================
Low-level image processing for receipt images before OCR.

PIPELINE POSITION:
    pipeline/simple_ocr_pipeline.py (MAIN PIPELINE)
        ↓
    processor/core.py (THIS FILE - Image Processing)
        ↓
    ┌─────────────────┬─────────────────┐
    │ contour.py      │ cropper.py      │
    │ (Find Receipt)  │ (Crop & Fix)    │
    └─────────────────┴─────────────────┘

PURPOSE:
- LOW-LEVEL image processing before OCR
- Receipt boundary detection and cropping
- Image orientation correction and enhancement
- Prepares processed images for OCR processing
- Different from pipeline which handles the complete flow
"""

import cv2
import numpy as np
import logging
import os
from app.ocr.processor.contour import ReceiptContourDetector
from app.ocr.processor.cropper import ReceiptCropper
from app.core.constants import DEBUG_IMAGE_DIR, DEBUG_SAVE_FILES

logger = logging.getLogger(__name__)
os.makedirs(DEBUG_IMAGE_DIR, exist_ok=True)

class ReceiptProcessor:
    def __init__(self, debug=True):
        self.debug = debug
        # Use the improved contour detector and dedicated cropper
        self.contour_detector = ReceiptContourDetector(debug=debug)
        self.cropper = ReceiptCropper(debug=debug)
        self.debug_session = None  # Will be set by pipeline if debug session active

    def save_debug_image(self, image, name):
        """Save debug image if debug mode AND DEBUG_SAVE_FILES are enabled"""
        if self.debug and DEBUG_SAVE_FILES:
            path = os.path.join(DEBUG_IMAGE_DIR, name if name.endswith(".png") else name + ".png")
            cv2.imwrite(path, image)
            logger.debug(f"[PROCESSOR] Saved debug image: {path}")
        elif self.debug and not DEBUG_SAVE_FILES:
            logger.debug(f"[PROCESSOR] Skipping debug image '{name}' (DEBUG_SAVE_FILES=False)")

    def detect_receipt_orientation(self, image):
        """Detect and correct receipt orientation"""
        h, w = image.shape[:2]

        # If landscape, rotate to portrait
        if w > h:
            rotated = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
            self.save_debug_image(rotated, "step1_orientation_corrected.png")
            # Save to debug session if available
            if self.debug_session:
                self.debug_session.save_visual_debug("orientation_corrected", rotated, "01_orientation_corrected.png")
            return rotated

        return image

    def upscale_if_needed(self, image):
        """
        DPI optimization - upscale if image is too small for OCR
        No enhancement applied - only size adjustment
        """
        if len(image.shape) == 3:
            h, w = image.shape[:2]
        else:
            h, w = image.shape

        # DPI optimization - upscale if too small
        if w < 800:  # If less than 800px wide, upscale for better OCR
            scale_factor = 800 / w
            new_w = int(w * scale_factor)
            new_h = int(h * scale_factor)

            upscaled = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
            self.save_debug_image(upscaled, "upscaled_for_dpi.png")
            # Save to debug session if available
            if self.debug_session:
                self.debug_session.save_visual_debug("upscaled_for_dpi", upscaled, "04_upscaled_for_dpi.png")
            logger.info(f"[PROCESSOR] Upscaled from {w}x{h} to {new_w}x{new_h}")
            return upscaled

        return image
    
    # Legacy compatibility methods
    def four_point_crop(self, image, contour):
        """Legacy method - now redirects to dedicated cropper"""
        logger.info("[PROCESSOR] Legacy four_point_crop called - using dedicated cropper")
        return self.cropper.crop_receipt(image, contour)

    def order_points(self, pts):
        """Legacy method - now redirects to dedicated cropper"""
        return self.cropper.order_points(pts)

    def process_receipt(self, image):
        """
        Main processing pipeline using improved contour detection
        """
        logger.info("[PROCESSOR] Starting receipt processing with improved contour detection")

        try:
            # Save original image to debug session
            if self.debug_session:
                self.debug_session.save_visual_debug("original_input", image, "00_original_input.png")

            # Step 1: Fix orientation
            oriented = self.detect_receipt_orientation(image)

            # Step 2: Find receipt using improved contour detection
            logger.info("[PROCESSOR] Finding receipt contour...")
            receipt_contour = self.contour_detector.find_receipt_contour(oriented)

            # Save contour visualization if found
            if self.debug_session and receipt_contour is not None:
                # Draw contour on copy of image for visualization
                contour_vis = oriented.copy()
                cv2.drawContours(contour_vis, [receipt_contour], -1, (0, 255, 0), 3)
                self.debug_session.save_visual_debug("contour_detected", contour_vis, "02_contour_detected.png")

            processed_images = []

            if receipt_contour is not None:
                logger.info("[PROCESSOR] Receipt found, applying perspective correction")

                # Step 3: Crop the receipt using dedicated cropper
                cropped = self.cropper.crop_receipt(oriented, receipt_contour)

                if cropped is not None:
                    # Save as step7 for compatibility
                    self.save_debug_image(cropped, "step7_cropped_and_corrected.png")

                    # Save cropped image to debug session
                    if self.debug_session:
                        self.debug_session.save_visual_debug("cropped_and_corrected", cropped, "03_cropped_and_corrected.png")

                    # Step 4: Upscale if needed (no enhancement, just DPI optimization)
                    upscaled = self.upscale_if_needed(cropped)
                    processed_images.append(upscaled)

                    status = "success_with_crop"
                    logger.info(f"[PROCESSOR] 🎯 SUCCESS! Cropped and ready for OCR preprocessing")
                else:
                    logger.warning("[PROCESSOR] Cropping failed, using upscaled full image")
                    upscaled_full = self.upscale_if_needed(oriented)
                    processed_images.append(upscaled_full)
                    status = "crop_failed_fallback"

            else:
                logger.warning("[PROCESSOR] No receipt found, using upscaled full image")

                # Fallback: upscale the whole image if needed
                upscaled_full = self.upscale_if_needed(oriented)
                processed_images.append(upscaled_full)

                status = "fallback_no_crop"
                logger.info("[PROCESSOR] Fallback mode - processing full image")

            logger.info(f"[PROCESSOR] Complete: {status}, {len(processed_images)} images ready for OCR")
            return processed_images, status, {}

        except Exception as e:
            logger.error(f"[PROCESSOR] Error: {e}")

            # Final fallback
            try:
                gray = image if len(image.shape) == 2 else cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                return [gray], "error_fallback", {"error": str(e)}
            except:
                return [image], "complete_failure", {"error": str(e)}