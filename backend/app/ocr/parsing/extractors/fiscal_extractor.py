"""
Fiscal Code Extractor
=====================
Extracts Croatian fiscal receipt codes (ZKI and JIR).

ZKI (Zaštitni Kod Izdavatelja) - Security Code:
    - Format: 32 hexadecimal characters
    - Example: a5bcd002f1eeab23d202d07521c71d5
    - OCR may read as: "ža.Kod:a 55 cdc 002 fleeab 23d 202d 0752 lc7 ld5"

JIR (Jedinstveni Identifikator Računa) - Unique Receipt ID:
    - Format: UUID (8-4-4-4-12 characters)
    - Example: f15f86aa-2d62-462a-9461-ed4580d9c587
    - OCR may read as: "JIR:f 15f 86 aa-2d 82-462a-9461-ec 458 od9c 587"
"""

import re
import logging
from typing import List, Optional, Dict

logger = logging.getLogger(__name__)


class FiscalExtractor:
    """Extracts ZKI and JIR fiscal codes from Croatian receipts"""

    def __init__(self):
        # ZKI patterns - look for long strings after keywords
        # We'll extract only hex (a-f, 0-9) from the captured string
        # Pattern needs to be permissive to catch OCR errors (Croatian chars, extra letters)
        self.zki_patterns = [
            r'kod:?\s*([\w\s]{20,})',  # Kod: followed by word chars/spaces (we filter to hex later)
            r'zki:?\s*([\w\s]{20,})',  # ZKI:
        ]

        # JIR patterns - UUID format (capture everything after JIR:, filter to hex later)
        # Pattern needs to catch dashes and OCR errors
        self.jir_patterns = [
            r'jir:?\s*([\w\s\-]{25,})',  # JIR: followed by anything that looks like UUID-ish
            r'jedinstven.*?:?\s*([\w\s\-]{25,})',  # Jedinstveni identifikator:
        ]

    def extract_zki(self, lines: List[str], debug: bool = False) -> Optional[str]:
        """
        Extract ZKI (Zaštitni Kod Izdavatelja) - 32 hex character code.

        Args:
            lines: All receipt lines (typically search footer section)
            debug: Enable debug logging

        Returns:
            Clean ZKI code (32 hex chars) or None
            Example: "a5bcd002f1eeab23d202d07521c71d5"
        """
        if debug:
            logger.debug("[ZKI] Searching for Zaštitni Kod...")

        for line in lines:
            line_lower = line.lower()

            # Try each pattern
            for pattern in self.zki_patterns:
                match = re.search(pattern, line_lower, re.IGNORECASE)
                if match:
                    raw_code = match.group(1)

                    # ZKI is pure hex (0-9, a-f), remove spaces and any other chars
                    hex_only = re.sub(r'[^a-f0-9]', '', raw_code.lower())

                    if debug:
                        logger.debug(f"[ZKI] Found in line: '{line}'")
                        logger.debug(f"[ZKI] Raw: '{raw_code}'")
                        logger.debug(f"[ZKI] Hex only: '{hex_only}' ({len(hex_only)} chars)")

                    # ZKI should be exactly 32 hex chars (allow 28-36 for OCR errors)
                    if len(hex_only) >= 28:
                        # Truncate to 32 or pad if slightly short
                        clean_code = hex_only[:32]
                        if len(clean_code) < 32:
                            clean_code = clean_code.ljust(32, '0')

                        if debug:
                            logger.debug(f"[ZKI] Clean (32 chars): '{clean_code}'")

                        return clean_code

        if debug:
            logger.debug("[ZKI] Not found")
        return None

    def extract_jir(self, lines: List[str], debug: bool = False) -> Optional[str]:
        """
        Extract JIR (Jedinstveni Identifikator Računa) - UUID format.

        Args:
            lines: All receipt lines (typically search footer section)
            debug: Enable debug logging

        Returns:
            Clean JIR in UUID format or None
            Example: "f15f86aa-2d62-462a-9461-ed4580d9c587"
        """
        if debug:
            logger.debug("[JIR] Searching for Jedinstveni Identifikator...")

        for line in lines:
            line_lower = line.lower()

            # Try each pattern
            for pattern in self.jir_patterns:
                match = re.search(pattern, line_lower, re.IGNORECASE)
                if match:
                    raw_code = match.group(1)

                    # JIR is pure hex (0-9, a-f) formatted as UUID with dashes
                    # Remove spaces but keep dashes (they mark UUID segment boundaries)
                    hex_with_dashes = re.sub(r'[^a-f0-9\-]', '', raw_code.lower())

                    # Extract hex only (remove dashes for counting)
                    hex_only = hex_with_dashes.replace('-', '')

                    if debug:
                        logger.debug(f"[JIR] Found in line: '{line}'")
                        logger.debug(f"[JIR] Raw: '{raw_code}'")
                        logger.debug(f"[JIR] With dashes: '{hex_with_dashes}'")
                        logger.debug(f"[JIR] Hex only: '{hex_only}' ({len(hex_only)} chars)")

                    # UUID should be 32 hex chars (allow 28-36 for OCR errors)
                    if len(hex_only) >= 28:
                        # Truncate to 32 if longer, pad if shorter
                        if len(hex_only) > 32:
                            hex_only = hex_only[:32]
                        elif len(hex_only) < 32:
                            hex_only = hex_only.ljust(32, '0')

                        # Format as UUID (8-4-4-4-12)
                        uuid_formatted = f"{hex_only[0:8]}-{hex_only[8:12]}-{hex_only[12:16]}-{hex_only[16:20]}-{hex_only[20:32]}"

                        if debug:
                            logger.debug(f"[JIR] Clean UUID: '{uuid_formatted}'")

                        return uuid_formatted

        if debug:
            logger.debug("[JIR] Not found")
        return None

    def extract_digital_signature(self, lines: List[str], debug: bool = False) -> Optional[str]:
        """
        Extract Bosnian digital signature from footer.

        Digital signature is a long alphanumeric code (50-200+ characters) that appears
        in the footer after totals, before QR code. May span multiple lines.

        Args:
            lines: All receipt lines (typically search footer section)
            debug: Enable debug logging

        Returns:
            Digital signature string or None
            Example: "3EF48D0C74F29CB9E3B1A5D7..."
        """
        if debug:
            logger.debug("[DIGITAL SIG] Searching for Bosnian digital signature...")

        # Look for long alphanumeric strings after total/ukupno
        # Digital signature appears after payment section, before QR code
        signature_candidates = []
        found_total = False
        found_qr_or_config = False

        for i, line in enumerate(lines):
            line_clean = line.strip()
            line_upper = line_clean.upper()

            # Mark when we've passed the total section
            if re.search(r'\b(UKUPNO|TOTAL|SUMA)\b', line_upper):
                found_total = True
                continue

            # Stop before QR code or CONFIG FISCAL marker
            if re.search(r'\b(QR|CONFIG\s*FISCAL|HVALA)\b', line_upper):
                found_qr_or_config = True
                break

            # Only look for signature after total, before QR
            if found_total and not found_qr_or_config:
                # Look for long alphanumeric strings (50+ chars after cleaning)
                # Remove spaces and common separators
                alphanumeric_only = re.sub(r'[^A-Z0-9]', '', line_upper)

                if len(alphanumeric_only) >= 50:
                    signature_candidates.append({
                        'line_index': i,
                        'value': alphanumeric_only,
                        'length': len(alphanumeric_only)
                    })
                    if debug:
                        logger.debug(f"[DIGITAL SIG] Candidate at line {i}: '{alphanumeric_only[:60]}...' ({len(alphanumeric_only)} chars)")

        # If we found candidates, take the longest one (likely the signature)
        if signature_candidates:
            # Sort by length descending
            signature_candidates.sort(key=lambda x: x['length'], reverse=True)
            best_candidate = signature_candidates[0]

            # Check if there are consecutive lines that might be part of the signature
            signature = best_candidate['value']
            start_index = best_candidate['line_index']

            # Try to concatenate consecutive alphanumeric lines
            for j in range(start_index + 1, min(start_index + 5, len(lines))):
                next_line = lines[j].strip().upper()
                next_alphanumeric = re.sub(r'[^A-Z0-9]', '', next_line)

                # If next line is also long alphanumeric, it might be continuation
                if len(next_alphanumeric) >= 30 and not re.search(r'\b(QR|CONFIG|HVALA)\b', next_line):
                    signature += next_alphanumeric
                    if debug:
                        logger.debug(f"[DIGITAL SIG] Concatenating line {j}: '{next_alphanumeric[:40]}...'")
                else:
                    break

            if debug:
                logger.debug(f"[DIGITAL SIG] Found signature: '{signature[:80]}...' ({len(signature)} total chars)")

            return signature

        if debug:
            logger.debug("[DIGITAL SIG] Not found")
        return None

    def extract_fiscal_codes(self, lines: List[str], debug: bool = False) -> Dict[str, Optional[str]]:
        """
        Extract fiscal codes: ZKI, JIR (Croatian), and digital signature (Bosnian).

        Args:
            lines: All receipt lines
            debug: Enable debug logging

        Returns:
            {
                "zki": "a5bcd002f1eeab23d202d07521c71d5",    # Croatian
                "jir": "f15f86aa-2d62-462a-9461-ed4580d9c587", # Croatian
                "digital_signature": "3EF48D0C74F29CB9..."     # Bosnian
            }
        """
        return {
            "zki": self.extract_zki(lines, debug=debug),
            "jir": self.extract_jir(lines, debug=debug),
            "digital_signature": self.extract_digital_signature(lines, debug=debug)
        }
