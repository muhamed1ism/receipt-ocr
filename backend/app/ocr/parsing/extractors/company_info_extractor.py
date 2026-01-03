"""
Company Info Extractor
======================
Extracts business/company information from Croatian receipts.

Extracts:
- Address (street, city, postal code)
- Business registration (OIB, business type)
- Owner information

Example from receipt header:
    čaffe bar
    RETRO
    Ruđera Bokoviča 23, 21000 Split      ← Address
    šAT Obrt ža ugostiteljstvo...        ← Business registration
    vl. Herbert Hrgovic                  ← Owner
"""

import re
import logging
from typing import List, Optional, Dict

logger = logging.getLogger(__name__)


class CompanyInfoExtractor:
    """Extracts company/business information from receipt header"""

    def __init__(self):
        # Business ID patterns for Croatian and Bosnian receipts
        self.business_id_patterns = {
            # Croatian
            'oib': r'oib\s*:?\s*([\d\s.]+)',  # OIB: 11 digits

            # Bosnian (patterns with separators: dots, dashes, spaces)
            # JIB variations: JIB, SB (Sistem Broj), MB (Matični Broj)
            'jib': r'(?:jib|sb|mb)\s*:?\s*([\d\s.\-]+)',  # JIB: 10-13 digits
            # PIB variations: PIB, PB (Poreski Broj)
            'pib': r'(?:pib|pb)\s*:?\s*([\d\s.\-]+)',  # PIB: 9-12 digits
            'ibfm': r'ibfm\s*:?\s*([A-Z0-9\s\-]+)',  # IBFM: fiscal device ID
        }

    def extract_business_ids(self, lines: List[str], debug: bool = False) -> Dict[str, Optional[str]]:
        """
        Extract business identifiers from receipt lines.

        Supports:
        - Croatian: OIB (11 digits)
        - Bosnian: JIB (13 digits), PIB (9-12 digits), IBFM (fiscal device ID)

        Args:
            lines: Lines to search (typically header section)
            debug: Enable debug logging

        Returns:
            {
                "oib": "12345678901" or None,      # Croatian
                "jib": "1234567890123" or None,    # Bosnian
                "pib": "123456789012" or None,     # Bosnian
                "ibfm": "XYZ-123" or None          # Bosnian
            }
        """
        result = {
            'oib': None,
            'jib': None,
            'pib': None,
            'ibfm': None
        }

        # First, try to find labeled IDs (with keywords like "JIB:", "PIB:", etc.)
        for line in lines:
            line_lower = line.lower()

            # Try each pattern
            for id_type, pattern in self.business_id_patterns.items():
                if result[id_type]:  # Already found
                    continue

                match = re.search(pattern, line_lower, re.IGNORECASE)
                if match:
                    raw_value = match.group(1)

                    # Clean the extracted value
                    if id_type in ['oib', 'jib', 'pib']:
                        # Remove spaces and non-digits for numeric IDs
                        cleaned = re.sub(r'[^0-9]', '', raw_value)

                        # Validate length
                        if id_type == 'oib' and len(cleaned) == 11:
                            result['oib'] = cleaned
                            if debug:
                                logger.debug(f"[COMPANY INFO] Found labeled OIB: {cleaned}")
                        elif id_type == 'jib' and 10 <= len(cleaned) <= 13:
                            result['jib'] = cleaned
                            if debug:
                                logger.debug(f"[COMPANY INFO] Found labeled JIB: {cleaned}")
                        elif id_type == 'pib' and 9 <= len(cleaned) <= 12:
                            result['pib'] = cleaned
                            if debug:
                                logger.debug(f"[COMPANY INFO] Found labeled PIB: {cleaned}")

                    elif id_type == 'ibfm':
                        # IBFM can be alphanumeric with dashes
                        cleaned = raw_value.strip().upper()
                        result['ibfm'] = cleaned
                        if debug:
                            logger.debug(f"[COMPANY INFO] Found labeled IBFM: {cleaned}")

        # If no labeled IDs found, try pattern-based extraction (for receipts without labels)
        if not any(result.values()):
            if debug:
                logger.debug("[COMPANY INFO] No labeled IDs found, trying pattern-based extraction...")

            for i, line in enumerate(lines[:10]):  # Only check first 10 lines (header)
                line_clean = line.strip()

                # Skip empty lines, store names, addresses
                if not line_clean or len(line_clean) < 5:
                    continue

                # Skip lines that look like dates/times (avoid false positives)
                # Patterns: "31.12.2025", "19:33", "01.12.2025.19:36"
                if re.search(r'\b\d{1,2}[.:/]\d{1,2}[.:/]\d{2,4}', line_clean):
                    if debug:
                        logger.debug(f"[COMPANY INFO] Skipping date/time line {i+1}: '{line_clean}'")
                    continue

                # First, try to find numbers with dots/dashes that might be IDs
                # Pattern like: 61.12.2825.1933 or 123-456-789-012
                # Remove dots, dashes, spaces and check if it forms a valid ID
                cleaned_line = re.sub(r'[.\-\s]', '', line_clean)
                digit_sequences_full = re.findall(r'\d+', cleaned_line)

                for seq in digit_sequences_full:
                    # Priority order to avoid conflicts:
                    # 1. OIB: exactly 11 digits (Croatian, distinct length)
                    # 2. JIB: exactly 13 digits OR exactly 10 digits (Bosnian - 13 is standard, 10 is legacy)
                    # 3. PIB: 12 digits OR 9 digits (Bosnian - avoid 10, 11, 13 which are taken)

                    # OIB: exactly 11 digits (Croatian only)
                    if not result['oib'] and len(seq) == 11:
                        result['oib'] = seq
                        if debug:
                            logger.debug(f"[COMPANY INFO] Found unlabeled OIB (11 digits): {seq} on line {i+1}: '{line_clean}'")

                    # JIB: 13 digits (standard) or 10 digits (legacy format)
                    elif not result['jib'] and len(seq) in [10, 13]:
                        result['jib'] = seq
                        if debug:
                            logger.debug(f"[COMPANY INFO] Found unlabeled JIB ({len(seq)} digits): {seq} on line {i+1}: '{line_clean}'")

                    # PIB: 12 digits or 9 digits (avoid 10, 11, 13 which are taken by JIB/OIB)
                    elif not result['pib'] and len(seq) in [9, 12]:
                        result['pib'] = seq
                        if debug:
                            logger.debug(f"[COMPANY INFO] Found unlabeled PIB ({len(seq)} digits): {seq} on line {i+1}: '{line_clean}'")

                # Look for IBFM-like codes (8-12 alphanumeric chars, possibly with dashes)
                # IBFM format: BP + 6 digits (e.g., BP002450)
                # May appear as "BFMBP002450" after OCR merging "BF.M BP 002450"
                if not result['ibfm']:
                    # First, try to extract BP + 6 digits (the actual IBFM code)
                    ibfm_match = re.search(r'\b(BP\d{6})\b', line_clean.upper())

                    if not ibfm_match:
                        # Fallback: Look for longer codes and extract BP portion if present
                        long_match = re.search(r'\b[A-Z]*?(BP\d{6})\b', line_clean.upper())
                        if long_match:
                            ibfm_match = long_match

                    if not ibfm_match:
                        # Final fallback: BF + 6-8 digits (older format)
                        ibfm_match = re.search(r'\b(BF\d{6,8})\b', line_clean.upper())

                    if ibfm_match:
                        result['ibfm'] = ibfm_match.group(1)
                        if debug:
                            logger.debug(f"[COMPANY INFO] Found IBFM pattern: {result['ibfm']} on line {i+1}")

        if debug and not any(result.values()):
            logger.debug("[COMPANY INFO] No business IDs found (labeled or unlabeled)")

        return result

    def extract_business_ids_explicit(self, lines: List[str], debug: bool = False) -> Dict[str, Optional[str]]:
        """
        EXPLICIT business ID extraction with location-based rules.

        This method searches for business IDs in specific locations (header lines 0-10)
        using both labeled and unlabeled patterns.

        Bosnian ID variations:
        - JIB (Jedinstveni Identifikacioni Broj): also appears as "SB" (Sistem Broj) or "MB" (Matični Broj)
        - PIB (Poreski Identifikacioni Broj): also appears as "PB" (Poreski Broj)
        - IBFM: fiscal device identifier (e.g., BF290832)

        Croatian ID variations:
        - OIB (Osobni Identifikacijski Broj): 11 digits

        Args:
            lines: All receipt lines
            debug: Enable debug logging

        Returns:
            {
                "oib": "12345678901" or None,
                "jib": "4280918683054" or None,
                "pib": "123456789" or None,
                "ibfm": "BF290832" or None
            }
        """
        result = {
            'oib': None,
            'jib': None,
            'pib': None,
            'ibfm': None
        }

        # Search ONLY in header (lines 0-10)
        header_lines = lines[:min(10, len(lines))]

        if debug:
            logger.debug(f"[EXPLICIT BUSINESS IDs] Searching in header lines (0-{len(header_lines)-1})")

        for i, line in enumerate(header_lines):
            line_upper = line.upper()

            # Skip date/time lines to avoid false positives
            if re.search(r'\b\d{1,2}[.:/]\d{1,2}[.:/]\d{2,4}', line):
                if debug:
                    logger.debug(f"[EXPLICIT BUSINESS IDs] Skipping date/time line {i}: '{line}'")
                continue

            # JIB pattern (Bosnian): 10-13 digits, with labels "JIB:", "SB:", "MB:"
            if not result['jib']:
                match = re.search(r'(?:JIB|SB|MB)\s*:?\s*(\d[\d\s.\-]{8,13})', line_upper)
                if match:
                    raw = match.group(1)
                    cleaned = re.sub(r'[^0-9]', '', raw)
                    if 10 <= len(cleaned) <= 13:
                        result['jib'] = cleaned
                        if debug:
                            logger.debug(f"[EXPLICIT BUSINESS IDs] Found JIB on line {i}: {cleaned} (from '{line}')")

            # PIB pattern (Bosnian): 9-12 digits, with labels "PIB:", "PB:"
            if not result['pib']:
                match = re.search(r'(?:PIB|PB)\s*:?\s*(\d[\d\s.\-]{7,12})', line_upper)
                if match:
                    raw = match.group(1)
                    cleaned = re.sub(r'[^0-9]', '', raw)
                    if 9 <= len(cleaned) <= 12:
                        result['pib'] = cleaned
                        if debug:
                            logger.debug(f"[EXPLICIT BUSINESS IDs] Found PIB on line {i}: {cleaned} (from '{line}')")

            # OIB pattern (Croatian): exactly 11 digits, with label "OIB:"
            if not result['oib']:
                match = re.search(r'OIB\s*:?\s*(\d[\d\s.\-]{9,11})', line_upper)
                if match:
                    raw = match.group(1)
                    cleaned = re.sub(r'[^0-9]', '', raw)
                    if len(cleaned) == 11:
                        result['oib'] = cleaned
                        if debug:
                            logger.debug(f"[EXPLICIT BUSINESS IDs] Found OIB on line {i}: {cleaned} (from '{line}')")

            # IBFM pattern (Bosnian fiscal device): BP + 6 digits (e.g., BP002450)
            # May appear as "BFMBP002450" after OCR merging "BF.M BP 002450"
            if not result['ibfm']:
                # First, try to extract BP + 6 digits (the actual IBFM code)
                match = re.search(r'\b(BP\s?\d{6})\b', line_upper)

                if not match:
                    # Fallback: Look for longer codes and extract BP portion if present
                    match = re.search(r'\b[A-Z]*?(BP\s?\d{6})\b', line_upper)

                if not match:
                    # Final fallback: BF + 6-8 digits (older format)
                    match = re.search(r'\b(BF\s?\d{6,8})\b', line_upper)

                if match:
                    # Remove space if present
                    ibfm_value = match.group(1).replace(' ', '')
                    result['ibfm'] = ibfm_value
                    if debug:
                        logger.debug(f"[EXPLICIT BUSINESS IDs] Found IBFM on line {i}: {result['ibfm']} (from '{line}')")

        if debug:
            found = [k for k, v in result.items() if v is not None]
            if found:
                logger.debug(f"[EXPLICIT BUSINESS IDs] Extraction complete - found: {', '.join(found)}")
            else:
                logger.debug("[EXPLICIT BUSINESS IDs] No business IDs found in header")

        return result

    def extract_company_info(self, header_lines: List[str], debug: bool = False) -> Dict[str, Optional[str]]:
        """
        Extract company information from header section - SIMPLIFIED.

        NEW APPROACH: Just collect everything, don't try to parse/categorize.
        Receipt formats vary too much - shuffled fields, different layouts.

        Args:
            header_lines: Lines from HEADER section (typically first 5-7 lines)
            debug: Enable debug logging

        Returns:
            {
                "raw_lines": ["line1", "line2", ...],  # All company info lines
                "text": "line1\nline2\n..."            # Combined text block
            }
        """
        if debug:
            logger.debug("[COMPANY INFO] Collecting company info lines (no parsing)")

        company_lines = []

        for line in header_lines:
            line_clean = line.strip()

            # Skip empty lines
            if not line_clean or len(line_clean) < 2:
                continue

            # Skip if it looks like table header (marks end of header section)
            if re.search(r'(naziv|cijena|kol\.?|iznos)', line_clean.lower()):
                break

            # Skip if it looks like items section
            if re.search(r'\d+[.,]\d{2}.*\d+[.,]\d{2}', line_clean):
                break

            # Collect this line as company info
            company_lines.append(line_clean)

            if debug:
                logger.debug(f"[COMPANY INFO] Collected: {line_clean}")

        # Extract business IDs from header lines
        # NOTE: We pass header_lines to extract_business_ids which checks first 10 lines
        # This ensures we catch IDs even if they appear slightly outside the detected header
        business_ids = self.extract_business_ids(header_lines, debug=debug)

        # Return simple structure with business IDs
        result = {
            "raw_lines": company_lines,
            "text": "\n".join(company_lines) if company_lines else None,
            # Business identifiers
            "oib": business_ids.get("oib"),
            "jib": business_ids.get("jib"),
            "pib": business_ids.get("pib"),
            "ibfm": business_ids.get("ibfm")
        }

        if debug:
            logger.debug(f"[COMPANY INFO] Collected {len(company_lines)} lines total")
            logger.debug(f"[COMPANY INFO] Business IDs: OIB={business_ids.get('oib')}, JIB={business_ids.get('jib')}, PIB={business_ids.get('pib')}, IBFM={business_ids.get('ibfm')}")

        return result

    def _is_address(self, line: str) -> bool:
        """
        Check if line is an address.

        Croatian address patterns:
        - Contains postal code (5 digits)
        - Contains city name
        - Contains street number
        - Format: "Street XX, XXXXX City"
        """
        # Must have postal code (5 digits)
        if not re.search(r'\b\d{5}\b', line):
            return False

        # Must have city name (word after postal code)
        # Pattern: "XXXXX City" or "XXXXX City Name"
        if not re.search(r'\d{5}\s+[A-ZČĆĐŠŽ][a-zčćđšž]+', line):
            return False

        # Likely contains street number (number before comma)
        # Pattern: "Street XX,"
        if re.search(r'\d+\s*,', line):
            return True

        return True  # Has postal code and city, likely address

    def _is_business_registration(self, line: str) -> bool:
        """
        Check if line contains business registration info.

        Patterns:
        - OIB: followed by number
        - šAT / OAT (tax number)
        - Obrt (craft business)
        - d.o.o. / j.d.o.o. (company types)
        - PDV (VAT registration)
        """
        line_lower = line.lower()

        business_patterns = [
            r'oib\s*:?\s*\d+',           # OIB: 12345678901
            r'[šs]at',                   # šAT
            r'oat',                      # OAT (OCR variation)
            r'obrt',                     # Obrt (craft business)
            r'd\.?\s*o\.?\s*o',          # d.o.o. (LLC)
            r'j\.?\s*d\.?\s*o\.?\s*o',   # j.d.o.o. (simple LLC)
            r'pdv',                      # PDV registration
            r'ugostiteljstvo',           # Hospitality business
            r'trgovina',                 # Trade business
        ]

        for pattern in business_patterns:
            if re.search(pattern, line_lower):
                return True

        return False

    def _is_owner_info(self, line: str) -> bool:
        """
        Check if line contains owner/director information.

        Patterns:
        - vl. (vlasnik = owner)
        - direktor
        - izvršni direktor (CEO)
        - Contains person name pattern
        """
        line_lower = line.lower()

        owner_patterns = [
            r'\bvl\.\s*',                # vl. Herbert Hrgovic
            r'\bvlasnik',                # vlasnik
            r'direktor',                 # direktor
            r'izvr[sš]ni\s+direktor',    # izvršni direktor
        ]

        for pattern in owner_patterns:
            if re.search(pattern, line_lower):
                return True

        # Check if line looks like a person name (after "vl." prefix)
        # Pattern: "vl. FirstName LastName" or just "FirstName LastName"
        if re.match(r'vl\.\s+[A-ZČĆĐŠŽ][a-zčćđšž]+\s+[A-ZČĆĐŠŽ][a-zčćđšž]+', line):
            return True

        return False

    def _clean_owner_name(self, owner_line: str) -> str:
        """
        Clean owner name by removing prefixes like 'vl.'

        Examples:
            "vl. Herbert Hrgovic" → "Herbert Hrgovic"
            "vlasnik: John Doe" → "John Doe"
        """
        # Remove common prefixes
        cleaned = re.sub(r'^(vl\.|vlasnik:?)\s*', '', owner_line, flags=re.IGNORECASE)
        return cleaned.strip()
