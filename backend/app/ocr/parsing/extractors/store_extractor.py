"""
Store Information Extractor
===========================
Extracts store name and address information from Croatian receipts.
"""

import re
from typing import List
from ..text_preprocessing.text_cleaner import TextCleaner


class StoreExtractor:
    """Extracts store information from receipt text"""
    
    def __init__(self):
        """Initialize store extractor with text cleaner"""
        self.text_cleaner = TextCleaner()
    
    def detect_croatian_address(self, line: str) -> bool:
        """Detect Croatian address patterns (street, zipcode city)"""
        line_clean = self.text_cleaner.clean_ocr_line(line)

        # Croatian address patterns
        # OCR often misreads: 21000 → 210oo, 21000 → 2l000, etc.
        address_patterns = [
            r'.*,\s*\d{5}\s+\w+',  # street, 21000 Split
            r'.*\d+,\s*\d{5}\s+\w+',  # street 23, 21000 Split
            r'.*\s+\d+.*\d{5}.*\w+',  # flexible address format
            r'.*,\s*\d{3}[o0]{2}\s+',  # OCR error: 210oo or 2l000
            r'.*(obala|ulica|cesta|trg|avenija).*\d+',  # Street type + number
        ]

        for pattern in address_patterns:
            if re.search(pattern, line_clean, re.IGNORECASE):
                return True
        return False
    
    def find_store_name_from_address(self, lines: List[str], address_idx: int) -> str:
        """Find store name by looking backward from address"""
        # Look backward from address to find store name
        for i in range(address_idx - 1, max(0, address_idx - 5), -1):
            line = lines[i].strip()
            cleaned = self.text_cleaner.clean_ocr_line(line)
            
            # Skip descriptors like "čaffe bar"
            if cleaned.lower() in ['caffe bar', 'caffe', 'bar', 'restoran', 'pekara']:
                continue
                
            # Skip obvious junk
            if (len(cleaned) < 2 or 
                re.match(r'^\W*$', cleaned) or  # Only symbols
                cleaned.lower() in ['po', 'ze', 'ni', 'ce']):
                continue
            
            # Clean up quotes and symbols
            cleaned = cleaned.strip('"').strip("'").strip()
            
            # If it looks like a store name
            if (len(cleaned) >= 3 and 
                re.search(r'[a-zA-ZčćžšđĆČŽŠĐ]{2,}', cleaned) and
                len(cleaned) <= 30):
                return cleaned
        
        return "Unknown Store"
    
    def extract_store_name_from_wifi(self, lines: List[str]) -> str:
        """
        Extract store name from WiFi line (fallback method).

        Many receipts have WiFi info like:
        - "WIFI: CAFFE BAR \"MX\""
        - "WI-FI: retro 1234"

        Returns store name or None if not found.
        """
        for line in lines:
            line_lower = line.lower()

            # Look for WiFi pattern
            if 'wifi' in line_lower or 'wi-fi' in line_lower:
                # Extract everything after "wifi:" or "wi-fi:" (use original line for case preservation)
                match = re.search(r'wi-?fi\s*:\s*(.+)', line, re.IGNORECASE)
                if match:
                    wifi_content = match.group(1).strip()

                    # Remove password/numbers at end
                    # "retro 1234" → "retro"
                    wifi_content = re.sub(r'\s+\d{4,}$', '', wifi_content)

                    # Extract name from quotes if present
                    # "CAFFE BAR \"MX\"" → "MX"
                    quote_match = re.search(r'["\']([^"\']+)["\']', wifi_content)
                    if quote_match:
                        return quote_match.group(1).strip()

                    # Remove "caffe bar" prefix if present
                    wifi_content = re.sub(r'^(caffe\s+bar|bar|caffe)\s+', '', wifi_content, flags=re.IGNORECASE)

                    # Return cleaned name
                    if len(wifi_content) >= 2:
                        return wifi_content.strip()

        return None

    def extract_store_name_flexible(self, lines: List[str]) -> str:
        """
        Extract store name - IMPROVED approach.

        Store name can be in:
        1. Header (first 1-7 lines) - most common
        2. WiFi line (footer) - fallback for franchises

        Examples:
        - "Caffe bar RETRO" in header
        - Only company name "METRO COMMERCE d.o.o." in header → check WiFi
        - WiFi: "CAFFE BAR \"MX\"" → extract "MX"
        """

        store_from_header = None

        for i, line in enumerate(lines[:7]):  # Check first 7 lines
            line_clean = line.strip()

            # Skip empty or very short lines
            if len(line_clean) < 2:
                continue

            cleaned = self.text_cleaner.clean_ocr_line(line_clean)

            # Skip if it's clearly an address (has postal code)
            if self.detect_croatian_address(line_clean):
                continue

            # Skip table headers
            if re.search(r'(naziv|cijena|kol|iznos)', cleaned.lower()):
                continue

            # Skip item lines (have prices like "2,40" or patterns like "1,00 2,40")
            if re.search(r'\d+[.,]\d{2}.*\d+[.,]\d{2}', line_clean):
                continue

            # Skip total/sum lines
            if re.search(r'(ukupno|total|suma|svega)', cleaned.lower()):
                continue

            # Skip obvious noise/junk
            if re.match(r'^\W*$', cleaned):  # Only symbols
                continue

            # Clean up quotes and symbols
            cleaned = cleaned.strip('"').strip("'").strip()

            # Fix OCR error: "11" is often misread quotation marks around names
            # Pattern: "11 MX 11" should be "MX"
            cleaned = re.sub(r'^11\s+', '', cleaned)  # Remove leading "11 "
            cleaned = re.sub(r'\s+11$', '', cleaned)  # Remove trailing " 11"

            # Check for standalone business type descriptors (caffe bar, restoran, etc.)
            # BUT: if next line has the actual name, combine them
            # Example: "čaffe bar" + "MX" → "čaffe bar MX"
            business_types = ['caffe bar', 'čaffe bar', 'bar', 'caffe', 'čaffe',
                             'restoran', 'pekara', 'trgovina', 'kafić',
                             'bistro', 'pizzeria']

            if cleaned.lower() in business_types:
                # Check if next line has a name (not address, not numbers)
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    next_cleaned = self.text_cleaner.clean_ocr_line(next_line)

                    # Remove numbers and spaces to check if there's a name
                    next_name_only = re.sub(r'[\d\s]+', '', next_cleaned).strip()

                    # If next line has letters (potential name), combine them
                    if (len(next_name_only) >= 2 and
                        not self.detect_croatian_address(next_line) and
                        not re.search(r'[dđ]\.?\s*[o0]\.?\s*[o0]\.?', next_cleaned.lower())):
                        combined = f"{cleaned} {next_name_only}"
                        return combined
                # No valid next line, skip this business type line
                continue

            # Check for company legal names (d.o.o., j.d.o.o., đ.O.O., đ.0.0.)
            # These are company entities, not store brands - skip them entirely
            # Handle both d and đ (Croatian character), and OCR errors (0 instead of O)
            if re.search(r'[dđ]\.?\s*[o0]\.?\s*[o0]\.?|j\.?\s*[dđ]\.?\s*[o0]\.?\s*[o0]\.?', cleaned.lower()):
                # Found company legal name - mark that we need to check WiFi
                store_from_header = "COMPANY_NAME_FOUND"  # Marker to trigger WiFi check
                continue

            # Check if it looks like a store name
            # Must have at least 2 letters and be between 2-50 chars
            if (2 <= len(cleaned) <= 50 and
                re.search(r'[a-zA-ZčćžšđĆČŽŠĐ]{2,}', cleaned)):

                # Skip lines with excessive numbers (OCR noise like "11 MX 11")
                # Count letters vs numbers
                letter_count = len(re.findall(r'[a-zA-ZčćžšđĆČŽŠĐ]', cleaned))
                digit_count = len(re.findall(r'\d', cleaned))

                # If more than 30% digits, likely noise
                if digit_count > 0 and digit_count / len(cleaned) > 0.3:
                    continue

                # Found potential store name in header
                store_from_header = cleaned
                # Don't return yet - might be company name, check if better option exists
                # But if it's clearly a brand name (short, no d.o.o.), use it
                if 'd.o.o' not in cleaned.lower() and 'j.d.o.o' not in cleaned.lower():
                    return cleaned

        # If we found a company name (d.o.o.) in header but no clear store name,
        # try to extract from WiFi line
        if store_from_header:
            wifi_name = self.extract_store_name_from_wifi(lines)
            if wifi_name:
                return wifi_name
            # No WiFi name found
            # If we only found a company legal name, return None instead of using it
            if store_from_header == "COMPANY_NAME_FOUND":
                return None
            # Otherwise return what we found
            return store_from_header

        # Last resort: check WiFi line
        wifi_name = self.extract_store_name_from_wifi(lines)
        if wifi_name:
            return wifi_name

        return "Unknown Store"