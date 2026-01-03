"""
Total Amount Extractor
=====================
Extracts receipt total amounts from Croatian and Bosnian receipts.
"""

import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class TotalExtractor:
    """Extracts total amounts from receipt text"""
    
    def extract_total_flexible(self, lines: list[str]) -> Optional[float]:
        """Extract total with flexible UKUPNO detection (handles split-line format)"""
        for i, line in enumerate(lines):
            line_lower = line.lower()

            # Look for total keywords
            if re.search(r'ukupno|total|suma', line_lower):
                # Try to extract price from same line
                price_match = re.search(r'(\d+[.,]\d{1,2})', line)
                if price_match:
                    try:
                        return float(price_match.group(1).replace(',', '.'))
                    except ValueError:
                        pass

                # Check next line for standalone price (handles "UKUPNO (EUR) :" on one line, "2,10" on next)
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    # Look for price pattern at start of next line
                    next_price_match = re.match(r'^(\d+[.,]\d{1,2})', next_line)
                    if next_price_match:
                        try:
                            price = float(next_price_match.group(1).replace(',', '.'))
                            if 0.5 <= price <= 2000:  # Reasonable range
                                return price
                        except ValueError:
                            pass

                # Also check 2 lines down (in case there's a blank line)
                if i + 2 < len(lines):
                    line_after = lines[i + 2].strip()
                    after_price_match = re.match(r'^(\d+[.,]\d{1,2})', line_after)
                    if after_price_match:
                        try:
                            price = float(after_price_match.group(1).replace(',', '.'))
                            if 0.5 <= price <= 2000:  # Reasonable range
                                return price
                        except ValueError:
                            pass

        return None

    def extract_total_explicit(self, lines: list[str], debug: bool = False) -> Optional[float]:
        """
        EXPLICIT total extraction with keyword-based rules.

        The total appears on a line containing one of these keywords:
        - "TOTAL:" (Bosnian receipts)
        - "UKUPNO:" (Croatian/Bosnian receipts)
        - "SUMA:" (less common)

        Common formats:
        - "TOTAL: 59,29" or "TOTAL: 59.29"
        - "UKUPNO (EUR): 59,29"
        - "TOTAL:" on one line, "59,29" on next line

        Search strategy:
        - Look for keyword line
        - Extract number from same line
        - If not found, check next line

        Args:
            lines: All receipt lines
            debug: Enable debug logging

        Returns:
            Total amount as float, or None if not found
        """
        if debug:
            logger.debug(f"[EXPLICIT TOTAL] Searching in {len(lines)} lines")

        for i, line in enumerate(lines):
            line_upper = line.upper()

            # Check if this line contains a total keyword
            has_total_keyword = any(keyword in line_upper for keyword in ['TOTAL', 'UKUPNO', 'SUMA'])

            if has_total_keyword:
                if debug:
                    logger.debug(f"[EXPLICIT TOTAL] Found keyword on line {i}: '{line}'")

                # Try to extract number from same line first
                # Pattern: digits, comma/dot, 2 decimal places
                # Match patterns like: "59,29", "59.29", "159,00"
                price_match = re.search(r'(\d+[.,]\d{2})', line)
                if price_match:
                    price_str = price_match.group(1).replace(',', '.')
                    try:
                        total = float(price_str)
                        if 0.01 <= total <= 10000:  # Reasonable range for receipt total
                            if debug:
                                logger.debug(f"[EXPLICIT TOTAL] Found total on same line: {total}")
                            return total
                    except ValueError:
                        pass

                # Check next line for standalone price
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if debug:
                        logger.debug(f"[EXPLICIT TOTAL] Checking next line {i+1}: '{next_line}'")

                    # Look for price at start of next line
                    next_match = re.match(r'^(\d+[.,]\d{2})', next_line)
                    if next_match:
                        price_str = next_match.group(1).replace(',', '.')
                        try:
                            total = float(price_str)
                            if 0.01 <= total <= 10000:
                                if debug:
                                    logger.debug(f"[EXPLICIT TOTAL] Found total on next line: {total}")
                                return total
                        except ValueError:
                            pass

                # Check 2 lines down (in case of blank line)
                if i + 2 < len(lines):
                    line_after = lines[i + 2].strip()
                    after_match = re.match(r'^(\d+[.,]\d{2})', line_after)
                    if after_match:
                        price_str = after_match.group(1).replace(',', '.')
                        try:
                            total = float(price_str)
                            if 0.01 <= total <= 10000:
                                if debug:
                                    logger.debug(f"[EXPLICIT TOTAL] Found total 2 lines down: {total}")
                                return total
                        except ValueError:
                            pass

        if debug:
            logger.debug("[EXPLICIT TOTAL] No total found")

        return None