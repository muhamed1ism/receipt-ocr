"""
Receipt Schema Detection and Validation
========================================
Detects the format/structure of a receipt and validates data against it.

Key Concepts:
1. Schema Detection - Identify if items follow "price × quantity = total"
2. Field Grouping - Related fields appear together (total, tax, payment)
3. Optional Fields - Don't force-search for missing fields (if no tax, don't look for it)
"""

import re
import logging
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ReceiptSchema:
    """Detected schema for a receipt"""
    # Item format validation
    has_price_qty_total_format: bool = False  # Does price × qty = total hold?

    # Optional fields detected
    has_tax: bool = False
    has_subtotal: bool = False
    has_payment_method: bool = False
    has_change: bool = False

    # Currency and payment
    currency: str = "EUR"  # Default for Croatia
    payment_method: Optional[str] = None  # "GOTOVINA" or "KARTICA" or None

    # Field locations (line indices)
    tax_line: Optional[int] = None
    subtotal_line: Optional[int] = None
    total_line: Optional[int] = None

    # Validation stats
    items_validated: int = 0
    items_failed_validation: int = 0
    confidence: float = 0.0


class ReceiptSchemaDetector:
    """Detects and validates receipt schema/format"""

    def __init__(self):
        self.schema: Optional[ReceiptSchema] = None

    def detect_schema(self, lines: List[str], items: List[Dict[str, Any]],
                     sections: Dict[str, Tuple[int, int]], debug: bool = False) -> ReceiptSchema:
        """
        Analyze receipt and detect its schema/format.

        Args:
            lines: All receipt lines
            items: Extracted items (to analyze format)
            sections: Section boundaries from section_detector
            debug: Enable debug logging

        Returns:
            ReceiptSchema with detected format and optional fields
        """
        if debug:
            logger.debug("[SCHEMA DETECTOR] Analyzing receipt format")

        schema = ReceiptSchema()

        # 1. Check if items follow price × qty = total pattern
        if items:
            schema.has_price_qty_total_format = self._check_price_math_pattern(items, debug=debug)

        # 2. Check for optional fields in totals section (don't force if not there)
        if 'totals' in sections:
            totals_start, totals_end = sections['totals']
            totals_lines = lines[totals_start:totals_end]
            schema = self._detect_optional_fields(totals_lines, schema, totals_start, debug=debug)

        # 3. Calculate schema confidence
        schema.confidence = self._calculate_schema_confidence(schema, items)

        if debug:
            logger.debug(f"[SCHEMA] Has price×qty=total format: {schema.has_price_qty_total_format}")
            logger.debug(f"[SCHEMA] Optional fields - Tax: {schema.has_tax}, "
                        f"Subtotal: {schema.has_subtotal}, Payment: {schema.has_payment_method}")
            logger.debug(f"[SCHEMA] Confidence: {schema.confidence:.2%}")

        self.schema = schema
        return schema

    def _check_price_math_pattern(self, items: List[Dict[str, Any]], debug: bool = False) -> bool:
        """
        Check if items follow the pattern: price × quantity = total

        Returns True if 70%+ of items follow this rule.
        """
        if not items:
            return False

        valid_count = 0
        total_count = len(items)

        for item in items:
            qty = item.get('quantity', 1)
            price = item.get('price_per_item', 0)
            total = item.get('total', 0)

            # Check if math adds up (5 cent tolerance)
            expected_total = qty * price
            if abs(expected_total - total) < 0.05:
                valid_count += 1
                if debug:
                    logger.debug(f"[SCHEMA] ✓ {item['name']}: {price} × {qty} = {total}")
            elif debug:
                logger.debug(f"[SCHEMA] ✗ {item['name']}: {price} × {qty} ≠ {total} "
                           f"(expected {expected_total:.2f})")

        validation_rate = valid_count / total_count
        has_pattern = validation_rate >= 0.7  # 70%+ must validate

        if debug:
            logger.debug(f"[SCHEMA] Math validation: {valid_count}/{total_count} = {validation_rate:.0%}")

        return has_pattern

    def _detect_optional_fields(self, totals_lines: List[str], schema: ReceiptSchema,
                               offset: int, debug: bool = False) -> ReceiptSchema:
        """
        Detect optional fields in totals section.
        Only mark as present if actually found - don't force-search.
        """
        for i, line in enumerate(totals_lines):
            line_lower = line.lower()

            # Tax/PDV - only if present
            if re.search(r'(pdv|porez|tax|vat).*\d+[.,]\d{2}', line_lower):
                schema.has_tax = True
                schema.tax_line = offset + i
                if debug:
                    logger.debug(f"[SCHEMA] Found tax at line {offset + i}: {line}")

            # Subtotal - only if present
            if re.search(r'(subtotal|međuzbroj|medjuzbroj)', line_lower):
                schema.has_subtotal = True
                schema.subtotal_line = offset + i
                if debug:
                    logger.debug(f"[SCHEMA] Found subtotal at line {offset + i}: {line}")

            # Payment method - only if present, EXTRACT the actual method
            # Note: OCR often reads ć as j or c, so we need flexible patterns
            payment_match = re.search(r'(pla[cč]anj[ae]|pla[aá]nja|payment|nain.*pla|gotovina|kartica|cash|card|nov[cč]anic)', line_lower)
            if payment_match:
                schema.has_payment_method = True
                # Extract the actual payment method value
                schema.payment_method = self._extract_payment_method(line, debug=debug)
                if debug:
                    logger.debug(f"[SCHEMA] Found payment method at line {offset + i}: {line}")
                    logger.debug(f"[SCHEMA] Payment method: {schema.payment_method}")

            # Change/Kusur - only if present
            if re.search(r'(kusur|povrat|change).*\d+[.,]\d{2}', line_lower):
                schema.has_change = True
                if debug:
                    logger.debug(f"[SCHEMA] Found change at line {offset + i}: {line}")

            # Total
            if re.search(r'(ukupno|total|suma).*\d+[.,]\d{2}', line_lower):
                schema.total_line = offset + i

        return schema

    def _calculate_schema_confidence(self, schema: ReceiptSchema, items: List[Dict[str, Any]]) -> float:
        """Calculate confidence in detected schema"""
        confidence = 0.0

        # Base confidence from price math pattern
        if schema.has_price_qty_total_format:
            confidence += 0.6

        # Boost if we found total line
        if schema.total_line is not None:
            confidence += 0.2

        # Boost if items exist
        if items and len(items) > 0:
            confidence += 0.2

        return min(confidence, 1.0)

    def validate_items_against_schema(self, items: List[Dict[str, Any]],
                                     schema: ReceiptSchema, debug: bool = False) -> List[Dict[str, Any]]:
        """
        Validate items against detected schema.

        If schema has price×qty=total pattern, validate that rule.
        Remove items that don't pass validation.

        Returns:
            List of items that passed validation
        """
        valid_items = []

        for item in items:
            if self._validate_item(item, schema, debug=debug):
                valid_items.append(item)
                schema.items_validated += 1
            else:
                schema.items_failed_validation += 1
                if debug:
                    logger.debug(f"[SCHEMA VALIDATION FAILED] {item}")

        return valid_items

    def _validate_item(self, item: Dict[str, Any], schema: ReceiptSchema, debug: bool = False) -> bool:
        """Validate a single item against schema rules"""
        qty = item.get('quantity', 1)
        price = item.get('price_per_item', 0)
        total = item.get('total', 0)

        # If schema expects price×qty=total, enforce it
        if schema.has_price_qty_total_format:
            expected_total = qty * price
            if abs(expected_total - total) > 0.05:
                if debug:
                    logger.debug(f"[VALIDATION] Math failed: {price} × {qty} = {expected_total}, "
                               f"but got {total} (diff: {abs(expected_total - total):.2f})")
                return False

        # Rule: Name should not be too short (likely parsing error)
        name = item.get('name', '')
        if len(name) < 2:
            if debug:
                logger.debug(f"[VALIDATION] Name too short: '{name}'")
            return False

        # Rule: Name should not be a number or address
        if re.match(r'^[\d\s.,:-]+$', name):
            if debug:
                logger.debug(f"[VALIDATION] Name looks like number: '{name}'")
            return False

        return True

    def _extract_payment_method(self, line: str, debug: bool = False) -> Optional[str]:
        """
        Extract payment method value from line.
        Normalizes to "GOTOVINA" (cash) or "KARTICA" (card).
        """
        line_lower = line.lower()

        # Cash patterns (Croatian and English)
        # OCR variations: ć→c/j, č→c, e→ice at end
        cash_patterns = [
            r'gotovina',
            r'nov[cč]ani[cč][ei]',  # novčanice / novčaniče with OCR variations
            r'novcanic',            # Common OCR error
            r'cash',
        ]

        # Card patterns (Croatian and English)
        card_patterns = [
            r'kartica',
            r'kartic',
            r'card',
            r'kredit',
            r'debit',
        ]

        # Check for cash
        for pattern in cash_patterns:
            if re.search(pattern, line_lower):
                return "GOTOVINA"

        # Check for card
        for pattern in card_patterns:
            if re.search(pattern, line_lower):
                return "KARTICA"

        # Default: if payment method detected but can't classify
        if debug:
            logger.debug(f"[SCHEMA] Could not classify payment method in: {line}")
        return None
