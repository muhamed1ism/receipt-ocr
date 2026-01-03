"""
OCR Text Quality Scoring
=======================
Scoring functions for OCR text quality assessment.
"""

import re
import logging

logger = logging.getLogger(__name__)


class OCRTextScorer:
    """Handles OCR text quality scoring"""
    
    def __init__(self):
        self.croatian_business_words = [
            'caffe', 'bar', 'restoran', 'pekara', 'market', 'trgovina', 
            'konzum', 'tommy', 'spar', 'kaufland', 'lidl', 'plodine',
            'ina', 'omv', 'lukoil', 'mol', 'ljekarna', 'apoteka',
            'dućan', 'prodavaonica', 'kavana'
        ]
        
        self.croatian_receipt_words = [
            'ukupno', 'suma', 'račun', 'bon', 'datum', 'vrijeme',
            'pdv', 'porez', 'blagajna', 'kasa', 'operater'
        ]
    
    def score_text(self, text: str) -> int:
        """
        Croatian-specific OCR text scoring function.
        Higher scores indicate better OCR quality for Croatian receipts.
        """
        if not text or len(text.strip()) < 5:
            return 0
        
        lines = [line for line in text.split('\n') if len(line.strip()) > 2]
        
        # Base score from number of meaningful lines
        score = len(lines) * 1
        
        # Price detection (Croatian decimal format)
        price_hits = sum(bool(re.search(r'\d+[,.]\d{2}', line)) for line in lines)
        score += price_hits * 2
        
        # Croatian store/business words
        has_croatian_business = any(word in text.lower() for word in self.croatian_business_words)
        if has_croatian_business:
            score += 3
        
        # Croatian receipt keywords
        croatian_keyword_hits = sum(1 for word in self.croatian_receipt_words if word in text.lower())
        score += croatian_keyword_hits * 1
        
        # Date pattern (Croatian format DD.MM.YYYY or DD.MM.YY)
        if re.search(r'\d{1,2}\.\d{1,2}\.\d{2,4}', text):
            score += 3
        
        # Time pattern (HH:MM or HH.MM)
        if re.search(r'\d{1,2}[:.]\d{2}', text):
            score += 2
        
        # Receipt formatting patterns
        if re.search(r'-{3,}|={3,}', text):  # Separator lines
            score += 2
        
        # Long coherent words (sign of good OCR)
        long_words = re.findall(r'\b\w{6,}\b', text)
        score += min(len(long_words), 10)  # Cap at 10 bonus points
        
        # Penalty for too much gibberish
        words = re.findall(r'\b\w+\b', text.lower())
        if words:
            short_words = [w for w in words if len(w) <= 2]
            gibberish_ratio = len(short_words) / len(words)
            if gibberish_ratio > 0.5:
                score -= 5
        
        # Bonus for multiple price entries (typical for receipts)
        if price_hits >= 3:
            score += 5
        
        return max(score, 0)  # Ensure non-negative score


# Backward compatibility function
def score_ocr_text(text: str) -> int:
    """Backward compatibility wrapper for OCR text scoring"""
    scorer = OCRTextScorer()
    return scorer.score_text(text)