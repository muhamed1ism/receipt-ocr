"""
Binary Image Processing Methods
==============================
Different approaches to create binary images for contour detection.
"""

import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)


class BinaryContourMethods:
    """Handles creation of various binary images for contour detection"""
    
    def __init__(self, debug=False):
        self.debug = debug
    
    def create_binary_methods(self, image):
        """Enhanced binary methods - GENTLE approach for finger-held receipts"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        
        # CRITICAL: Much gentler filtering to preserve edges near fingers
        filtered = cv2.GaussianBlur(gray, (3, 3), 0)  # Much lighter blur
        
        methods = []
        
        # Method 1: GENTLE Otsu (works better with fingers)
        _, gentle_otsu = cv2.threshold(filtered, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        methods.append(("gentle_otsu", gentle_otsu))
        
        # Method 2: HIGH threshold binary (fingers are usually darker than receipt)
        high_thresh = int(np.percentile(filtered, 75))  # Use 75th percentile as threshold
        _, high_binary = cv2.threshold(filtered, high_thresh, 255, cv2.THRESH_BINARY)
        methods.append(("high_threshold", high_binary))
        
        # Method 3: VERY gentle adaptive (large block size to ignore finger details)
        adaptive_gentle = cv2.adaptiveThreshold(filtered, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                               cv2.THRESH_BINARY, 31, 15)  # Large block, gentle
        methods.append(("adaptive_gentle", adaptive_gentle))
        
        # Method 4: Multiple Otsu thresholds to separate finger/receipt/background
        mean_val = int(np.mean(filtered))
        
        _, mean_plus = cv2.threshold(filtered, mean_val + 20, 255, cv2.THRESH_BINARY)
        methods.append(("mean_plus", mean_plus))
        
        _, mean_minus = cv2.threshold(filtered, mean_val - 20, 255, cv2.THRESH_BINARY)
        methods.append(("mean_minus", mean_minus))
        
        # Method 5: Edge-based but MUCH gentler
        edges_gentle = cv2.Canny(filtered, 30, 90)  # Lower thresholds
        kernel_small = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))  # Smaller kernel
        edges_dilated = cv2.dilate(edges_gentle, kernel_small, iterations=1)
        methods.append(("gentle_edges", edges_dilated))
        
        # CRITICAL: Only light morphological operations
        cleaned_methods = []
        for name, binary in methods:
            # MINIMAL morphological operations - don't destroy finger boundaries
            kernel_tiny = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
            cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel_tiny, iterations=1)
            cleaned_methods.append((name, cleaned))
        
        return cleaned_methods, gray
    
    def sharpen_edge(self, img):
        """Edge detection for contour finding"""
        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(img, (5, 5), 0)
        
        # Apply dilate and erode to close small gaps
        kernel = np.ones((3, 3), np.uint8)
        dilated = cv2.dilate(blurred, kernel, iterations=2)
        closed = cv2.morphologyEx(dilated, cv2.MORPH_CLOSE, kernel, iterations=2)
        
        # Edge detection
        edged = cv2.Canny(closed, 50, 150, apertureSize=3)
        
        return edged
    
    def binarize(self, edged):
        """Convert edge image to binary with morphological operations"""
        # Apply morphological operations to fill gaps
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        
        # Dilate to make edges thicker
        dilated = cv2.dilate(edged, kernel, iterations=2)
        
        # Close gaps
        closed = cv2.morphologyEx(dilated, cv2.MORPH_CLOSE, kernel, iterations=3)
        
        return closed