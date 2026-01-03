"""
OCR Text Cleaning Utilities
===========================
Handles OCR corruption and noise removal from Croatian receipt text.
"""

import re


class TextCleaner:
    """Handles OCR text cleaning and corruption fixes"""
    
    def __init__(self):
        """Initialize text cleaner - SIMPLIFIED to not interfere with OCR corrections"""
        # NOTE: We removed the letter-to-number substitutions (O->0, l->1, o->0)
        # because the OCR coordinator already does smart corrections in the opposite direction
        # and we were undoing those corrections!
        pass
    
    def clean_ocr_line(self, line: str) -> str:
        """Clean OCR corruption from a line of text"""
        if not line:
            return line
        
        cleaned = line
        
        # Remove excessive repeated characters (OCR artifacts)
        cleaned = re.sub(r'(.)\1{3,}', r'\1\1', cleaned)
        
        # Clean obvious OCR noise patterns (but DON'T mess with letters vs numbers!)
        cleaned = re.sub(r'[đĐ]{2,}', 'd', cleaned)  # Multiple croatian chars
        # UPDATED: Preserve + symbol for product names like "PILE+COCA COLA"
        cleaned = re.sub(r'[^a-zA-ZčćžšđĆČŽŠĐ0-9\s.,:\-€()+]+', '', cleaned)  # Remove weird chars but keep +

        # NOTE: We removed the letter/number substitutions - those are handled by OCR correction now
        
        # Clean up whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        return cleaned