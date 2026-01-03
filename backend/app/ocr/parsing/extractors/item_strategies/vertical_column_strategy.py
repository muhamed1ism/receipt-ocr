"""
Vertical Column Item Extraction Strategy
========================================
Handles receipts where headers and data are in vertical lists.

Example format:
    Kol.
    Iznos
    Cijena
    Naziv
    2,10      <- Cijena value
    1,00      <- Kol value
    2,10      <- Iznos value
    KAVA      <- Naziv value
"""

import re
import logging
from typing import List, Dict, Optional, Any

logger = logging.getLogger(__name__)


class VerticalColumnStrategy:
    """Handles vertical column format where headers and values are stacked"""

    def detect_vertical_header(self, lines: List[str]) -> Optional[Dict[str, int]]:
        """
        Detect if consecutive lines form a vertical header (Kol, Iznos, Cijena, Naziv)

        Returns a dict mapping header names to their order indices, or None
        Example: {'kol': 0, 'iznos': 1, 'cijena': 2, 'naziv': 3}
        """
        header_keywords = ['kol', 'iznos', 'cijena', 'naziv']
        header_positions = {}

        # Look for a sequence of header keywords on consecutive lines
        for i in range(len(lines) - 3):
            # Check if the next 4 lines contain all header keywords
            window = [lines[i+j].lower().strip() for j in range(4)]

            matches = []
            for j, line in enumerate(window):
                for keyword in header_keywords:
                    if keyword in line and keyword not in [m[0] for m in matches]:
                        matches.append((keyword, j))
                        break

            if len(matches) >= 3:  # At least 3 headers found
                # Record the order
                for keyword, pos in matches:
                    header_positions[keyword] = pos
                return header_positions

        return None

    def extract_items_vertical(self, lines: List[str], debug: bool = False) -> List[Dict[str, Any]]:
        """
        Extract items from vertical column format

        Expected pattern:
            Line N:   Kol.
            Line N+1: Iznos
            Line N+2: Cijena
            Line N+3: Naziv
            Line N+4: <price_value>    (maps to Cijena)
            Line N+5: <quantity_value> (maps to Kol)
            Line N+6: <total_value>    (maps to Iznos)
            Line N+7: <name_value>     (maps to Naziv)
        """
        items = []

        # First, find the vertical header
        header_start = -1
        header_map = None

        for i, line in enumerate(lines):
            window_lines = lines[i:i+4] if i + 4 <= len(lines) else []
            if len(window_lines) >= 3:
                detected = self.detect_vertical_header(window_lines)
                if detected:
                    header_start = i
                    header_map = detected
                    if debug:
                        logger.debug(f"[VERTICAL] Found vertical header at line {i}: {header_map}")
                    break

        if header_start == -1 or not header_map:
            if debug:
                logger.debug("[VERTICAL] No vertical header pattern found")
            return []

        # Determine the number of header lines
        num_headers = max(header_map.values()) + 1
        data_start = header_start + num_headers

        if debug:
            logger.debug(f"[VERTICAL] Headers span {num_headers} lines, data starts at line {data_start}")

        # Parse items: each item consists of num_headers consecutive data lines
        i = data_start
        item_num = 0

        while i + num_headers <= len(lines):
            data_lines = lines[i:i + num_headers]

            if debug:
                logger.debug(f"[VERTICAL] Parsing item {item_num + 1}, lines {i}-{i + num_headers}: {data_lines}")

            # Try to extract an item from these lines
            item = self._parse_vertical_item(data_lines, header_map, debug=debug)

            if item:
                items.append(item)
                item_num += 1
                i += num_headers
            else:
                # If parsing failed, this might be the end of items section
                # Check if we've hit a total line or other section marker
                stop_keywords = ['ukupno', 'total', 'način', 'račun', 'porez']
                if any(keyword in lines[i].lower() for keyword in stop_keywords):
                    if debug:
                        logger.debug(f"[VERTICAL] Hit section marker at line {i}, stopping: '{lines[i]}'")
                    break

                # Skip this line and try next
                i += 1

        if debug:
            logger.debug(f"[VERTICAL] Extracted {len(items)} items using vertical strategy")

        return items

    def _parse_vertical_item(self, data_lines: List[str], header_map: Dict[str, int], debug: bool = False) -> Optional[Dict[str, Any]]:
        """
        Parse a single item from vertical data lines

        Args:
            data_lines: List of data value lines (same length as header_map)
            header_map: Mapping of header names to their positions
            debug: Enable debug logging
        """
        # Create a mapping of header -> value
        values = {}

        for header, pos in header_map.items():
            if pos < len(data_lines):
                values[header] = data_lines[pos].strip()

        if debug:
            logger.debug(f"[VERTICAL PARSE] Values: {values}")

        # Extract the required fields
        name = values.get('naziv', '').strip()

        # Parse numeric fields
        try:
            price_str = values.get('cijena', '0').strip()
            price = self._parse_number(price_str)

            quantity_str = values.get('kol', '1').strip()
            quantity = self._parse_number(quantity_str)

            total_str = values.get('iznos', '0').strip()
            total = self._parse_number(total_str)

            # Validation: name must exist and be non-numeric
            if not name or self._is_numeric(name):
                if debug:
                    logger.debug(f"[VERTICAL PARSE] Invalid name: '{name}'")
                return None

            # Validation: at least price and total must be valid
            if price <= 0 and total <= 0:
                if debug:
                    logger.debug(f"[VERTICAL PARSE] No valid prices found")
                return None

            # If total is missing but price exists, use price as total
            if total <= 0 and price > 0:
                total = price * quantity

            # If price is missing but total exists, calculate price
            if price <= 0 and total > 0:
                price = total / quantity if quantity > 0 else total

            item = {
                'name': name[:50],
                'quantity': round(quantity, 2),
                'price_per_item': round(price, 2),
                'total': round(total, 2),
                'extraction_method': 'vertical_column'
            }

            if debug:
                logger.debug(f"[VERTICAL PARSE] SUCCESS: {item}")

            return item

        except (ValueError, ZeroDivisionError) as e:
            if debug:
                logger.debug(f"[VERTICAL PARSE] Failed to parse numeric values: {e}")
            return None

    def _parse_number(self, value_str: str) -> float:
        """Parse a number string (handles European decimal format)"""
        if not value_str:
            return 0.0

        # Remove whitespace
        value_str = value_str.strip()

        # Replace comma with dot for European format
        value_str = value_str.replace(',', '.')

        # Try to parse
        try:
            return float(value_str)
        except ValueError:
            return 0.0

    def _is_numeric(self, value: str) -> bool:
        """Check if a string is numeric"""
        try:
            float(value.replace(',', '.'))
            return True
        except ValueError:
            return False
