"""
Receipt Validation
==================
Validates overall receipt structure and calculates confidence scores.
"""

from typing import Dict, Any, Optional


class ReceiptValidator:
    """Validates receipt structure and calculates confidence"""
    
    def calculate_confidence(self, store: str, date: Optional[str], 
                           items: list, total: Optional[float]) -> float:
        """Calculate overall receipt parsing confidence"""
        confidence_factors = []
        
        # Store name confidence
        if store and store != "Unknown Store":
            if len(store) > 3:
                confidence_factors.append(0.8)
            else:
                confidence_factors.append(0.5)
        else:
            confidence_factors.append(0.1)
        
        # Date confidence
        if date:
            confidence_factors.append(0.7)
        else:
            confidence_factors.append(0.3)
        
        # Items confidence
        if items:
            if len(items) <= 10:
                confidence_factors.append(0.8)
            else:
                confidence_factors.append(0.5)
        else:
            confidence_factors.append(0.1)
        
        # Total confidence
        if total and total > 0:
            confidence_factors.append(0.7)
        else:
            confidence_factors.append(0.3)
        
        # Calculate average
        return sum(confidence_factors) / len(confidence_factors)
    
    def create_empty_receipt(self, error: str = None) -> Dict[str, Any]:
        """Return empty receipt structure"""
        return {
            "store": "Unknown Store",
            "location_label": None,
            "date": None,
            "time": None,
            "total": None,
            "items": [],
            "confidence": 0.0,
            "error": error,
            "raw_lines_count": 0,
            "parsed_items_count": 0
        }