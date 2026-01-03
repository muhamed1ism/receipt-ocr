"""
Text Box Merging for OCR Results
=================================
Handles spatial analysis and merging of PaddleOCR text boxes into complete lines.

PaddleOCR detects individual text boxes (columns), but receipts have
tab-separated data on the same line. This module merges boxes that are
vertically aligned into complete lines.
"""

import logging
from typing import List

import numpy as np

logger = logging.getLogger(__name__)

# ===== MERGING CONSTANTS =====
# Adaptive threshold bounds for vertical alignment
MIN_Y_THRESHOLD = 8.0   # Don't merge items closer than 8px vertically (too close = same box)
MAX_Y_THRESHOLD = 30.0  # Don't merge items farther than 30px vertically (too far = different lines)
DEFAULT_Y_THRESHOLD = 15.0  # Fallback threshold if auto-detection fails

# Horizontal spacing between merged text boxes
LARGE_GAP_THRESHOLD = 30   # Gap > 30px = add tab (4 spaces)
MEDIUM_GAP_THRESHOLD = 10  # Gap > 10px = add 2 spaces
LARGE_GAP_SPACING = "    " # 4 spaces (tab)
MEDIUM_GAP_SPACING = "  "  # 2 spaces
SMALL_GAP_SPACING = " "    # 1 space

# Adaptive threshold calculation parameters
MAX_REASONABLE_GAP = 50    # Gaps > 50px are definitely line breaks, not within-line spacing
PERCENTILE_THRESHOLD = 90  # Use 90th percentile of gaps for threshold


def calculate_adaptive_threshold(items: List[dict], debug: bool = False) -> float:
    """
    Automatically calculate optimal y_threshold based on actual receipt data.

    Strategy:
    1. Sort all text boxes by Y position (top to bottom)
    2. Calculate vertical gaps between consecutive boxes
    3. Separate "small gaps" (within same line) from "large gaps" (between lines)
    4. Use 90th percentile of small gaps as threshold

    This adapts to:
    - Different font sizes (receipts with large vs small text)
    - Different receipt formats (tight vs loose spacing)
    - OCR misalignment (slight vertical variations)

    Args:
        items: List of dicts with 'y_center', 'x1', 'text' keys
        debug: Enable debug logging

    Returns:
        float: Optimal y_threshold in pixels

    Example:
        Items at Y: [50, 52, 55, 78, 80, 82, 105, ...]
        Gaps:       [2,  3,  23, 2,  2,  23, ...]
        Small gaps: [2, 3, 2, 2] (within same line)
        Large gaps: [23, 23] (between lines)
        90th percentile of [2,3,2,2] = 3
        Threshold: 3 + safety margin = ~18
    """
    if not items or len(items) < 2:
        if debug:
            logger.debug(f"[AUTO-THRESHOLD] Not enough items, using fallback={DEFAULT_Y_THRESHOLD}")
        return DEFAULT_Y_THRESHOLD

    # Sort by Y position (top to bottom)
    sorted_items = sorted(items, key=lambda x: x['y_center'])

    # Calculate gaps between consecutive items
    gaps = []
    for i in range(len(sorted_items) - 1):
        gap = abs(sorted_items[i+1]['y_center'] - sorted_items[i]['y_center'])
        if gap > 0.1:  # Ignore items at exactly same Y
            gaps.append(gap)

    if not gaps:
        if debug:
            logger.debug(f"[AUTO-THRESHOLD] No gaps found, using fallback={DEFAULT_Y_THRESHOLD}")
        return DEFAULT_Y_THRESHOLD

    # Filter out extreme outliers (gaps > 50px are definitely line breaks)
    # We only want to analyze "reasonable" gaps to find within-line threshold
    reasonable_gaps = [g for g in gaps if g < MAX_REASONABLE_GAP]

    if not reasonable_gaps:
        if debug:
            logger.debug(f"[AUTO-THRESHOLD] All gaps are large, using fallback={DEFAULT_Y_THRESHOLD}")
        return DEFAULT_Y_THRESHOLD

    # Use 90th percentile of reasonable gaps
    # This means: "90% of items within a line have gaps <= this value"
    threshold = np.percentile(reasonable_gaps, PERCENTILE_THRESHOLD)

    # Apply safety bounds
    threshold = max(MIN_Y_THRESHOLD, min(MAX_Y_THRESHOLD, threshold))

    if debug:
        logger.debug(f"[AUTO-THRESHOLD] Analyzed {len(gaps)} gaps")
        logger.debug(f"[AUTO-THRESHOLD] Reasonable gaps (<{MAX_REASONABLE_GAP}px): {sorted(reasonable_gaps)[:20]}")
        logger.debug(f"[AUTO-THRESHOLD] {PERCENTILE_THRESHOLD}th percentile: {np.percentile(reasonable_gaps, PERCENTILE_THRESHOLD):.1f}px")
        logger.debug(f"[AUTO-THRESHOLD] Final threshold (with bounds): {threshold:.1f}px")

    return float(threshold)


