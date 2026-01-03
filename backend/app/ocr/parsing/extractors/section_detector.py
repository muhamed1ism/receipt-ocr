"""
Receipt Section Detector
========================
Identifies distinct sections in Croatian receipts to prevent cross-section contamination.

Sections:
- HEADER: Store name, address, OIB (lines 0 to items_header)
- ITEMS_HEADER: Column headers like "Naziv Cijena Kol. Iznos"
- ITEMS: Product listings (items_header+1 to total_line)
- TOTALS: Total amount and payment info (total_line to footer)
- FOOTER: Receipt number, date, taxes, QR codes
"""

import re
import logging
from typing import List, Dict, Optional, Tuple
from ..text_preprocessing.text_cleaner import TextCleaner

logger = logging.getLogger(__name__)


class ReceiptSectionDetector:
    """Detects and marks receipt sections for accurate parsing"""

    def __init__(self):
        self.text_cleaner = TextCleaner()

    def detect_sections(self, lines: List[str], debug: bool = False) -> Dict[str, Tuple[int, int]]:
        """
        Detect all receipt sections and return their boundaries.

        Returns:
            {
                'header': (start_idx, end_idx),
                'items_header': (idx, idx),  # Single line
                'items': (start_idx, end_idx),
                'totals': (start_idx, end_idx),
                'footer': (start_idx, end_idx)
            }
        """
        if not lines:
            return {}

        # Find key markers
        items_header_idx = self._find_items_header(lines)
        total_idx = self._find_total_line(lines)
        receipt_number_idx = self._find_receipt_number(lines)

        if debug:
            logger.debug(f"[SECTION DETECTOR] Items header at line: {items_header_idx}")
            logger.debug(f"[SECTION DETECTOR] Total at line: {total_idx}")
            logger.debug(f"[SECTION DETECTOR] Receipt number at line: {receipt_number_idx}")

        # Build sections
        sections = {}

        # HEADER SECTION (everything before items header or items start)
        if items_header_idx >= 0:
            sections['header'] = (0, items_header_idx)
            sections['items_header'] = (items_header_idx, items_header_idx + 1)
            items_start = items_header_idx + 1
        else:
            # No items header found, estimate header size (first 3-5 lines)
            header_end = min(3, len(lines) // 4)
            sections['header'] = (0, header_end)
            items_start = header_end

        # ITEMS SECTION (from items_header+1 to total line)
        if total_idx >= 0:
            sections['items'] = (items_start, total_idx)
            totals_start = total_idx
        else:
            # No total found, assume items go until 80% of receipt
            items_end = int(len(lines) * 0.8)
            sections['items'] = (items_start, items_end)
            totals_start = items_end

        # TOTALS SECTION (from total line to receipt number or end)
        if receipt_number_idx >= 0 and receipt_number_idx > totals_start:
            sections['totals'] = (totals_start, receipt_number_idx)
            sections['footer'] = (receipt_number_idx, len(lines))
        else:
            # No clear footer, totals go to end
            sections['totals'] = (totals_start, len(lines))
            sections['footer'] = (len(lines), len(lines))  # Empty

        if debug:
            logger.debug("[SECTION DETECTOR] Detected sections:")
            for section_name, (start, end) in sections.items():
                logger.debug(f"  {section_name}: lines {start}-{end}")

        return sections

    def _find_items_header(self, lines: List[str]) -> int:
        """
        Find the items header line (e.g., "Naziv Cijena Kol. Iznos" or "Kol. Iznos Cijena Naziv")
        This is the most reliable marker for where items start.
        Handles both standard and reversed column order formats.
        """
        items_header_patterns = [
            # Standard format: Naziv Cijena Kol. Iznos
            r'na[žz]iv.*[čc]ijena.*kol.*izn[o0]s',  # Full header (with OCR variants)
            r'na[žz]iv.*[čc]ijena',  # Partial header
            # Reversed format: Kol. Iznos Cijena Naziv
            r'kol.*izn[o0]s.*[čc]ijena.*na[žz]iv',  # Reversed full header
            r'kol.*[čc]ijena.*na[žz]iv',  # Reversed partial
            # English variants
            r'name.*price.*qty',  # English variant
            r'qty.*price.*name',  # Reversed English
            # Alternative formats
            r'artikl.*[čc]ijena',  # Alternative
        ]

        for i, line in enumerate(lines[:15]):  # Check first 15 lines only
            line_clean = self.text_cleaner.clean_ocr_line(line).lower()

            for pattern in items_header_patterns:
                if re.search(pattern, line_clean):
                    return i

        return -1

    def _find_total_line(self, lines: List[str]) -> int:
        """Find the line with total amount (ukupno, total, suma)"""
        total_patterns = [
            r'ukupn[o0].*\d+[.,]\d{2}',  # ukupno (EUR): 8,60
            r't[o0]tal.*\d+[.,]\d{2}',   # total: 8.60
            r'suma.*\d+[.,]\d{2}',       # suma: 8,60
            r'sveukupn[o0].*\d+[.,]\d{2}',  # sveukupno
        ]

        for i, line in enumerate(lines):
            line_clean = self.text_cleaner.clean_ocr_line(line).lower()

            for pattern in total_patterns:
                if re.search(pattern, line_clean):
                    return i

        return -1

    def _find_receipt_number(self, lines: List[str]) -> int:
        """Find receipt number line (marks start of footer)"""
        receipt_patterns = [
            r'ra[cč]un\s*br[o0]j',  # račun broj
            r'receipt\s*number',     # English
            r'receipt\s*#',
        ]

        for i, line in enumerate(lines):
            line_clean = self.text_cleaner.clean_ocr_line(line).lower()

            for pattern in receipt_patterns:
                if re.search(pattern, line_clean):
                    return i

        return -1

    def get_section_lines(self, lines: List[str], section: str, sections: Dict[str, Tuple[int, int]]) -> List[str]:
        """Extract lines for a specific section"""
        if section not in sections:
            return []

        start, end = sections[section]
        return lines[start:end]
