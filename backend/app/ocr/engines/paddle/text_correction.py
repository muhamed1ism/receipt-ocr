"""
Croatian Text Correction
========================
Advanced text cleaning and OCR error correction for Croatian receipts.
"""

import re


class CroatianTextCorrector:
    """Handles Croatian-specific text cleaning and OCR error correction"""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """
        ENHANCED Croatian text cleaning - preserves valuable text while filtering noise.
        Smarter filtering based on Croatian receipt patterns.
        """
        if not text:
            return ""
        
        # Process line by line to preserve structure
        lines = text.split('\n')
        cleaned_lines = []
        
        # Croatian receipt keywords that should always be preserved
        important_croatian_words = [
            'kava', 'kapućino', 'caffe', 'bar', 'restoran', 'pekara', 'market',
            'jamnica', 'konzum', 'tommy', 'spar', 'kaufland', 'lidl', 'plodine',
            'ukupno', 'suma', 'račun', 'bon', 'datum', 'vrijeme', 'konobar',
            'način', 'plaćanja', 'novčanice', 'porez', 'pdv', 'stopa', 'osnovica',
            'hvala', 'povjerenju', 'mlijeko', 'velik', 'mali', 'okusi'
        ]
        
        for line in lines:
            if not line.strip():
                continue
                
            line = line.strip()
            line_lower = line.lower()
            
            # Skip obvious noise lines first
            # Lines with >70% repetitive characters (OOOOO, BBBBB, etc.)
            if len(line) > 5:
                char_counts = {}
                for char in line:
                    char_counts[char] = char_counts.get(char, 0) + 1
                max_char_count = max(char_counts.values()) if char_counts else 0
                if max_char_count > len(line) * 0.7:
                    continue
            
            # Skip lines that are mostly repeated character patterns
            if re.match(r'^[OGBD\s]{8,}$', line) or re.match(r'^[ODB\s]{8,}$', line):
                continue
                
            # Preserve lines with Croatian words (PRIORITY)
            has_croatian_word = any(word in line_lower for word in important_croatian_words)
            if has_croatian_word:
                # Light cleaning for Croatian lines
                line = re.sub(r'\s+', ' ', line).strip()
                cleaned_lines.append(line)
                continue
            
            # Preserve lines with prices (format: digits.digits)
            if re.search(r'\d+[.,]\d{1,2}', line):
                line = re.sub(r'\s+', ' ', line).strip()
                cleaned_lines.append(line)
                continue
                
            # Preserve lines with dates
            if re.search(r'\d{1,2}[./-]\d{1,2}[./-]\d{2,4}', line):
                line = re.sub(r'\s+', ' ', line).strip()
                cleaned_lines.append(line)
                continue
                
            # Preserve lines with times
            if re.search(r'\d{1,2}:\d{2}', line):
                line = re.sub(r'\s+', ' ', line).strip()
                cleaned_lines.append(line)
                continue
            
            # For other lines, apply quality filtering
            # Skip lines with excessive corruption (>50% non-word characters)
            word_chars = len(re.findall(r'[a-zA-ZčćžšđĆČŽŠĐ0-9\s]', line))
            total_chars = len(line)
            if total_chars > 0 and word_chars / total_chars < 0.5:
                continue
                
            # Skip very short lines that aren't important
            if len(line) < 3:
                continue
                
            # Skip lines that are mostly uppercase nonsense
            if len(line) > 10 and line.isupper() and not has_croatian_word:
                # Check if it's meaningful uppercase (like store names)
                if not re.search(r'\b[A-Z]{2,}\b.*\b[A-Z]{2,}\b', line):
                    continue
            
            # Apply basic fixes to remaining lines
            # Add space between number and letters
            line = re.sub(r'(\d)([A-Za-zčćžšđĆČŽŠĐ]{2,})', r'\1 \2', line)
            # Add space between letters and numbers  
            line = re.sub(r'([A-Za-zčćžšđĆČŽŠĐ])(\d{2,})', r'\1 \2', line)
            # Clean excessive whitespace
            line = re.sub(r'\s+', ' ', line).strip()
            
            # Final check - only add if it has some meaningful content
            if len(line) >= 2 and not re.match(r'^[^\w\s]+$', line):
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)

    @staticmethod
    def correct_croatian_ocr_errors(text: str) -> str:
        """
        Correct common OCR character recognition errors.

        IMPORTANT: Minimal corrections only! PaddleOCR's Latin dictionary already
        handles Croatian/Bosnian text well. Aggressive corrections were causing
        more harm than good by corrupting correct OCR output.

        Examples of previous problems:
        - "KONZUM" was becoming "KONžUM" (wrong!)
        - "SARAJEVO" was becoming "šARAJEVO" (wrong!)
        - Bosnian receipts use standard Latin (s, z, d) not Croatian special chars
        """
        if not text:
            return text

        corrected_text = text

        # MINIMAL CORRECTIONS: Only fix obvious OCR mistakes
        # Fix d.0.0 -> d.o.o (common company suffix)
        corrected_text = re.sub(r'\.0(?=\.|\b)', '.o', corrected_text)  # .0. or .0 -> .o

        # That's it! PaddleOCR does a good job, don't over-correct.
        # If specific issues are found in production, add targeted fixes here.

        return corrected_text

    @staticmethod
    def clean_item_name_simple(name: str) -> str:
        """
        Simple item name cleaning - ASCII-safe version

        UPDATED: Preserve + symbols and product details like "0.5" in "COCA COLA 0.5"
        """
        if not name:
            return name

        # Remove ONLY leading/trailing whitespace and punctuation (preserve + and product sizes)
        # Don't remove + symbols (common in product names like "PILE+COCA COLA")
        # Don't remove numbers at the end (product sizes like "0.5", "1.5L")
        name = re.sub(r'^[\s.,;:-]+', '', name)  # Remove leading punctuation only
        name = re.sub(r'[\s.,;:-]+$', '', name)  # Remove trailing punctuation only

        # Basic cleanup - normalize whitespace
        name = re.sub(r'\s+', ' ', name).strip()

        return name