"""
Enhanced Contour Detection for Croatian Receipts
===============================================
Improved contour detection with multiple strategies and validation for 98% accuracy target.

This module provides enhanced contour detection capabilities specifically optimized
for Croatian receipt processing, with fallback strategies and quality validation.

Features:
    - Multi-threshold contour detection strategies
    - Croatian receipt-specific contour validation
    - Confidence scoring and strategy selection
    - Fallback handling for edge cases
    - Performance optimization with early termination

Usage:
    >>> detector = EnhancedContourDetector(debug=True)
    >>> contour, confidence = detector.detect_receipt_contour(image)
    >>> if confidence > 0.9:
    >>>     # High confidence detection - proceed with cropping
"""

import cv2
import numpy as np
import logging
from typing import Tuple, Optional, List, Dict
from dataclasses import dataclass
from app.core.constants import DEBUG_SAVE_FILES

logger = logging.getLogger(__name__)


@dataclass
class ContourResult:
    """Result container for contour detection with confidence scoring"""
    contour: Optional[np.ndarray]
    confidence: float
    method: str
    area: float
    perimeter: float
    aspect_ratio: float
    validation_flags: Dict[str, bool]


class EnhancedContourDetector:
    """
    Enhanced contour detection system for Croatian receipt processing.

    Provides multiple detection strategies with quality validation and confidence
    scoring to achieve 98% accuracy target for receipt boundary detection.

    Detection Strategies:
        1. Otsu binarization + contour detection
        2. Adaptive mean threshold
        3. Adaptive Gaussian threshold
        4. Edge-based detection with Canny
        5. Morphological operations for broken edges

    Croatian Receipt Optimizations:
        - Aspect ratio validation for typical receipt proportions
        - Size validation for Croatian thermal receipt standards
        - Content-aware validation using text layout analysis
        - Store chain specific adaptations
    """

    def __init__(self, debug: bool = True):
        """
        Initialize enhanced contour detector.

        Args:
            debug: Enable debug logging and image saving
        """
        self.debug = debug
        self.logger = logger

        # Debug image saving
        if self.debug:
            try:
                from app.utils.unified_debug_manager import get_global_debug_manager
                self.debug_manager = get_global_debug_manager()
            except ImportError:
                self.debug_manager = None

        # Croatian receipt characteristics - BALANCED for main receipt outline
        self.min_receipt_area = 100000   # Large enough to avoid grain noise
        self.max_receipt_area = 1200000  # Conservative maximum
        self.min_aspect_ratio = 0.3      # Allow some variation
        self.max_aspect_ratio = 3.0      # Cover tall receipts

        # Detection strategy weights - SIMPLIFIED for main outline detection
        self.strategy_weights = {
            'otsu_binary': 1.0,         # Best for clean background separation
            'adaptive_gaussian': 0.8,   # Good for varying lighting
            'canny_based': 0.6          # Backup for edge detection
        }

    def save_debug_image(self, image: np.ndarray, filename: str, stage: str = "contour_detection"):
        """Save debug image using unified debug manager (only if DEBUG_SAVE_FILES=True)"""
        if not self.debug or not DEBUG_SAVE_FILES:
            if self.debug and not DEBUG_SAVE_FILES:
                self.logger.debug(f"[ENHANCED CONTOUR] Skipping debug image '{filename}' (DEBUG_SAVE_FILES=False)")
            return

        if self.debug_manager is None:
            return

        try:
            saved_path = self.debug_manager.save_visual_debug(stage, image, filename)
            if saved_path:
                self.logger.debug(f"[ENHANCED CONTOUR] Saved debug image: {filename}")
        except Exception as e:
            self.logger.warning(f"[ENHANCED CONTOUR] Failed to save debug image {filename}: {e}")

    def detect_receipt_contour(self, image: np.ndarray) -> Tuple[Optional[np.ndarray], float]:
        """
        Main contour detection method with multiple strategies and validation.

        Args:
            image: Input image for contour detection

        Returns:
            Tuple of (best_contour, confidence_score)
        """
        if image is None or image.size == 0:
            self.logger.warning("[ENHANCED CONTOUR] Invalid input image")
            return None, 0.0

        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()

        # Save original image for debug
        self.save_debug_image(image, "01_contour_original.png")
        self.save_debug_image(gray, "02_contour_grayscale.png")

        self.logger.info(f"[ENHANCED CONTOUR] Starting enhanced detection on {gray.shape} image")

        # Apply SIMPLIFIED detection strategies - focus on main receipt outline
        results = []

        # Strategy 1: Otsu binarization (best for clean separation)
        otsu_result = self._detect_otsu_binary(gray)
        if otsu_result.contour is not None:
            results.append(otsu_result)

        # Strategy 2: Adaptive Gaussian threshold (good for varying lighting)
        adaptive_gauss_result = self._detect_adaptive_gaussian(gray)
        if adaptive_gauss_result.contour is not None:
            results.append(adaptive_gauss_result)

        # Strategy 3: Canny edge-based detection (backup for edge cases)
        canny_result = self._detect_canny_based(gray)
        if canny_result.contour is not None:
            results.append(canny_result)

        # Select best result based on confidence scoring
        best_result = self._select_best_result(results, gray)

        if best_result:
            self.logger.info(f"[ENHANCED CONTOUR] Best result: {best_result.method} "
                           f"(confidence: {best_result.confidence:.3f})")
            return best_result.contour, best_result.confidence
        else:
            self.logger.warning("[ENHANCED CONTOUR] No valid contour detected by any strategy")
            return None, 0.0

    def _detect_otsu_binary(self, gray: np.ndarray) -> ContourResult:
        """Detect contour using Otsu binarization with morphological filtering to remove grain noise"""
        try:
            # Apply Otsu threshold - INVERTED to make receipt white on black background
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            self.save_debug_image(binary, "03_otsu_binary.png")

            # MORPHOLOGICAL FILTERING to remove small grains and focus on main shapes
            # Remove small noise with opening operation
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
            binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=2)
            self.save_debug_image(binary, "04_otsu_morph_open.png")

            # Fill gaps in main shapes with closing operation
            kernel_large = cv2.getStructuringElement(cv2.MORPH_RECT, (10, 10))
            binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel_large, iterations=1)
            self.save_debug_image(binary, "05_otsu_morph_close.png")

            # Find contours - use RETR_LIST to get all contours, not just external
            contours, _ = cv2.findContours(binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

            # Filter out contours that touch image edges (these are usually image boundaries)
            h, w = gray.shape
            filtered_contours = []
            for contour in contours:
                x, y, cw, ch = cv2.boundingRect(contour)
                # Skip if contour touches any edge (5 pixel margin)
                if x > 5 and y > 5 and (x + cw) < (w - 5) and (y + ch) < (h - 5):
                    filtered_contours.append(contour)

            contours = filtered_contours

            # Find best contour
            best_contour = self._find_best_contour_by_area(contours)

            # Save contour visualization
            if contours:
                contour_viz = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
                cv2.drawContours(contour_viz, contours, -1, (0, 255, 0), 2)  # All contours in green
                if best_contour is not None:
                    cv2.drawContours(contour_viz, [best_contour], -1, (0, 0, 255), 3)  # Best contour in red
                self.save_debug_image(contour_viz, "06_otsu_contours.png")

            if best_contour is not None:
                return self._create_contour_result(best_contour, "otsu_binary", gray)
            else:
                return ContourResult(None, 0.0, "otsu_binary", 0, 0, 0, {})

        except Exception as e:
            self.logger.warning(f"[ENHANCED CONTOUR] Otsu detection failed: {e}")
            return ContourResult(None, 0.0, "otsu_binary", 0, 0, 0, {})

    def _detect_adaptive_mean(self, gray: np.ndarray) -> ContourResult:
        """Detect contour using adaptive mean threshold"""
        try:
            # Apply adaptive mean threshold
            binary = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2
            )

            # Find contours
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Find best contour
            best_contour = self._find_best_contour_by_area(contours)

            if best_contour is not None:
                return self._create_contour_result(best_contour, "adaptive_mean", gray)
            else:
                return ContourResult(None, 0.0, "adaptive_mean", 0, 0, 0, {})

        except Exception as e:
            self.logger.warning(f"[ENHANCED CONTOUR] Adaptive mean detection failed: {e}")
            return ContourResult(None, 0.0, "adaptive_mean", 0, 0, 0, {})

    def _detect_adaptive_gaussian(self, gray: np.ndarray) -> ContourResult:
        """Detect contour using adaptive Gaussian threshold"""
        try:
            # Apply adaptive Gaussian threshold
            binary = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )

            # Find contours
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Find best contour
            best_contour = self._find_best_contour_by_area(contours)

            if best_contour is not None:
                return self._create_contour_result(best_contour, "adaptive_gaussian", gray)
            else:
                return ContourResult(None, 0.0, "adaptive_gaussian", 0, 0, 0, {})

        except Exception as e:
            self.logger.warning(f"[ENHANCED CONTOUR] Adaptive Gaussian detection failed: {e}")
            return ContourResult(None, 0.0, "adaptive_gaussian", 0, 0, 0, {})

    def _detect_canny_based(self, gray: np.ndarray) -> ContourResult:
        """Detect contour using Canny edge detection"""
        try:
            # Apply Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)

            # Apply Canny edge detection
            edges = cv2.Canny(blurred, 50, 150, apertureSize=3)

            # Morphological operations to connect edges
            kernel = np.ones((3, 3), np.uint8)
            edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Find best contour
            best_contour = self._find_best_contour_by_area(contours)

            if best_contour is not None:
                return self._create_contour_result(best_contour, "canny_based", gray)
            else:
                return ContourResult(None, 0.0, "canny_based", 0, 0, 0, {})

        except Exception as e:
            self.logger.warning(f"[ENHANCED CONTOUR] Canny-based detection failed: {e}")
            return ContourResult(None, 0.0, "canny_based", 0, 0, 0, {})

    def _detect_morphological(self, gray: np.ndarray) -> ContourResult:
        """Detect contour using morphological operations for broken edges"""
        try:
            # Apply initial threshold
            _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

            # Morphological operations to repair broken edges
            kernel_close = np.ones((5, 5), np.uint8)
            binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel_close)

            kernel_open = np.ones((3, 3), np.uint8)
            binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel_open)

            # Find contours
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Find best contour
            best_contour = self._find_best_contour_by_area(contours)

            if best_contour is not None:
                return self._create_contour_result(best_contour, "morphological", gray)
            else:
                return ContourResult(None, 0.0, "morphological", 0, 0, 0, {})

        except Exception as e:
            self.logger.warning(f"[ENHANCED CONTOUR] Morphological detection failed: {e}")
            return ContourResult(None, 0.0, "morphological", 0, 0, 0, {})

    def _find_best_contour_by_area(self, contours: List[np.ndarray]) -> Optional[np.ndarray]:
        """Find the largest valid contour from a list of contours"""
        best_contour = None
        max_area = 0

        for contour in contours:
            area = cv2.contourArea(contour)

            # Check if area is within valid range
            if self.min_receipt_area <= area <= self.max_receipt_area:
                if area > max_area:
                    max_area = area
                    best_contour = contour

        return best_contour

    def _create_contour_result(self, contour: np.ndarray, method: str,
                             gray: np.ndarray) -> ContourResult:
        """Create a ContourResult with validation and confidence scoring"""
        # Calculate basic metrics
        area = cv2.contourArea(contour)
        perimeter = cv2.arcLength(contour, True)

        # Calculate bounding rectangle for aspect ratio
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = h / w if w > 0 else 0

        # Validate contour characteristics
        validation_flags = {
            'area_valid': self.min_receipt_area <= area <= self.max_receipt_area,
            'aspect_ratio_valid': self.min_aspect_ratio <= aspect_ratio <= self.max_aspect_ratio,
            'perimeter_valid': perimeter > 100,  # Minimum perimeter
            'shape_valid': self._validate_contour_shape(contour),
            'position_valid': self._validate_contour_position(contour, gray.shape),
            'croatian_receipt_characteristics': self._validate_croatian_characteristics(contour, gray)
        }

        # Calculate confidence score
        confidence = self._calculate_confidence_score(contour, method, validation_flags, gray)

        return ContourResult(
            contour=contour,
            confidence=confidence,
            method=method,
            area=area,
            perimeter=perimeter,
            aspect_ratio=aspect_ratio,
            validation_flags=validation_flags
        )

    def _validate_contour_shape(self, contour: np.ndarray) -> bool:
        """Validate that contour has reasonable shape characteristics"""
        # Approximate contour to polygon
        epsilon = 0.02 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)

        # Check if it's roughly rectangular (4-8 points after approximation)
        return 4 <= len(approx) <= 8

    def _validate_contour_position(self, contour: np.ndarray, image_shape: Tuple[int, int]) -> bool:
        """Validate contour position within image bounds - CONSERVATIVE for main receipt"""
        x, y, w, h = cv2.boundingRect(contour)
        img_h, img_w = image_shape

        # Check if contour takes up reasonable portion of image - BALANCED
        contour_ratio = (w * h) / (img_w * img_h)
        return 0.15 <= contour_ratio <= 0.80  # Main receipt should be 15-80% of image

    def _validate_croatian_characteristics(self, contour: np.ndarray, gray: np.ndarray) -> bool:
        """Validate characteristics specific to Croatian receipts"""
        x, y, w, h = cv2.boundingRect(contour)

        # Extract region of interest
        roi = gray[y:y+h, x:x+w]

        # Check for typical Croatian receipt characteristics
        mean_brightness = np.mean(roi)
        contrast = np.std(roi)

        # Croatian thermal receipts typically have:
        # - White/light background (high brightness)
        # - Good contrast for text readability
        brightness_valid = mean_brightness > 150  # Light background
        contrast_valid = contrast > 20           # Sufficient contrast

        return brightness_valid and contrast_valid

    def _calculate_confidence_score(self, contour: np.ndarray, method: str,
                                  validation_flags: Dict[str, bool], gray: np.ndarray) -> float:
        """Calculate confidence score for contour detection result"""
        base_score = self.strategy_weights.get(method, 0.5)

        # Weight by validation results
        validation_score = sum(validation_flags.values()) / len(validation_flags)

        # Additional scoring factors
        area_score = self._score_area_appropriateness(cv2.contourArea(contour))
        shape_score = self._score_shape_quality(contour)
        content_score = self._score_content_characteristics(contour, gray)

        # Combine scores with weights
        final_confidence = (
            base_score * 0.3 +           # Method base score
            validation_score * 0.4 +     # Validation results
            area_score * 0.1 +          # Area appropriateness
            shape_score * 0.1 +         # Shape quality
            content_score * 0.1         # Content characteristics
        )

        return min(final_confidence, 1.0)  # Cap at 1.0

    def _score_area_appropriateness(self, area: float) -> float:
        """Score area appropriateness for Croatian receipts - Fixed for full receipt detection"""
        # Optimal area range for typical Croatian receipts - expanded to accept larger receipts
        optimal_min = 100000   # Increased to better match full receipts
        optimal_max = 800000   # Significantly increased to capture full receipt images

        if optimal_min <= area <= optimal_max:
            return 1.0
        elif self.min_receipt_area <= area < optimal_min:
            return 0.8  # Increased score for smaller but valid receipts
        elif optimal_max < area <= self.max_receipt_area:
            return 0.9  # Increased score for large receipts (was 0.8)
        else:
            return 0.0

    def _score_shape_quality(self, contour: np.ndarray) -> float:
        """Score the shape quality of the contour"""
        # Check how rectangular the contour is
        epsilon = 0.02 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)

        if len(approx) == 4:
            return 1.0  # Perfect rectangle
        elif len(approx) in [5, 6]:
            return 0.8  # Close to rectangle
        elif len(approx) in [7, 8]:
            return 0.6  # Reasonable approximation
        else:
            return 0.3  # Poor shape

    def _score_content_characteristics(self, contour: np.ndarray, gray: np.ndarray) -> float:
        """Score content characteristics within the contour"""
        x, y, w, h = cv2.boundingRect(contour)
        roi = gray[y:y+h, x:x+w]

        # Calculate text-like characteristics
        edges = cv2.Canny(roi, 50, 150)
        edge_density = np.sum(edges > 0) / edges.size

        # Croatian receipts should have moderate edge density (text lines)
        if 0.05 <= edge_density <= 0.15:
            return 1.0
        elif 0.02 <= edge_density <= 0.20:
            return 0.7
        else:
            return 0.4

    def _select_best_result(self, results: List[ContourResult], gray: np.ndarray) -> Optional[ContourResult]:
        """Select the best result from multiple detection strategies"""
        if not results:
            return None

        # Sort by confidence score
        results.sort(key=lambda r: r.confidence, reverse=True)

        # Return the highest confidence result that meets minimum threshold
        for result in results:
            if result.confidence >= 0.5:  # Minimum confidence threshold
                self.logger.debug(f"[ENHANCED CONTOUR] Selected {result.method} "
                                f"(confidence: {result.confidence:.3f})")
                return result

        # If no result meets threshold, return the best available
        if results:
            self.logger.warning(f"[ENHANCED CONTOUR] No high-confidence result, "
                              f"using best available: {results[0].method} "
                              f"(confidence: {results[0].confidence:.3f})")
            return results[0]

        return None