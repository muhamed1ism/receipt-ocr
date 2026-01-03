"""
Receipt Quality Scoring
======================
Scoring functions for parsed Croatian receipt data quality.
"""

import re
import logging

logger = logging.getLogger(__name__)


class ReceiptScorer:
    """Handles scoring of parsed Croatian receipt data"""
    
    def __init__(self):
        self.croatian_stores = [
            'konzum', 'tommy', 'spar', 'kaufland', 'lidl', 'plodine', 
            'ina', 'omv', 'lukoil', 'mol', 'interspar', 'studenac'
        ]
    
    def score_receipt_quality(self, parsed_data: dict) -> float:
        """
        Score parsed Croatian receipt data quality.
        Returns confidence score between 0.0 and 1.0.
        """
        if not parsed_data:
            return 0.0
        
        confidence = 0.0
        
        # Store name quality
        store = parsed_data.get('store', '')
        if store and store != 'Nepoznata trgovina':
            confidence += 0.2
            
            # Bonus for Croatian store patterns
            if any(pattern in store.lower() for pattern in self.croatian_stores):
                confidence += 0.1
        
        # Date quality
        date = parsed_data.get('date')
        if date:
            confidence += 0.15
            if re.match(r'\d{4}-\d{2}-\d{2}', date):
                confidence += 0.05
        
        # Items quality
        items = parsed_data.get('items', [])
        if items:
            confidence += 0.3
            
            # Quality of item names
            good_items = sum(1 for item in items if len(item.get('name', '')) > 3)
            item_quality = good_items / len(items) if items else 0
            confidence += item_quality * 0.1
            
            # Multiple items bonus
            if len(items) > 1:
                confidence += 0.05
        
        # Total amount quality
        total = parsed_data.get('total')
        if total and total > 0:
            confidence += 0.2
            
            # Check if total matches items
            if items:
                calculated_total = sum(item.get('total', 0) for item in items)
                if abs(calculated_total - total) <= 0.02:  # Allow small rounding
                    confidence += 0.1
        
        return min(confidence, 1.0)  # Cap at 1.0
    
    def validate_receipt_structure(self, parsed_data: dict) -> dict:
        """Validate and return issues with receipt structure"""
        issues = []
        
        if not parsed_data.get('store'):
            issues.append("Missing store name")
        
        if not parsed_data.get('date'):
            issues.append("Missing date")
        
        if not parsed_data.get('items'):
            issues.append("No items found")
        elif len(parsed_data.get('items', [])) == 0:
            issues.append("Empty items list")
        
        if not parsed_data.get('total'):
            issues.append("Missing total amount")
        
        # Cross-validation
        items = parsed_data.get('items', [])
        total = parsed_data.get('total', 0)
        
        if items and total:
            calculated_total = sum(item.get('total', 0) for item in items)
            if abs(calculated_total - total) > 1.0:  # Allow some tolerance
                issues.append(f"Total mismatch: calculated {calculated_total}, found {total}")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'confidence': self.score_receipt_quality(parsed_data)
        }


# Backward compatibility function
def score_croatian_receipt_quality(parsed_data: dict) -> float:
    """Backward compatibility wrapper for receipt quality scoring"""
    scorer = ReceiptScorer()
    return scorer.score_receipt_quality(parsed_data)