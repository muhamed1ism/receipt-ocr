"""
Croatian Pattern Matching
=========================
Detects Croatian receipt patterns with OCR corruption tolerance.
"""

import re
from .text_cleaner import TextCleaner


class CroatianPatternMatcher:
    """Detects Croatian-specific patterns in OCR text"""
    
    def __init__(self):
        """Initialize pattern matcher with text cleaner"""
        self.text_cleaner = TextCleaner()
    
    def fuzzy_match_croatian_patterns(self, line: str) -> bool:
        """Check if line matches Croatian receipt patterns with OCR corruption tolerance"""
        line_lower = line.lower().strip()
        cleaned_line = self.text_cleaner.clean_ocr_line(line_lower)
        
        # Croatian column headers with OCR variations
        header_patterns = [
            # Original + common OCR corruptions
            r'naz[ij]v',  # naziv, naziv  
            r'[nc][ij]jena',  # cijena, njena, cijjena
            r'[kc]ol',  # kol
            r'[ij]znos',  # iznos
            # Combined header patterns
            r'naz[ij]v.*[nc][ij]jena',
            r'naz[ij]v.*kol.*[ij]znos',
        ]
        
        for pattern in header_patterns:
            if re.search(pattern, cleaned_line):
                return True
                
        return False
    
    def looks_like_croatian_product_name(self, line: str) -> bool:
        """Check if line looks like a Croatian product name"""
        line_clean = line.lower().strip()
        if len(line_clean) < 2:
            return False
        
        # Croatian product indicators
        croatian_indicators = [
            # Food/drink categories
            r'kava|cokolada|sir|mlijeko|jogurt|kruh|mesa|riba',
            r'pivo|vino|sok|voda|tea|cola|pepsi',
            r'jabuka|banana|naranc|limun|groz|jagod',
            # Common Croatian prefixes/suffixes
            r'[a-z]+ski|[a-z]+cki|[a-z]+ni|[a-z]+na',
            # Measurement units
            r'kg|gr|kom|lit|ml|kut',
            # Common product words
            r'veliki|mali|bijeli|crni|fresh|novo'
        ]
        
        for pattern in croatian_indicators:
            if re.search(pattern, line_clean):
                return True
        
        # General Croatian text pattern (more consonants, specific letter combinations)
        if (re.search(r'[čćžšđ]', line_clean) or  # Croatian diacritics
            len(re.findall(r'[bcdfghjklmnpqrstvwxz]', line_clean)) > len(line_clean) * 0.4):
            return True
            
        return False