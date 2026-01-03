"""
Fallback Item Extraction Strategy
=================================
Simple pattern matching for item extraction when other methods fail.
"""

import re
import logging
from typing import List, Dict, Any
from ...text_preprocessing.text_cleaner import TextCleaner
from ...text_preprocessing.pattern_matcher import CroatianPatternMatcher

logger = logging.getLogger(__name__)


class FallbackItemStrategy:
    """Fallback extraction method using simple pattern matching"""
    
    def __init__(self):
        self.text_cleaner = TextCleaner()
        self.pattern_matcher = CroatianPatternMatcher()
    
    def extract_items(self, lines: List[str], debug: bool = False) -> List[Dict[str, Any]]:
        """Fallback extraction method using simple pattern matching"""
        items = []
        
        # Find lines that look like Croatian product names with nearby prices
        for i, line in enumerate(lines):
            line_clean = line.strip()
            cleaned_line = self.text_cleaner.clean_ocr_line(line_clean)
            
            # Look for Croatian product-like patterns
            if not self.pattern_matcher.looks_like_croatian_product_name(cleaned_line):
                continue
            
            # Search for prices in the next few lines
            prices_nearby = []
            for j in range(i, min(i + 4, len(lines))):
                price_matches = re.findall(r'(\d+[.,]\d{1,2})', lines[j])
                for match in price_matches:
                    try:
                        price = float(match.replace(',', '.'))
                        if 0.1 <= price <= 500:  # Reasonable price range
                            prices_nearby.append(price)
                    except ValueError:
                        continue
            
            if prices_nearby:
                # Use the first reasonable price found
                price = prices_nearby[0]
                item = {
                    'name': cleaned_line,
                    'price': price,
                    'quantity': 1.0,
                    'total': price,
                    'extraction_method': 'fallback_pattern_matching'
                }
                items.append(item)
                if debug:
                    logger.debug(f"  FALLBACK ITEM: {item}")
        
        return items