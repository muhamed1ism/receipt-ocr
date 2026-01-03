"""
Tax Breakdown Extractor
=======================
Extracts and validates tax information from Croatian receipts.

Focuses on:
- PDV (tax rate) - Government-approved rates only (0%, 3%, 5%, 13%, 25%)
- Iznos (tax amount) - Required
- Osnovica (taxable base) - Optional

Validates tax rates against Croatian legal standards.
"""

import re
import logging
from typing import List, Dict, Optional, Tuple

logger = logging.getLogger(__name__)

# Croatian government-approved tax rates
CROATIAN_TAX_RATES = [0.0, 3.0, 5.0, 13.0, 25.0]
STANDARD_TAX_RATE = 25.0  # Most common rate


class TaxExtractor:
    """Extracts tax breakdown from Croatian receipts"""

    def __init__(self):
        self.croatian_rates = CROATIAN_TAX_RATES

    def extract_tax_breakdown(self, lines: List[str], debug: bool = False) -> Tuple[List[Dict], float]:
        """
        Extract tax breakdown from receipt lines.

        Returns:
            Tuple of (tax_breakdown_list, total_tax)
            - tax_breakdown_list: List of tax entries
            - total_tax: Sum of all tax amounts
        """
        if debug:
            logger.debug("[TAX EXTRACTOR] Starting tax extraction")

        # Find tax section
        tax_section_start = self._find_tax_section(lines, debug=debug)
        if tax_section_start == -1:
            if debug:
                logger.debug("[TAX EXTRACTOR] No tax section found")
            return [], 0.0

        # Extract tax entries from table
        tax_entries = self._parse_tax_table(lines, tax_section_start, debug=debug)

        # Calculate total tax
        total_tax = sum(entry['tax_amount'] for entry in tax_entries)

        if debug:
            logger.debug(f"[TAX EXTRACTOR] Found {len(tax_entries)} tax entries, total: {total_tax:.2f}")

        return tax_entries, total_tax

    def extract_tax_summary(self, lines: List[str], debug: bool = False) -> Dict[str, float]:
        """
        Extract tax summary lines (PRIMARY tax source).

        Looks for summary lines like:
        - "Porez (PDV)...: 1.71"        → PDV tax
        - "Porez na potronju...: 0.08"  → PNP tax

        Returns:
            Dict with individual tax types and total:
            {"PDV": 1.71, "PNP": 0.08, "total": 1.79}
        """
        tax_summary = {}

        # Patterns for tax summary lines
        summary_patterns = [
            (r'porez[\s.]*\(pdv\)[\s.:]*(\d+[.,]\d{1,2})', 'PDV'),      # Porez.(PDV)...: 1.71 or Porez (PDV): 1.71
            (r'porez\s+na\s+potro[sš]?nju[\s.:]*(\d+[.,]\d{1,2})', 'PNP'),  # Porez na potro(s)nju...: 0.08
            (r'porez\s+na\s+potro[sš]?nju[\s.:]*\d+\s+(\d+[.,]\d{1,2})', 'PNP'),  # Porez na potrosnju... 8 0,00 (edge case)
        ]

        for line in lines:
            line_clean = line.lower().strip()

            for pattern, tax_type in summary_patterns:
                match = re.search(pattern, line_clean)
                if match:
                    tax_str = match.group(1).replace(',', '.')
                    tax_amount = float(tax_str)

                    # Only add non-zero taxes
                    if tax_amount >= 0.01:
                        tax_summary[tax_type] = round(tax_amount, 2)
                        if debug:
                            logger.debug(f"[TAX SUMMARY] Found {tax_type}: {tax_amount:.2f} in '{line}'")

        # Calculate total
        if tax_summary:
            total = sum(tax_summary.values())
            tax_summary['total'] = round(total, 2)

            if debug:
                logger.debug(f"[TAX SUMMARY] Total tax: {total:.2f} from {len(tax_summary)-1} tax types")

        return tax_summary

    def extract_total_tax_simple(self, lines: List[str], debug: bool = False) -> Optional[float]:
        """
        Extract single tax amount from simple receipts.
        Looks for patterns like "Porez (PDV): 1.71" or "PDV 1,71"

        DEPRECATED: Use extract_tax_summary() instead for better coverage.
        """
        tax_patterns = [
            r'porez\s*\(pdv\)[:\s]*(\d+[.,]\d{2})',  # Porez (PDV): 1.71
            r'pdv[:\s]+(\d+[.,]\d{2})',               # PDV: 1.71
            r'tax[:\s]+(\d+[.,]\d{2})',               # Tax: 1.71
            r'vat[:\s]+(\d+[.,]\d{2})',               # VAT: 1.71
        ]

        for line in lines:
            line_clean = line.lower().strip()
            for pattern in tax_patterns:
                match = re.search(pattern, line_clean)
                if match:
                    tax_str = match.group(1).replace(',', '.')
                    tax_amount = float(tax_str)
                    if debug:
                        logger.debug(f"[TAX EXTRACTOR] Found simple tax: {tax_amount:.2f} in '{line}'")
                    return tax_amount

        return None

    def _find_tax_section(self, lines: List[str], debug: bool = False) -> int:
        """Find the start of tax breakdown section"""
        tax_section_markers = [
            r'rekapitula[cč]ija\s*pore[zž]a',  # Rekapitulacija poreza
            r'tax\s*breakdown',
            r'stopa\s+osnovica\s+iznos',       # Table header
            r'pdv.*osnovica.*iznos',
        ]

        for i, line in enumerate(lines):
            line_clean = line.lower().strip()
            for marker in tax_section_markers:
                if re.search(marker, line_clean):
                    if debug:
                        logger.debug(f"[TAX EXTRACTOR] Found tax section at line {i}: '{line}'")
                    return i

        return -1

    def _parse_tax_table(self, lines: List[str], start_idx: int, debug: bool = False) -> List[Dict]:
        """
        Parse tax breakdown table.

        Croatian receipts have TWO formats:

        Format A (Single line):
        Stopa    Osnovica    Iznos
        25,00    6,82        1,71

        Format B (Two lines - COMMON):
        PDV         1,71        ← Tax name and amount
        25,00  6,82            ← Rate and base
        """
        tax_entries = []

        # Look at next 15 lines after tax section marker
        i = start_idx + 1
        while i < min(start_idx + 16, len(lines)):
            line = lines[i].strip()

            # Check if this is a tax name line (PDV, PNP, etc.)
            tax_name_match = re.search(r'(pdv|pnp|porez)', line.lower())

            if tax_name_match:
                # Format B: Tax name with amount on current line, rate+base on next line
                numbers_current = re.findall(r'\d+[.,]\d{1,2}', line)

                if numbers_current and i + 1 < len(lines):
                    # Get next line for rate and base
                    next_line = lines[i + 1].strip()
                    numbers_next = re.findall(r'\d+[.,]\d{1,2}', next_line)

                    if len(numbers_next) >= 2:
                        # Current line: tax amount
                        # Next line: rate, base
                        tax_amount = float(numbers_current[0].replace(',', '.'))
                        rate = float(numbers_next[0].replace(',', '.'))
                        base = float(numbers_next[1].replace(',', '.'))

                        # Validate rate
                        rate = self._validate_tax_rate(rate, debug=debug)
                        if rate and tax_amount >= 0.01:
                            entry = {
                                "tax_rate": rate,
                                "taxable_base": round(base, 2),
                                "tax_amount": round(tax_amount, 2)
                            }

                            if self._validate_tax_math(rate, base, tax_amount, debug=debug):
                                tax_entries.append(entry)
                                if debug:
                                    logger.debug(f"[TAX] Format B: {rate}% on {base} = {tax_amount}")

                        i += 2  # Skip next line (already processed)
                        continue

            # Format A: Single line with all values
            numbers = re.findall(r'\d+[.,]\d{1,2}', line)
            if len(numbers) >= 3:
                entry = self._parse_tax_entry(numbers, line, debug=debug)
                if entry:
                    tax_entries.append(entry)

            i += 1

        return tax_entries

    def _parse_tax_entry(self, numbers: List[str], original_line: str, debug: bool = False) -> Optional[Dict]:
        """
        Parse a single tax entry line.

        Formats:
        - 3 numbers: [rate, base, amount]
        - 2 numbers: [rate, amount] (no base)
        """
        if len(numbers) < 2:
            return None

        try:
            # Convert to floats
            floats = [float(n.replace(',', '.')) for n in numbers]

            if len(floats) >= 3:
                # Full format: rate, base, amount
                rate, base, amount = floats[0], floats[1], floats[2]
            else:
                # Simple format: rate, amount
                rate, base, amount = floats[0], None, floats[1]

            # Validate and correct tax rate
            rate = self._validate_tax_rate(rate, debug=debug)
            if rate is None:
                return None

            # Skip if tax amount is 0 (often shown but not relevant)
            if amount < 0.01:
                if debug:
                    logger.debug(f"[TAX EXTRACTOR] Skipping zero-tax entry: rate={rate}%")
                return None

            # Build entry
            entry = {
                "tax_rate": rate,
                "tax_amount": round(amount, 2)
            }

            # Add base if present
            if base is not None:
                entry["taxable_base"] = round(base, 2)

                # Validate math if base exists
                if not self._validate_tax_math(rate, base, amount, debug=debug):
                    if debug:
                        logger.debug(f"[TAX EXTRACTOR] Math validation failed for entry")

            if debug:
                logger.debug(f"[TAX EXTRACTOR] Parsed tax entry: {entry}")

            return entry

        except (ValueError, IndexError) as e:
            if debug:
                logger.debug(f"[TAX EXTRACTOR] Failed to parse tax entry from '{original_line}': {e}")
            return None

    def _validate_tax_rate(self, rate: float, debug: bool = False) -> Optional[float]:
        """
        Validate tax rate against Croatian standards.
        Auto-correct obvious OCR errors.
        """
        # Check if rate is already valid
        if rate in self.croatian_rates:
            return rate

        # Try to find closest valid rate (OCR error correction)
        closest_rate = min(self.croatian_rates, key=lambda x: abs(x - rate))
        distance = abs(closest_rate - rate)

        # If within 5 percentage points, likely OCR error
        if distance <= 5.0:
            if debug:
                logger.debug(f"[TAX EXTRACTOR] Correcting invalid rate {rate}% → {closest_rate}%")
            return closest_rate

        # Too far from any valid rate
        if debug:
            logger.debug(f"[TAX EXTRACTOR] Invalid tax rate {rate}% (not a Croatian standard rate)")
        return None

    def _validate_tax_math(self, rate: float, base: float, amount: float, debug: bool = False) -> bool:
        """
        Validate: base × (rate / 100) ≈ amount
        Tolerance: 0.02 EUR (2 cents) due to rounding
        """
        expected_amount = base * (rate / 100.0)
        difference = abs(expected_amount - amount)

        if difference > 0.02:
            if debug:
                logger.debug(f"[TAX MATH] {base} × {rate}% = {expected_amount:.2f}, "
                           f"but got {amount:.2f} (diff: {difference:.2f})")
            return False

        return True
