"""
Item Validation
===============
Validates and cleans parsed items from Croatian receipts.
"""

import logging
from typing import List, Dict, Optional, Any

logger = logging.getLogger(__name__)


class ItemValidator:
    """Validates and cleans parsed receipt items"""
    
    def validate_and_clean_items(self, items: List[Dict[str, Any]], expected_total: Optional[float], debug: bool = False) -> List[Dict[str, Any]]:
        """Remove invalid items that are actually totals or store information"""
        if not items:
            return items
        
        valid_items = []
        
        for item in items:
            item_name = item.get('name', '').lower().strip()
            item_total = item.get('total', 0)
            
            # Remove items that are actually totals
            # BUT: Only if the name looks like a total line (not a product name)
            if expected_total and abs(item_total - expected_total) < 0.01:
                # Check if name looks like a total indicator (not a product)
                total_indicators = ['ukupno', 'total', 'suma', 'sveukupno', 'placanje']
                if any(indicator in item_name for indicator in total_indicators):
                    if debug:
                        logger.debug(f"  REMOVED TOTAL AS ITEM: {item}")
                    continue
                # If it has a valid product name, keep it (might be single-item receipt)
                elif len(item_name) < 3:
                    # Very short name and matches total - probably total line
                    if debug:
                        logger.debug(f"  REMOVED SHORT NAME MATCHING TOTAL: {item}")
                    continue
                else:
                    # Has a decent name, keep it even if total matches
                    if debug:
                        logger.debug(f"  KEPT ITEM (matches total but has valid name): {item}")

            
            # Remove items with names that are obviously not products
            invalid_names = [
                'ukupno', 'ukupn0', 'total', 'suma', 'placanje', 'novcanice',  # Added ukupn0 (OCR error)
                'racun', 'ra0un', 'broj', 'datum', 'konobar', 'sto', 'stol',  # Added OCR variants
                'porez', 'pdv', 'osnovica', 'stopa', 'iznos', 'izn0s',
                '(eur)', 'eur:', 'kuna', 'hrk',  # Currency indicators
                'ae', 's 555 5e', 'd8c', 'odbc bob',  # OCR artifacts
                'jena k', 'na', 'izr', 'sgrgggavo'  # More OCR junk
            ]
            
            if any(invalid in item_name for invalid in invalid_names):
                if debug:
                    logger.debug(f"  REMOVED INVALID NAME: {item}")
                continue
            
            # Remove items with unreasonable values
            if (item.get('quantity', 0) <= 0 or 
                item.get('price_per_item', 0) <= 0 or
                item.get('total', 0) <= 0):
                if debug:
                    logger.debug(f"  REMOVED ZERO/NEGATIVE VALUES: {item}")
                continue
            
            # Remove items with excessive values
            if (item.get('quantity', 0) > 100 or
                item.get('price_per_item', 0) > 500 or
                item.get('total', 0) > 1000):
                if debug:
                    logger.debug(f"  REMOVED EXCESSIVE VALUES: {item}")
                continue
            
            # Validate math consistency
            quantity = item.get('quantity', 1)
            price_per_item = item.get('price_per_item', 0)
            total = item.get('total', 0)
            
            expected_total_calc = quantity * price_per_item
            if abs(expected_total_calc - total) > 0.02:  # Allow small rounding errors
                if debug:
                    logger.debug(f"  MATH ERROR - Expected: {expected_total_calc}, Got: {total} for item: {item}")
                # Try to fix if possible
                if quantity > 0:
                    corrected_price = total / quantity
                    item['price_per_item'] = round(corrected_price, 2)
                    if debug:
                        logger.debug(f"  CORRECTED price_per_item to: {corrected_price}")
            
            # Remove items with names that are too short or just numbers
            name = item.get('name', '').strip()
            if len(name) < 2 or name.isdigit():
                if debug:
                    logger.debug(f"  REMOVED SHORT/NUMERIC NAME: {item}")
                continue
            
            valid_items.append(item)
        
        if debug:
            logger.debug(f"[VALIDATION] Kept {len(valid_items)}/{len(items)} items")
        
        return valid_items
    
    def calculate_items_confidence(self, items: List[Dict[str, Any]], expected_total: Optional[float]) -> float:
        """Calculate confidence score for extracted items"""
        if not items:
            return 0.0
        
        confidence_factors = []
        
        # Factor 1: Item count (reasonable number of items)
        item_count = len(items)
        if 1 <= item_count <= 10:
            confidence_factors.append(0.8)
        elif 11 <= item_count <= 20:
            confidence_factors.append(0.6)
        else:
            confidence_factors.append(0.3)
        
        # Factor 2: Total match (if we have expected total)
        if expected_total:
            calculated_total = sum(item.get('total', 0) for item in items)
            total_diff = abs(calculated_total - expected_total)
            
            if total_diff < 0.01:
                confidence_factors.append(1.0)  # Perfect match
            elif total_diff < 1.0:
                confidence_factors.append(0.8)  # Close match
            elif total_diff < 5.0:
                confidence_factors.append(0.5)  # Reasonable match
            else:
                confidence_factors.append(0.2)  # Poor match
        
        # Factor 3: Item name quality
        name_quality = 0.0
        for item in items:
            name = item.get('name', '').strip()
            if len(name) >= 5:
                name_quality += 0.3
            if any(char.isalpha() for char in name):
                name_quality += 0.2
        
        name_quality = min(name_quality / len(items), 1.0) if items else 0.0
        confidence_factors.append(name_quality)
        
        # Factor 4: Math consistency
        math_consistency = 0.0
        for item in items:
            quantity = item.get('quantity', 1)
            price_per_item = item.get('price_per_item', 0)
            total = item.get('total', 0)
            
            expected = quantity * price_per_item
            if abs(expected - total) < 0.02:
                math_consistency += 1.0
        
        math_consistency = math_consistency / len(items) if items else 0.0
        confidence_factors.append(math_consistency)
        
        # Calculate weighted average
        return sum(confidence_factors) / len(confidence_factors) if confidence_factors else 0.0