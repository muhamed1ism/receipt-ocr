"""
Tab-Separated Croatian Receipt Parser
====================================
Specialized parser for Croatian receipts with tab-separated format.
Different from receipt_parser.py which is the main parsing orchestrator.
"""

import re
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class TabSeparatedParser:
    """Parser for Croatian receipts with tab-separated item format"""
    
    def __init__(self):
        """Initialize the structured parser"""
        self.debug = False
    
    def parse_structured_receipt(self, lines: List[str], debug: bool = False) -> Dict[str, Any]:
        """
        Parse structured Croatian receipt with tab-separated format
        
        Expected format:
        Line 1-2: Store name
        Line 7: Header (Naziv Cijena Kol. Iznos)  
        Line 8-N: Items in format: NAME [tab] PRICE [tab] QUANTITY [tab] TOTAL
        """
        self.debug = debug
        if debug:
            logger.debug("=== STRUCTURED RECEIPT PARSING ===")
            for i, line in enumerate(lines[:15]):
                logger.debug(f"Line {i+1:2d}: '{line}'")
        
        # Clean the lines - remove prefixes like "line1 - "
        clean_lines = []
        for line in lines:
            if line.startswith("line") and " - " in line:
                # Remove "line1 - " prefix
                clean_line = line.split(" - ", 1)[1] if " - " in line else line
                clean_lines.append(clean_line)
            else:
                clean_lines.append(line)
        
        if debug:
            logger.debug("\n=== CLEANED LINES ===")
            for i, line in enumerate(clean_lines[:15]):
                logger.debug(f"Clean {i+1:2d}: '{line}'")
        
        try:
            # Parse store name (lines 1-2)
            store_name = self._extract_store_name(clean_lines)
            
            # Parse date and time
            date, time = self._extract_date_time(clean_lines)
            
            # Find items section and parse items
            items = self._extract_structured_items(clean_lines, debug=debug)
            
            # Extract total
            total = self._extract_total(clean_lines)
            
            # Calculate confidence based on successful parsing
            confidence = self._calculate_confidence(store_name, items, total)
            
            result = {
                "store": store_name,
                "location_label": None,
                "date": date,
                "time": time,
                "total": total,
                "items": items,
                "confidence": confidence,
                "error": None,
                "raw_lines_count": len(clean_lines),
                "parsed_items_count": len(items),
                "parsing_method": "structured_tab_separated"
            }
            
            if debug:
                logger.debug(f"[STRUCTURED RESULT] Store: {store_name}, Items: {len(items)}, Total: {total}, Confidence: {confidence:.2f}")
            
            return result
            
        except Exception as e:
            if debug:
                logger.error(f"Structured parsing failed: {e}")
            return {
                "store": None,
                "location_label": None, 
                "date": None,
                "time": None,
                "total": None,
                "items": [],
                "confidence": 0.0,
                "error": str(e),
                "raw_lines_count": len(clean_lines),
                "parsed_items_count": 0,
                "parsing_method": "structured_tab_separated"
            }
    
    def _extract_store_name(self, lines: List[str]) -> Optional[str]:
        """
        Extract store name from header lines.

        Handles Croatian address patterns like:
        Line 0: "Caffe bar"
        Line 1: "Ruđera Boškovića 23, 21000 Split RETRO"

        Returns: "Caffe bar RETRO" (business type + store name)
        """
        if len(lines) < 2:
            return None

        line1 = lines[0].strip().strip('"')  # "Caffe bar"
        line2 = lines[1].strip().strip('"')  # "Ruđera Boškovića 23, 21000 Split RETRO"

        # Check if line2 contains Croatian address pattern (5-digit postal code)
        # Pattern: "Street, PostalCode City StoreName"
        # Example: "Ruđera Boškovića 23, 21000 Split RETRO"
        address_pattern = r'(\d{5})\s+([A-ZČĆŽŠĐ][a-zčćžšđ]+)\s+(.+)$'
        match = re.search(address_pattern, line2)

        if match:
            # Extract store name from AFTER the city name
            store_name = match.group(3).strip()  # "RETRO"

            # Remove quotes if present
            store_name = store_name.strip('"').strip("'")

            # Combine with business type if line1 is a descriptor
            business_types = ['caffe bar', 'bar', 'restoran', 'pekara',
                            'bistro', 'pizzeria', 'kafić', 'trgovina']
            if line1.lower() in business_types:
                return f"{line1} {store_name}"  # "Caffe bar RETRO"
            else:
                return store_name  # "RETRO"

        # Fallback: no address pattern found, combine both lines (old behavior)
        # Handle case where line2 might be in quotes
        if line2.startswith('"') and line2.endswith('"'):
            line2 = line2[1:-1]

        store_name = f"{line1} {line2}".strip()
        return store_name if store_name else None
    
    def _extract_date_time(self, lines: List[str]) -> tuple:
        """
        Extract date and time from the receipt.

        Handles formats:
        - "Datum : 25.06.2025 14:02"
        - "Račun broj : Datum : 25.06.2025 14:02"
        - "datum: 25/06/2025 14:02"

        Returns: (date, time) tuple in format ("YYYY-MM-DD", "HH:MM")
        """
        # More flexible pattern - allows optional text before "datum"
        # Allows dots or slashes as separators
        # Matches: "Datum : 25.06.2025 14:02" or "Račun broj : Datum : 25.06.2025 14:02"
        date_pattern = r'datum\s*:?\s*(\d{1,2})[.,/](\d{1,2})[.,/](\d{4})\s+(\d{1,2}):(\d{2})'

        for line in lines:
            match = re.search(date_pattern, line, re.IGNORECASE)
            if match:
                day, month, year, hour, minute = match.groups()
                # Convert to ISO format
                date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"  # "2025-06-25"
                time = f"{hour.zfill(2)}:{minute}"  # "14:02"
                return date, time

        return None, None
    
    def _extract_structured_items(self, lines: List[str], debug: bool = False) -> List[Dict[str, Any]]:
        """Extract items from tab-separated format"""
        items = []

        # Find the items header line (contains "Naziv", "Cijena", "Kol", "Iznos")
        items_start = -1
        column_order = 'standard'  # or 'reversed'

        for i, line in enumerate(lines):
            line_lower = line.lower()
            if ('naziv' in line_lower and 'cijena' in line_lower and
                'kol' in line_lower and 'iznos' in line_lower):
                items_start = i + 1  # Items start on next line

                # Detect column order: standard (Naziv first) or reversed (Kol first)
                naziv_pos = line_lower.find('naziv')
                kol_pos = line_lower.find('kol')

                if kol_pos < naziv_pos:
                    column_order = 'reversed'
                    if debug:
                        logger.debug(f"Detected REVERSED column order: Kol-Iznos-Cijena-Naziv")
                else:
                    column_order = 'standard'
                    if debug:
                        logger.debug(f"Detected STANDARD column order: Naziv-Cijena-Kol-Iznos")

                if debug:
                    logger.debug(f"Found items header at line {i+1}, items start at line {items_start+1}")
                break

        if items_start == -1:
            if debug:
                logger.debug("No items header found")
            return []

        # Parse items until we hit a line that doesn't look like an item
        for i in range(items_start, len(lines)):
            line = lines[i].strip()
            if not line:
                continue

            # Stop parsing items if we hit total line or other sections
            line_lower = line.lower()
            if ('ukupno' in line_lower or 'način' in line_lower or
                'račun' in line_lower or 'datum' in line_lower or
                'porez' in line_lower):
                if debug:
                    logger.debug(f"Stopping item parsing at line {i+1}: '{line}'")
                break

            # Try to parse this line as an item
            item = self._parse_item_line(line, column_order, debug=debug)
            if item:
                items.append(item)
            else:
                if debug:
                    logger.debug(f"Could not parse as item: '{line}'")

        return items
    
    def _parse_item_line(self, line: str, column_order: str = 'standard', debug: bool = False) -> Optional[Dict[str, Any]]:
        """
        Parse a single item line in tab-separated format

        Args:
            line: The line to parse
            column_order: 'standard' (Naziv-Cijena-Kol-Iznos) or 'reversed' (Kol-Iznos-Cijena-Naziv)
            debug: Enable debug logging
        """
        if not line.strip():
            return None

        # Split by tabs first, then by multiple spaces as fallback
        parts = line.split('\t')
        if len(parts) < 2:
            # Fallback: split by multiple spaces
            parts = re.split(r'\s{2,}', line)

        if debug:
            logger.debug(f"Item line parts: {parts} (column_order={column_order})")

        # We expect different formats based on column order
        if len(parts) >= 3:
            try:
                if column_order == 'reversed':
                    # REVERSED FORMAT: [QUANTITY, TOTAL, PRICE, NAME]
                    # Example: "2,10\t1,00\t2,10\tKAVA MLIJEKO VELIK"
                    # Wait, let me re-check the data...
                    # Based on header "Kol. Iznos Cijena Naziv" and data "2,10 1,00 2,10 KAVA MLIJEKO VELIK"
                    # Actually: Kol=1,00  Iznos=2,10  Cijena=2,10  Naziv=KAVA MLIJEKO VELIK
                    # The OCR might be reading left-to-right incorrectly!

                    # Let's parse all parts
                    all_parts = [p.strip() for p in parts if p.strip()]

                    # Find name (last part that's not numeric)
                    name = None
                    numeric_parts = []

                    for part in all_parts:
                        if self._is_numeric(part):
                            numeric_parts.append(float(part.replace(',', '.')))
                        else:
                            name = part  # Take the first non-numeric as name

                    if not name or len(numeric_parts) < 2:
                        if debug:
                            logger.debug(f"Not enough data: name={name}, numeric_parts={numeric_parts}")
                        return None

                    # Reversed format: [QTY, TOTAL, PRICE] or [TOTAL, QTY, PRICE]
                    # Based on header "Kol. Iznos Cijena Naziv"
                    if len(numeric_parts) >= 3:
                        quantity = numeric_parts[0]  # Kol.
                        total = numeric_parts[1]     # Iznos
                        price = numeric_parts[2]     # Cijena
                    elif len(numeric_parts) == 2:
                        price = numeric_parts[0]
                        total = numeric_parts[1]
                        quantity = 1.0
                    else:
                        price = numeric_parts[0]
                        total = numeric_parts[0]
                        quantity = 1.0

                else:
                    # STANDARD FORMAT: [NAME, PRICE, QUANTITY, TOTAL]
                    # Extract name (first part)
                    name = parts[0].strip()
                    if not name:
                        return None

                    # Find numeric values in the remaining parts
                    numeric_parts = []
                    for part in parts[1:]:
                        part = part.strip()
                        if part and self._is_numeric(part):
                            numeric_parts.append(float(part.replace(',', '.')))

                    if debug:
                        logger.debug(f"Numeric parts found: {numeric_parts}")

                    # Determine price, quantity, total based on what we have
                    if len(numeric_parts) >= 3:
                        # Format: NAME PRICE QUANTITY TOTAL
                        price = numeric_parts[0]
                        quantity = numeric_parts[1]
                        total = numeric_parts[2]
                    elif len(numeric_parts) == 2:
                        # Format: NAME PRICE TOTAL (assume quantity = 1)
                        price = numeric_parts[0]
                        quantity = 1.0
                        total = numeric_parts[1]
                    elif len(numeric_parts) == 1:
                        # Format: NAME TOTAL (assume price = total, quantity = 1)
                        price = numeric_parts[0]
                        quantity = 1.0
                        total = numeric_parts[0]
                    else:
                        return None

                item = {
                    "name": name,
                    "quantity": quantity,
                    "price_per_item": price,
                    "total": total,
                    "extraction_method": f"structured_tab_separated_{column_order}"
                }

                if debug:
                    logger.debug(f"Parsed item: {item}")

                return item

            except (ValueError, IndexError) as e:
                if debug:
                    logger.debug(f"Failed to parse item line '{line}': {e}")
                return None

        return None
    
    def _is_numeric(self, value: str) -> bool:
        """Check if a string represents a numeric value"""
        try:
            # Handle European decimal format (comma as decimal separator)
            test_value = value.replace(',', '.')
            float(test_value)
            return True
        except ValueError:
            return False
    
    def _extract_total(self, lines: List[str]) -> Optional[float]:
        """Extract total amount from UKUPNO line"""
        total_pattern = r'ukupno.*?(\d+[.,]\d+)'
        
        for line in lines:
            line_lower = line.lower()
            match = re.search(total_pattern, line_lower)
            if match:
                total_str = match.group(1).replace(',', '.')
                try:
                    return float(total_str)
                except ValueError:
                    continue
        
        return None
    
    def _calculate_confidence(self, store_name: str, items: List[Dict], total: float) -> float:
        """Calculate parsing confidence score"""
        confidence = 0.0
        
        # Store name found
        if store_name:
            confidence += 0.2
        
        # Items found
        if items:
            confidence += 0.4
            # Bonus for multiple items
            confidence += min(0.2, len(items) * 0.05)
        
        # Total found
        if total is not None:
            confidence += 0.2
            
            # Check if total matches sum of items
            if items:
                items_sum = sum(item.get("total", 0) for item in items)
                if abs(total - items_sum) < 0.1:  # Allow small rounding differences
                    confidence += 0.2
        
        return min(1.0, confidence)