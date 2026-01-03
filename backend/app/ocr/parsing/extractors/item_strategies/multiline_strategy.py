"""
Multiline Item Extraction Strategy
==================================
Handles items that span multiple lines in Croatian receipts.
"""

import re
import logging
from typing import List, Dict, Optional, Any, Tuple
from ...text_preprocessing.text_cleaner import TextCleaner
from ...text_preprocessing.pattern_matcher import CroatianPatternMatcher

logger = logging.getLogger(__name__)


class MultilineItemStrategy:
    """Handles items that span multiple lines"""

    def __init__(self):
        self.text_cleaner = TextCleaner()
        self.pattern_matcher = CroatianPatternMatcher()

    def parse_bosnian_3line_item(self, items_section: List[str], start_idx: int, debug: bool = False) -> Optional[Dict[str, Any]]:
        """
        Parse Bosnian 3-line/4-line item formats:

        FORMAT 3 (Merged - MOST COMMON after text merging):
        Line N:   ITEM NAME + TOTAL (e.g., "P04130UBRUSPAPIRN2SL1KOMPALOMA    4.40E")
        Line N+1: QUANTITY + UNIT PRICE (e.g., "1.000x    4.40")

        FORMAT 1 (Simple - bosnian1.jpg):
        Line N:   ITEM NAME (e.g., "PILECOCA COLA.O.5")
        Line N+1: QUANTITY with 'x' (e.g., "1.008x")
        Line N+2: TOTAL PRICE (e.g., "7.95")

        FORMAT 2 (Common - bosnian3.jpg):
        Line N:   ITEM NAME (e.g., "P04130UBRUSPAPIRN2SL1KOMPALOMA")
        Line N+1: TOTAL with 'E' suffix (e.g., "4.40E")
        Line N+2: QUANTITY with 'x' (e.g., "1.000x")
        Line N+3: UNIT PRICE or repeated total (e.g., "4.40")
        """
        if start_idx >= len(items_section) - 1:
            return None

        line1 = items_section[start_idx].strip()
        line2 = items_section[start_idx + 1].strip()

        # CHECK FORMAT 3: 2-Line format (Name, Qty+Unit+Total)
        # Most common format after text merging
        # Line 1: "PILE+COCA COLA O.5L" (name only)
        # Line 2: "1.000x 7.95 7.95E" (quantity, unit price, total with E)

        # Line2 should have: "QTYx    UNIT_PRICE    TOTALE"
        # Pattern: quantity with x, then numbers, ending with E
        qty_unit_total_match = re.search(r'^(\d+[.,]?\d*)x\s+(\d+[.,]?\d+)\s+(\d+[.,]?\d*)E\s*$', line2, re.IGNORECASE)
        if qty_unit_total_match:
            quantity = float(qty_unit_total_match.group(1).replace(',', '.'))
            unit_price = float(qty_unit_total_match.group(2).replace(',', '.'))
            total_price = float(qty_unit_total_match.group(3).replace(',', '.'))

            # Validate price range
            if not (0.01 <= total_price <= 10000):
                return None

            # Clean name from line1
            name_cleaned = self.text_cleaner.clean_ocr_line(line1)

            # Validate calculation: qty * unit ≈ total (allow 0.50 tolerance)
            calculated_total = quantity * unit_price
            if abs(calculated_total - total_price) > 0.50:
                if debug:
                    logger.debug(f"[BOSNIAN FORMAT3] Calculation mismatch: {quantity} x {unit_price} = {calculated_total:.2f} vs {total_price}")
                # Still accept if close enough (OCR errors in unit price)
                if abs(calculated_total - total_price) > 1.00:
                    return None

            if debug:
                logger.debug(f"[BOSNIAN FORMAT3] Name: '{name_cleaned}', Qty: {quantity}x, Unit: {unit_price}, Total: {total_price}E")

            return {
                'name': name_cleaned[:50],
                'quantity': round(quantity, 3),
                'price_per_item': round(unit_price, 2),
                'total': round(total_price, 2),
                'extraction_method': 'bosnian_3line',  # Keep same method name for compatibility
                'lines_consumed': 2  # Format 3 uses 2 lines
            }

        # Continue with existing formats if Format 3 doesn't match
        if start_idx >= len(items_section) - 2:
            return None

        line3 = items_section[start_idx + 2].strip()

        # CHECK FORMAT 2: Name, Total(E), Quantity(x), Price
        # Look for "E" suffix on line2 (e.g., "4.40E", "30.95E")
        total_e_match = re.search(r'^(\d+[.,]?\d*)E\s*$', line2, re.IGNORECASE)
        if total_e_match:
            # Line2 is total with E suffix
            total_price = float(total_e_match.group(1).replace(',', '.'))

            # Line3 should be quantity with 'x'
            qty_match = re.search(r'^(\d+[.,]?\d*)x\s*$', line3, re.IGNORECASE)
            if not qty_match:
                return None  # Not Bosnian format

            quantity = float(qty_match.group(1).replace(',', '.'))

            # Validate price range
            if not (0.01 <= total_price <= 10000):
                return None

            # Clean name
            name_cleaned = self.text_cleaner.clean_ocr_line(line1)

            # Calculate unit price
            unit_price = total_price / quantity if quantity > 0 else total_price

            if debug:
                logger.debug(f"[BOSNIAN FORMAT2] Name: '{name_cleaned}', Total: {total_price}E, Qty: {quantity}x, Unit: {unit_price:.2f}")

            return {
                'name': name_cleaned[:50],
                'quantity': round(quantity, 3),
                'price_per_item': round(unit_price, 2),
                'total': round(total_price, 2),
                'extraction_method': 'bosnian_3line',
                'lines_consumed': 4  # Format 2 uses 4 lines (Name, Total(E), Qty(x), Unit)
            }

        # CHECK FORMAT 1: Name, Quantity(x), Total
        qty_match = re.search(r'^(\d+[.,]?\d*)x\s*$', line2, re.IGNORECASE)
        if not qty_match:
            return None  # Not Bosnian format

        quantity = float(qty_match.group(1).replace(',', '.'))

        # Extract price from line3 (should be just a number)
        price_match = re.search(r'^(\d+[.,]\d{1,2})\s*$', line3)
        if not price_match:
            return None

        total_price = float(price_match.group(1).replace(',', '.'))

        # Validate price range
        if not (0.01 <= total_price <= 10000):
            return None

        # Clean name
        name_cleaned = self.text_cleaner.clean_ocr_line(line1)

        # Calculate unit price
        unit_price = total_price / quantity if quantity > 0 else total_price

        if debug:
            logger.debug(f"[BOSNIAN FORMAT1] Name: '{name_cleaned}', Qty: {quantity}x, Total: {total_price}, Unit: {unit_price:.2f}")

        return {
            'name': name_cleaned[:50],
            'quantity': round(quantity, 3),
            'price_per_item': round(unit_price, 2),
            'total': round(total_price, 2),
            'extraction_method': 'bosnian_3line',
            'lines_consumed': 3  # Format 1 uses 3 lines (Name, Qty(x), Total)
        }

    def parse_multiline_item(self, items_section: List[str], start_idx: int, debug: bool = False) -> Optional[Dict[str, Any]]:
        """Parse items that span multiple lines (name on one line, details on others)"""
        if start_idx >= len(items_section) - 1:
            return None

        # Try Bosnian 3-line format first (most specific pattern)
        bosnian_item = self.parse_bosnian_3line_item(items_section, start_idx, debug=debug)
        if bosnian_item:
            return bosnian_item

        name_line = items_section[start_idx].strip()
        name_cleaned = self.text_cleaner.clean_ocr_line(name_line)

        # Must look like a product name
        if not self.pattern_matcher.looks_like_croatian_product_name(name_cleaned):
            return None
        
        # Look for prices in the next 2-3 lines
        prices_found = []
        for j in range(start_idx + 1, min(start_idx + 4, len(items_section))):
            line = items_section[j].strip()
            price_matches = re.findall(r'(\d+[.,]\d{1,2})', line)
            
            for price_str in price_matches:
                try:
                    price = float(price_str.replace(',', '.'))
                    if 0.01 <= price <= 1000:
                        prices_found.append((j, price, line))
                except ValueError:
                    continue
        
        if not prices_found:
            return None
        
        return self.build_item_from_multiline(name_line, prices_found, debug=debug)
    
    def build_item_from_multiline(self, name_line: str, prices_found: List[Tuple[int, float, str]], debug: bool = False) -> Optional[Dict[str, Any]]:
        """Build item from name line and found prices"""
        if not prices_found:
            return None
        
        name_cleaned = self.text_cleaner.clean_ocr_line(name_line)
        
        # Sort prices by line number
        prices_found.sort(key=lambda x: x[0])
        
        if len(prices_found) == 1:
            # Single price found
            _, price, _ = prices_found[0]
            return {
                'name': name_cleaned[:50],
                'quantity': 1.0,
                'price_per_item': price,
                'total': price,
                'extraction_method': 'multiline_single'
            }
        
        elif len(prices_found) >= 2:
            # Multiple prices - analyze the pattern
            # Common Croatian pattern: quantity, unit_price, total
            prices = [p[1] for p in prices_found]
            
            # Strategy: use last price as total, previous as unit price
            total = prices[-1]
            unit_price = prices[-2]
            
            # Try to find quantity
            quantity = 1.0
            if len(prices) >= 3:
                potential_qty = prices[0]
                if potential_qty < 20:  # Reasonable quantity
                    quantity = potential_qty
            
            # Validate calculation
            if abs(quantity * unit_price - total) > 0.02:
                # Try different combinations
                if len(prices) >= 2:
                    quantity = total / unit_price if unit_price > 0 else 1.0
                    if quantity > 100:  # Unreasonable quantity
                        quantity = 1.0
                        unit_price = total
            
            if debug:
                logger.debug(f"    Multiline item: '{name_cleaned}'")
                logger.debug(f"    Prices found: {prices}")
                logger.debug(f"    Final: Qty={quantity}, Price={unit_price}, Total={total}")
            
            return {
                'name': name_cleaned[:50],
                'quantity': round(quantity, 2),
                'price_per_item': round(unit_price, 2),
                'total': round(total, 2),
                'extraction_method': 'multiline_complex'
            }
        
        return None
    
    def extract_item_from_prices(self, name: str, prices: List[float], debug: bool = False) -> Optional[Dict[str, Any]]:
        """Extract item information when we have a name and list of prices"""
        if not prices:
            return None
        
        name_cleaned = self.text_cleaner.clean_ocr_line(name)
        if len(name_cleaned) < 2:
            return None
        
        if len(prices) == 1:
            # Single price
            price = prices[0]
            return {
                'name': name_cleaned[:50],
                'quantity': 1.0,
                'price_per_item': price,
                'total': price,
                'extraction_method': 'price_single'
            }
        
        elif len(prices) == 2:
            # Two prices - could be unit price and total, or quantity and total
            if prices[0] < 20 and prices[1] > prices[0]:
                # First looks like quantity
                quantity = prices[0]
                total = prices[1]
                unit_price = total / quantity if quantity > 0 else total
            else:
                # First is unit price, second is total
                quantity = 1.0
                unit_price = prices[0]
                total = prices[1]
        
        else:
            # Multiple prices - use heuristics
            # Often: quantity, unit_price, ... , total
            total = prices[-1]  # Last is usually total
            
            if prices[0] < 20:  # First could be quantity
                quantity = prices[0]
                unit_price = prices[1] if len(prices) > 1 else total
            else:
                quantity = 1.0
                unit_price = prices[0]
        
        # Validation
        if abs(quantity * unit_price - total) > 0.05:  # Allow small rounding
            if unit_price > 0:
                quantity = round(total / unit_price, 2)
            else:
                quantity = 1.0
                unit_price = total
        
        if debug:
            logger.debug(f"    Extract from prices: '{name_cleaned}' -> Qty={quantity}, Price={unit_price}, Total={total}")
        
        return {
            'name': name_cleaned[:50],
            'quantity': round(quantity, 2),
            'price_per_item': round(unit_price, 2),
            'total': round(total, 2),
            'extraction_method': 'price_analysis'
        }