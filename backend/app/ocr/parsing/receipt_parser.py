"""
Croatian Receipt Parser - Main Orchestrator
===========================================
Coordinates all specialized modules for parsing Croatian receipts.
"""

import logging
import re
from typing import List, Dict, Any

from .text_preprocessing.text_cleaner import TextCleaner
from .extractors.section_detector import ReceiptSectionDetector
from .schema.receipt_schema_detector import ReceiptSchemaDetector
from .extractors.tax_extractor import TaxExtractor
from .extractors.company_info_extractor import CompanyInfoExtractor
from .extractors.fiscal_extractor import FiscalExtractor
from .extractors.store_extractor import StoreExtractor
from .extractors.item_extractor import ItemExtractor
from .extractors.total_extractor import TotalExtractor
from .extractors.date_extractor import DateExtractor
from .validators.item_validator import ItemValidator
from .validators.receipt_validator import ReceiptValidator
from .extractors.tab_separated_parser import TabSeparatedParser

logger = logging.getLogger(__name__)


class ReceiptParser:
    """Main orchestrator for Croatian receipt parsing"""
    
    def __init__(self):
        """Initialize all specialized parsing components"""
        self.text_cleaner = TextCleaner()
        self.section_detector = ReceiptSectionDetector()
        self.schema_detector = ReceiptSchemaDetector()
        self.tax_extractor = TaxExtractor()
        self.company_info_extractor = CompanyInfoExtractor()
        self.fiscal_extractor = FiscalExtractor()
        self.store_extractor = StoreExtractor()
        self.item_extractor = ItemExtractor()
        self.total_extractor = TotalExtractor()
        self.date_extractor = DateExtractor()
        self.item_validator = ItemValidator()
        self.receipt_validator = ReceiptValidator()
        self.structured_parser = TabSeparatedParser()
    
    def parse_receipt(self, lines: List[str], log_debug: bool = False) -> Dict[str, Any]:
        """Main parsing function - flexible receipt parsing for variable formats"""
        if log_debug:
            logger.setLevel(logging.DEBUG)

        clean_lines = [line.strip() for line in lines if line.strip()]

        if not clean_lines:
            return self.receipt_validator.create_empty_receipt()

        # Detect receipt country (Croatian, Bosnian, or Unknown)
        country = self._detect_receipt_country(clean_lines)
        if log_debug:
            logger.debug(f"[COUNTRY DETECTION] Receipt country: {country}")

        try:
            # First try structured parsing for well-formatted receipts
            if self._is_structured_receipt(clean_lines):
                if log_debug:
                    logger.debug("=== TRYING STRUCTURED PARSING ===")
                structured_result = self.structured_parser.parse_structured_receipt(clean_lines, debug=log_debug)
                
                # If structured parsing was successful, use it
                if structured_result.get("parsed_items_count", 0) > 0 or structured_result.get("confidence", 0) > 0.5:
                    if log_debug:
                        logger.debug(f"[STRUCTURED SUCCESS] Found {structured_result.get('parsed_items_count', 0)} items")
                    return structured_result
                elif log_debug:
                    logger.debug("[STRUCTURED FAILED] Falling back to flexible parsing")
            
            # Fallback to flexible parsing WITH SECTION DETECTION
            if log_debug:
                logger.debug("=== FLEXIBLE PARSING WITH SECTIONS ===")
                for i, line in enumerate(clean_lines[:15]):
                    logger.debug(f"{i:2d}: '{line}'")

            # STEP 1: Detect receipt sections
            sections = self.section_detector.detect_sections(clean_lines, debug=log_debug)

            # STEP 2: Extract from correct sections
            # Store name & Company info
            header_lines = self.section_detector.get_section_lines(clean_lines, 'header', sections)

            # BOSNIAN FORMAT: Store name is FIRST line of receipt
            if country == "BA" and clean_lines:
                full_line = clean_lines[0].strip()

                # Remove city name from store name (e.g., "KONZUM d.o.o. SARAJEVO" → "KONZUM d.o.o.")
                # Common Bosnian cities: SARAJEVO, MOSTAR, BANJA LUKA, TUZLA, ZENICA, JABLANICA, etc.
                city_pattern = r'\s+(SARAJEVO|MOSTAR|BANJA\s+LUKA|TUZLA|ZENICA|JABLANICA|BIHAC|TREBINJE|LIVNO|KONJIC)$'
                store_name = re.sub(city_pattern, '', full_line, flags=re.IGNORECASE).strip()

                if log_debug:
                    logger.debug(f"[BOSNIAN] Extracted store from line 0: '{full_line}' → '{store_name}'")
            else:
                # CROATIAN FORMAT: Store name in header section
                store_name = self.store_extractor.extract_store_name_flexible(header_lines) if header_lines else "Unknown Store"

            # Company info (address, business registration, owner)
            # NOTE: We pass header_lines for company text extraction
            # But we pass clean_lines[:10] (first 10 lines of receipt) for business ID extraction
            # This ensures we catch JIB/PIB/IBFM even if section detector cuts header too short
            company_info = self.company_info_extractor.extract_company_info(
                header_lines,
                debug=log_debug
            ) if header_lines else None

            # Extract business IDs separately using first 10 lines of receipt
            # This avoids issues where section detector might cut header too early
            # USE EXPLICIT EXTRACTION for better accuracy
            if company_info:
                business_ids = self.company_info_extractor.extract_business_ids_explicit(
                    clean_lines,  # Pass all lines, method searches in header (0-10)
                    debug=log_debug
                )
                # Merge business IDs into company_info
                company_info.update(business_ids)

            # Date and time - USE EXPLICIT EXTRACTION
            # Searches in lines 4-12 where date/time typically appears
            date, time = self.date_extractor.extract_date_time_explicit(clean_lines, debug=log_debug)

            # Items - USE COUNTRY-SPECIFIC EXTRACTION
            # Get items section from section detector
            items_lines = self.section_detector.get_section_lines(clean_lines, 'items', sections)

            # If section detector didn't find items section, use bounded extraction
            if items_lines:
                # Use country-aware extraction (Bosnian 3-line vs Croatian single-line)
                items = self.item_extractor.extract_items_from_section(items_lines, country=country, debug=log_debug)
            else:
                # Fallback: Use bounded extraction (FISKALNI → TOTAL)
                if log_debug:
                    logger.debug("[ITEMS] No items section found, using bounded extraction")
                items = self.item_extractor.extract_items_with_boundaries(clean_lines, debug=log_debug)

            # Total - USE EXPLICIT EXTRACTION
            # Searches for TOTAL:/UKUPNO:/SUMA: keywords
            total = self.total_extractor.extract_total_explicit(clean_lines, debug=log_debug)

            # Tax - extract tax information
            # Tax information often appears after the items and before payment methods
            # Get footer section for tax extraction
            footer_lines = self.section_detector.get_section_lines(clean_lines, 'footer', sections)
            tax_search_lines = footer_lines if footer_lines else clean_lines

            # STEP 1: Extract tax summary (PRIMARY source)
            # Summary lines like "Porez (PDV): 1.71", "Porez na potronju: 0.08"
            tax_summary = self.tax_extractor.extract_tax_summary(
                tax_search_lines, debug=log_debug
            )

            # STEP 2: Extract tax breakdown (FALLBACK/VALIDATION source)
            # Detailed table with rates, bases, and amounts
            tax_breakdown, breakdown_total_tax = self.tax_extractor.extract_tax_breakdown(
                tax_search_lines, debug=log_debug
            )
            #this is a cool test
            # STEP 3: Determine total_tax (prefer summary, fallback to breakdown)
            total_tax = 0.0
            if tax_summary and 'total' in tax_summary:
                total_tax = tax_summary['total']
                if log_debug:
                    logger.debug(f"[TAX] Using tax summary: {total_tax:.2f} from {tax_summary}")

                # Validate against breakdown if both exist
                if tax_breakdown and abs(total_tax - breakdown_total_tax) > 0.02:
                    logger.warning(f"[TAX MISMATCH] Summary: {total_tax:.2f} vs Breakdown: {breakdown_total_tax:.2f}")

            elif tax_breakdown:
                total_tax = breakdown_total_tax
                if log_debug:
                    logger.debug(f"[TAX] Using tax breakdown total: {total_tax:.2f}")

            else:
                # Last resort: simple extraction (deprecated)
                simple_tax = self.tax_extractor.extract_total_tax_simple(
                    tax_search_lines, debug=log_debug
                )
                if simple_tax:
                    total_tax = simple_tax
                    if log_debug:
                        logger.debug(f"[TAX] Using simple extraction: {total_tax:.2f}")

            # Calculate Total Before Tax (TBT)
            total_before_tax = None
            if total_tax and total_tax > 0 and total:
                total_before_tax = round(total - total_tax, 2)
                if log_debug:
                    logger.debug(f"[TBT CALCULATION] {total} - {total_tax} = {total_before_tax}")

            # Fiscal codes (ZKI, JIR) - from FOOTER section
            fiscal_codes = self.fiscal_extractor.extract_fiscal_codes(
                footer_lines if footer_lines else clean_lines, debug=log_debug
            )

            # STEP 3: Detect receipt schema and validate items against it
            schema = self.schema_detector.detect_schema(clean_lines, items, sections, debug=log_debug)

            # Override currency based on detected country
            if schema and country == "BA":
                schema.currency = "BAM"  # Bosnian Convertible Mark
                if log_debug:
                    logger.debug("[CURRENCY] Bosnian receipt detected → currency set to BAM")
            elif schema and country == "HR":
                schema.currency = "EUR"  # Euro (Croatia uses EUR since 2023)
                if log_debug:
                    logger.debug("[CURRENCY] Croatian receipt detected → currency set to EUR")

            # Validate items against schema (enforces price×qty=total if schema has that pattern)
            if items and schema:
                items = self.schema_detector.validate_items_against_schema(items, schema, debug=log_debug)
                if log_debug:
                    logger.debug(f"[SCHEMA VALIDATION] {schema.items_validated} items passed, "
                               f"{schema.items_failed_validation} failed")

            # Additional validation and cleanup
            if items:
                items = self.item_validator.validate_and_clean_items(items, total, debug=log_debug)
                if log_debug:
                    logger.debug(f"[VALIDATION] Final item count after validation: {len(items)}")
            
            # Calculate confidence score
            confidence = self.receipt_validator.calculate_confidence(store_name, date, items, total)

            # Build result with all new fields
            result = {
                "store": store_name,
                "country": country,  # "HR" (Croatia), "BA" (Bosnia), or "UNKNOWN"
                "company_info": company_info,  # Address, business registration, owner
                "date": date,
                "time": time,

                # Currency and totals
                "currency": schema.currency if schema else "EUR",
                "total": total,
                "total_before_tax": total_before_tax,
                "total_tax": total_tax,

                # Display fields (optional, for UI)
                "total_display": f"{total:.2f} {schema.currency}" if total and schema else None,
                "total_before_tax_display": f"{total_before_tax:.2f} {schema.currency}" if total_before_tax and schema else None,

                # Tax information (simplified - just total tax amount)
                "tax_summary": tax_summary if tax_summary else None,  # Summary by tax type (PDV, PNP) - kept for compatibility

                # Payment method (for data analysis)
                "payment_method": schema.payment_method if schema else None,

                # Croatian identifiers
                "oib": company_info.get("oib") if company_info else None,
                "zki": fiscal_codes.get("zki"),
                "jir": fiscal_codes.get("jir"),

                # Bosnian identifiers
                "jib": company_info.get("jib") if company_info else None,
                "pib": company_info.get("pib") if company_info else None,
                "ibfm": company_info.get("ibfm") if company_info else None,
                "digital_signature": fiscal_codes.get("digital_signature"),

                # Items
                "items": items,

                # Metadata
                "confidence": confidence,
                "error": None,
                "raw_lines_count": len(clean_lines),
                "parsed_items_count": len(items)
            }
            
            if log_debug:
                logger.debug(f"[RESULT] Store: {store_name}, Items: {len(items)}, Total: {total}, Confidence: {confidence:.2f}")
            
            return result
            
        except Exception as e:
            logger.error(f"Receipt parsing failed: {str(e)}")
            return self.receipt_validator.create_empty_receipt(error=str(e))
    
    def _is_structured_receipt(self, lines: List[str]) -> bool:
        """Detect if this is a structured receipt with tab-separated format"""
        # Look for the characteristic structured format indicators
        for line in lines:
            line_lower = line.lower()
            
            # Check for structured header pattern
            if ('naziv' in line_lower and 'cijena' in line_lower and 
                'kol' in line_lower and 'iznos' in line_lower):
                return True
            
            # Check for tab-separated content (more than 2 tabs suggests structured format)
            if line.count('\t') >= 2:
                return True
        
        return False

    def _detect_receipt_country(self, lines: List[str]) -> str:
        """
        Auto-detect receipt country based on identifiers and patterns.

        Returns:
            "HR" (Croatia), "BA" (Bosnia), or "UNKNOWN"
        """
        text_blob = " ".join(lines).upper()

        # Bosnian indicators (check first - more specific)
        bosnian_indicators = [
            'JIB', 'PIB', 'IBFM',  # Business IDs
            'CONFIG FISCAL', 'CONFIG-FISCAL', 'CONFIGFISCAL',  # Footer branding
            'FISKALNI RACUN', 'FISKALNI',  # Receipt type
            'MOSTAR', 'JABLANICA', 'SARAJEVO', 'BANJA LUKA', 'TUZLA', 'ZENICA',  # Cities
            'KONZU', 'BINGO', 'DIONI'  # Common Bosnian stores
        ]

        # Croatian indicators
        croatian_indicators = [
            'ZKI', 'JIR', 'OIB',
            'SPLIT', 'ZAGREB', 'RIJEKA', 'DUBROVNIK', 'OSIJEK', 'ZADAR'
        ]

        # Check for currency display - Bosnian receipts DON'T show currency symbols
        # Croatian receipts show EUR
        has_currency = bool(re.search(r'\b(EUR|€)\b', text_blob))

        # Count indicators
        bosnian_count = sum(1 for ind in bosnian_indicators if ind in text_blob)
        croatian_count = sum(1 for ind in croatian_indicators if ind in text_blob)

        # Bosnian detection (priority)
        if bosnian_count > 0:
            return "BA"

        # Croatian detection
        if croatian_count > 0 or has_currency:
            return "HR"

        return "UNKNOWN"


def parse_receipt(lines: List[str], log_debug: bool = False) -> Dict[str, Any]:
    """Convenience function for backward compatibility"""
    parser = ReceiptParser()
    return parser.parse_receipt(lines, log_debug=log_debug)