def merge_horizontal_text_boxes(rec_texts: List[str],
                                 rec_scores: List[float],
                                 rec_boxes,
                                 y_threshold: float | None = None,
                                 auto_detect: bool = True,
                                 debug: bool = False) -> List[str]:
    """
    Merge OCR text boxes that are on the same horizontal line.

    PaddleOCR detects individual text boxes (columns), but receipts have
    tab-separated data on the same line. This function merges boxes that
    are vertically aligned into complete lines.

    Args:
        rec_texts: List of recognized text strings
        rec_scores: List of confidence scores
        rec_boxes: List/array of bounding boxes [[x1, y1, x2, y2], ...]
        y_threshold: Maximum Y-difference to consider boxes on same line (None = auto-detect)
        auto_detect: Enable automatic threshold detection based on receipt gaps
        debug: Enable debug logging

    Returns:
        List of merged text lines (strings)

    Example:
        Input:  ['kava', '2.10', '1', '2.10']  with Y coords [50, 48, 52, 49]
        Output: ['kava    2.10    1    2.10']
    """
    if not rec_texts or len(rec_texts) == 0:
        return []

    # Convert rec_boxes to list if needed
    if hasattr(rec_boxes, 'tolist'):
        boxes = rec_boxes.tolist() if hasattr(rec_boxes, 'tolist') else rec_boxes
    else:
        boxes = rec_boxes

    # Create list of (text, score, box) tuples with extracted coordinates
    items = []
    for i, text in enumerate(rec_texts):
        score = rec_scores[i] if i < len(rec_scores) else 0.0
        box = boxes[i] if i < len(boxes) else None

        if box is not None and text.strip():
            # Extract coordinates - handle different box formats
            # Check if first element is a list/tuple (polygon format) or a number (flat format)
            if isinstance(box[0], (list, tuple)):
                # Polygon format: [[x1,y1], [x2,y2], ...] (PaddleOCR 2.6.x)
                xs = [p[0] for p in box]
                ys = [p[1] for p in box]
                x1, y1, x2, y2 = min(xs), min(ys), max(xs), max(ys)
            elif len(box) == 4:
                # Flat format: [x1, y1, x2, y2]
                x1, y1, x2, y2 = box
            else:
                continue

            y_center = (y1 + y2) / 2
            items.append({
                'text': text.strip(),
                'score': score,
                'x1': x1,
                'y_center': y_center,
                'x2': x2
            })

    if not items:
        return []

    # Determine y_threshold for merging
    if auto_detect and y_threshold is None:
        y_threshold = calculate_adaptive_threshold(items, debug=debug)
        if debug:
            logger.debug(f"[MERGE] Using auto-detected y_threshold={y_threshold:.1f}px")
    elif y_threshold is None:
        y_threshold = DEFAULT_Y_THRESHOLD
        if debug:
            logger.debug(f"[MERGE] Using fallback y_threshold={y_threshold:.1f}px")
    else:
        if debug:
            logger.debug(f"[MERGE] Using manual y_threshold={y_threshold:.1f}px")

    # Group items into lines using y_threshold clustering
    # This groups boxes that are within y_threshold of each other vertically
    # Handles Bosnian receipts where qty/price/total are ~12px apart on same line

    # Sort items by Y position first
    sorted_items = sorted(items, key=lambda x: x['y_center'])

    # Cluster items into lines based on y_threshold
    lines = []
    current_line = []

    for item in sorted_items:
        if not current_line:
            # Start new line
            current_line.append(item)
        else:
            # Check if this item is within y_threshold of the FIRST item in current line
            # This prevents cascading where items keep getting added indefinitely
            first_y_in_line = current_line[0]['y_center']
            item_y = item['y_center']

            # Item belongs to current line if it's within y_threshold of the line's anchor (first item)
            # Example: First item at Y:925, threshold=30px
            #   - Item at Y:948 (diff=23) → PASS, add to line
            #   - Item at Y:958 (diff=33) → FAIL, start new line
            # This prevents merging unrelated items that are just incrementally close
            if abs(item_y - first_y_in_line) <= y_threshold:
                current_line.append(item)
            else:
                # Start new line
                # Sort current line left-to-right before saving
                current_line.sort(key=lambda x: x['x1'])
                lines.append(current_line)
                current_line = [item]

    # Don't forget the last line
    if current_line:
        current_line.sort(key=lambda x: x['x1'])
        lines.append(current_line)

    if debug:
        logger.debug(f"[Y-THRESHOLD CLUSTERING] Grouped {len(sorted_items)} boxes into {len(lines)} lines (threshold={y_threshold:.1f}px)")
        for i, line in enumerate(lines[:10]):  # Show first 10 lines
            y_coords = [f"{item['y_center']:.0f}" for item in line]
            logger.debug(f"  Line {i}: {len(line)} boxes at Y={y_coords}")

    # Merge each line's text with appropriate spacing
    merged_lines = []
    for line in lines:
        # Lines are already sorted left-to-right during clustering

        # Calculate spacing between items and merge with appropriate gaps
        line_text = ""
        prev_x2 = None

        for item in line:
            if prev_x2 is not None:
                # Calculate gap between previous box and current box
                gap = item['x1'] - prev_x2

                # Use spacing to approximate tabs/spaces
                if gap > LARGE_GAP_THRESHOLD:
                    line_text += LARGE_GAP_SPACING   # Large gap = tab
                elif gap > MEDIUM_GAP_THRESHOLD:
                    line_text += MEDIUM_GAP_SPACING  # Medium gap = double space
                else:
                    line_text += SMALL_GAP_SPACING   # Small gap = single space

            line_text += item['text']
            prev_x2 = item['x2']

        merged_lines.append(line_text)

    if debug:
        logger.debug(f"[MERGE] Merged {len(items)} boxes into {len(merged_lines)} lines")
        logger.debug(f"[MERGE DEBUG] Detailed line structure:")
        for i, line in enumerate(merged_lines[:10]):  # Show first 10 lines
            logger.debug(f"  Line {i:2d}: '{line}'")

    return merged_lines
