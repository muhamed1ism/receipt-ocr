"""
Flexible Item Extraction Strategy
=================================
Handles various Croatian receipt formats with flexible line parsing.
"""

import re
import logging
from typing import List, Dict, Optional, Any
from ...text_preprocessing.text_cleaner import TextCleaner
from ...text_preprocessing.pattern_matcher import CroatianPatternMatcher

logger = logging.getLogger(__name__)


class FlexibleItemStrategy:
    """Flexible extraction for various receipt formats"""
    
    def __init__(self):
        self.text_cleaner = TextCleaner()
        self.pattern_matcher = CroatianPatternMatcher()
    
    def looks_like_item_line(self, line: str) -> bool:
        """Check if a line looks like it contains item information"""
        line_clean = line.strip()
        if len(line_clean) < 3:
            return False
        
        # Croatian product indicators
        if re.search(r'\b(kava|čaj|sok|vode|pivo|vino|mlijeko|kruh|meso|riba|sir|jogurt)', line_clean.lower()):
            return True
        
        # Lines with prices
        if re.search(r'\d+[.,]\d{1,2}', line_clean):
            # But not lines that are obviously totals, taxes, or payment info
            excluded_indicators = [
                # Totals
                'ukupno', 'total', 'suma', 'sveukupno', 'povrat', 'priredak',
                # Taxes (Croatian and Bosnian)
                'pdv', 'pnp', 'osn', 've:', 'ue:', 'porez',
                # Payment methods
                'kartica', 'gotovina', 'placeno', 'uplaceno', 'cash', 'card',
                # Footer elements
                'pou:', 'pouee', 'hvala', 'thank'
            ]
            line_lower = line_clean.lower()
            if any(indicator in line_lower for indicator in excluded_indicators):
                return False
            # Also exclude very short lines that are just labels
            if len(line_clean) < 5:
                return False
            return True
        
        # Long enough lines that could be product names
        if len(line_clean) > 6 and not re.match(r'^[\d\s.,:-]+$', line_clean):
            return True
        
        return False
    
    def parse_item_line_flexible(self, line: str, debug: bool = False) -> Optional[Dict[str, Any]]:
        """Parse a single line that might contain item information"""
        line = line.strip()
        if not line or len(line) < 3:
            return None
        
        cleaned = self.text_cleaner.clean_ocr_line(line)
        
        # Extract all potential prices from the line
        price_matches = re.findall(r'(\d+[.,]\d{1,2})', cleaned)
        if not price_matches:
            return None
        
        prices = []
        for price_str in price_matches:
            try:
                price = float(price_str.replace(',', '.'))
                if 0.01 <= price <= 500:
                    prices.append(price)
            except ValueError:
                continue
        
        if not prices:
            return None
        
        # Extract product name (everything before the first price)
        first_price_pos = cleaned.find(price_matches[0].replace('.', ',')) 
        if first_price_pos == -1:
            first_price_pos = cleaned.find(price_matches[0])
        
        if first_price_pos > 0:
            name_part = cleaned[:first_price_pos].strip()
            # Clean up the name
            name_part = re.sub(r'^[\d\s.,:-]+', '', name_part).strip()

            # Skip if name is too short or just noise
            if len(name_part) < 3:
                return None

            # Skip single letter/word junk like "E:", "VE:", "POU:"
            if len(name_part) <= 4 and ':' in name_part:
                return None

            return self.extract_item_from_parts([name_part] + price_matches, debug=debug)
        
        return None
    
    def extract_item_from_parts(self, parts: List[str], debug: bool = False) -> Optional[Dict[str, Any]]:
        """Extract item information from separated parts (name and prices)"""
        if len(parts) < 2:
            return None
        
        name = parts[0].strip()
        price_parts = parts[1:]
        
        if len(name) < 2:
            return None
        
        # Parse prices
        prices = []
        for price_str in price_parts:
            try:
                price = float(price_str.replace(',', '.'))
                if 0.01 <= price <= 500:
                    prices.append(price)
            except ValueError:
                continue
        
        if not prices:
            return None
        
        # Determine quantity, unit price, and total
        # Croatian receipt format: NAME PRICE QUANTITY TOTAL
        if len(prices) == 1:
            # Single price - assume it's the total
            quantity = 1
            unit_price = prices[0]
            total = prices[0]
        elif len(prices) == 2:
            # Two prices - price and total (quantity assumed 1)
            quantity = 1
            unit_price = prices[0]
            total = prices[1]
        elif len(prices) == 3:
            # Three prices - Croatian format: PRICE QUANTITY TOTAL
            unit_price = prices[0]
            quantity = prices[1]
            total = prices[2]

            # Validate: quantity * price should = total (with small tolerance)
            expected_total = unit_price * quantity
            if abs(expected_total - total) > 0.05:
                # Math doesn't add up, fall back to old logic
                total = prices[-1]
                unit_price = prices[-2]
                quantity = total / unit_price if unit_price > 0 else 1
        else:
            # 4+ prices - use last 3: PRICE QUANTITY TOTAL
            unit_price = prices[-3]
            quantity = prices[-2]
            total = prices[-1]
        
        if debug:
            logger.debug(f"    Flexible parse: '{name}' -> Qty: {quantity}, Price: {unit_price}, Total: {total}")
        
        return {
            'name': name[:50],
            'quantity': round(quantity, 2),
            'price_per_item': round(unit_price, 2),
            'total': round(total, 2),
            'extraction_method': 'flexible_line'
        }