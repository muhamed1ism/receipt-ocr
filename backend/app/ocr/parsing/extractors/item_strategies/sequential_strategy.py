"""
Sequential Item Extraction Strategy
==================================
Handles Croatian sequential format: product name, then price details on next line.
"""

import re
import logging
from typing import List, Dict, Optional, Any
from ...text_preprocessing.text_cleaner import TextCleaner
from ...text_preprocessing.pattern_matcher import CroatianPatternMatcher

logger = logging.getLogger(__name__)


class SequentialItemStrategy:
    """Handles Croatian sequential format item extraction"""
    
    def __init__(self):
        self.text_cleaner = TextCleaner()
        self.pattern_matcher = CroatianPatternMatcher()
    
    def extract_items(self, lines: List[str], items_start: int, items_end: int, debug: bool = False) -> List[Dict[str, Any]]:
        """Parse items sequentially following Croatian receipt structure"""
        items = []
        i = items_start
        
        if debug:
            logger.debug(f"[SEQUENTIAL] Processing items from {items_start} to {items_end}")
        
        while i < items_end:
            line = lines[i].strip()
            cleaned = self.text_cleaner.clean_ocr_line(line)
            
            if debug:
                logger.debug(f"  Line {i}: '{line}'")
            
            # Skip empty lines and obvious junk
            if (len(cleaned) < 2 or 
                cleaned.lower() in ['x', 'min', 'ae', 'eur', 'sat'] or
                re.match(r'^[^\w]*$', cleaned)):
                i += 1
                continue
            
            # Try to parse sequential item
            item = self.parse_sequential_item(lines, i, items_end, debug=debug)
            if item:
                items.append(item)
                if debug:
                    logger.debug(f"  SEQUENTIAL ITEM: {item}")
                i += 2  # Skip processed lines (name + price)
            else:
                i += 1
        
        return items
    
    def parse_sequential_item(self, lines: List[str], start_idx: int, end_idx: int, debug: bool = False) -> Optional[Dict[str, Any]]:
        """Parse Croatian sequential format: product name, then price details on next line"""
        if start_idx >= end_idx - 1:  # Need at least 2 lines
            return None
        
        name_line = lines[start_idx].strip()
        price_line = lines[start_idx + 1].strip()
        
        name_cleaned = self.text_cleaner.clean_ocr_line(name_line)
        
        # First line should look like a product name
        if not self.pattern_matcher.looks_like_croatian_product_name(name_cleaned):
            return None
        
        # Second line should contain pricing info
        price_matches = re.findall(r'(\d+[.,]\d{1,2})', price_line)
        if not price_matches:
            return None
        
        # Extract pricing information
        prices = []
        for price_str in price_matches:
            try:
                price = float(price_str.replace(',', '.'))
                if 0.01 <= price <= 1000:
                    prices.append(price)
            except ValueError:
                continue
        
        if not prices:
            return None
        
        # Use logic to determine quantity and unit price
        if len(prices) >= 2:
            # Multiple prices: likely quantity * unit_price = total
            quantity = prices[0]
            unit_price = prices[1]  
            total = prices[-1] if len(prices) > 2 else quantity * unit_price
        else:
            # Single price: assume it's the total
            quantity = 1.0
            unit_price = prices[0]
            total = prices[0]
        
        return {
            'name': name_cleaned[:50],
            'quantity': quantity,
            'price_per_item': unit_price,
            'total': total,
            'extraction_method': 'sequential'
        }