"""
Item Extraction Coordinator
===========================
Orchestrates different item extraction strategies for Croatian and Bosnian receipts.
"""

import re
import logging
from typing import List, Dict, Any
from .item_strategies import (
    FallbackItemStrategy,
    SequentialItemStrategy,
    FlexibleItemStrategy,
    MultilineItemStrategy,
    VerticalColumnStrategy
)

logger = logging.getLogger(__name__)


class ItemExtractor:
    """Coordinates multiple item extraction strategies"""

    def __init__(self):
        """Initialize all extraction strategies"""
        self.fallback_strategy = FallbackItemStrategy()
        self.sequential_strategy = SequentialItemStrategy()
        self.flexible_strategy = FlexibleItemStrategy()
        self.multiline_strategy = MultilineItemStrategy()
        self.vertical_strategy = VerticalColumnStrategy()
    
    def extract_items_from_section(self, items_lines: List[str], country: str = "UNKNOWN", debug: bool = False) -> List[Dict[str, Any]]:
        """
        Extract items from pre-identified items section (no section detection needed).
        Use this when section_detector has already isolated the items lines.

        Args:
            items_lines: Lines containing items
            country: "HR" (Croatia), "BA" (Bosnia), or "UNKNOWN"
            debug: Enable debug logging
        """
        if debug:
            logger.debug(f"[ITEM EXTRACTOR] Extracting from {len(items_lines)} item lines (country={country})")

        if not items_lines:
            return []

        # BOSNIAN FORMAT: Try multiline 3-line format FIRST
        if country == "BA":
            if debug:
                logger.debug("[BOSNIAN] Using multiline-first strategy")

            # Try Bosnian 3-line multiline parsing
            multiline_items = []
            i = 0
            while i < len(items_lines):
                item = self.multiline_strategy.parse_multiline_item(items_lines, i, debug=debug)
                if item and item.get('extraction_method') == 'bosnian_3line':
                    multiline_items.append(item)
                    # Use lines_consumed field to know how many lines to skip (3 or 4)
                    lines_to_skip = item.get('lines_consumed', 3)
                    i += lines_to_skip
                    if debug:
                        logger.debug(f"[BOSNIAN 3-LINE] Found item: {item['name']} (qty={item['quantity']}, total={item['total']}, skipped {lines_to_skip} lines)")
                else:
                    i += 1

            if multiline_items:
                if debug:
                    logger.debug(f"[BOSNIAN MULTILINE] Found {len(multiline_items)} items")
                return multiline_items

            # Fallback to flexible if Bosnian format didn't work
            if debug:
                logger.debug("[BOSNIAN] Falling back to flexible strategy")

        # CROATIAN FORMAT: Try single-line formats FIRST
        if country == "HR" or country == "UNKNOWN":
            if debug and country == "HR":
                logger.debug("[CROATIAN] Using single-line-first strategy")

            # Try vertical column strategy first (handles Kol/Iznos/Cijena/Naziv vertical format)
            vertical_items = self.vertical_strategy.extract_items_vertical(items_lines, debug=debug)
            if vertical_items:
                if debug:
                    logger.debug(f"[VERTICAL] Found {len(vertical_items)} items")
                return vertical_items

            # Try flexible line-by-line parsing (most reliable for standard horizontal formats)
            flexible_items = []
            for line in items_lines:
                item = self.flexible_strategy.parse_item_line_flexible(line, debug=debug)
                if item:
                    flexible_items.append(item)

            if flexible_items:
                if debug:
                    logger.debug(f"[FLEXIBLE] Found {len(flexible_items)} items")
                return flexible_items

            # Try sequential parsing as fallback
            items = self.sequential_strategy.extract_items(items_lines, 0, len(items_lines), debug=debug)
            if items:
                if debug:
                    logger.debug(f"[SEQUENTIAL] Found {len(items)} items")
                return items

        # Universal fallback: Try multiline parsing (works for both formats)
        if country != "BA":  # Only if we haven't already tried this for Bosnian
            multiline_items = []
            for i in range(len(items_lines) - 2):
                item = self.multiline_strategy.parse_multiline_item(items_lines, i, debug=debug)
                if item:
                    multiline_items.append(item)

            if multiline_items:
                if debug:
                    logger.debug(f"[MULTILINE] Found {len(multiline_items)} items")
                return multiline_items

        # Final fallback
        fallback_items = self.fallback_strategy.extract_items(items_lines, debug=debug)
        if debug:
            logger.debug(f"[FALLBACK] Found {len(fallback_items)} items")

        return fallback_items

    def extract_items(self, lines: List[str], debug: bool = False) -> List[Dict[str, Any]]:
        """Extract items using multiple strategies with fallback"""
        if debug:
            logger.debug("[ITEM EXTRACTOR] Starting item extraction")

        # First, try to identify items section
        items_start, items_end = self.find_items_section_flexible(lines, debug=debug)
        
        if items_start >= 0 and items_end > items_start:
            # Try sequential parsing first (most common for Croatian receipts)
            items = self.sequential_strategy.extract_items(lines, items_start, items_end, debug=debug)
            if items:
                if debug:
                    logger.debug(f"[SEQUENTIAL] Found {len(items)} items")
                return items
            
            # Try multiline parsing
            items_section = lines[items_start:items_end]
            multiline_items = []
            for i in range(len(items_section) - 2):
                item = self.multiline_strategy.parse_multiline_item(items_section, i, debug=debug)
                if item:
                    multiline_items.append(item)
            
            if multiline_items:
                if debug:
                    logger.debug(f"[MULTILINE] Found {len(multiline_items)} items")
                return multiline_items
        
        # Try flexible line-by-line parsing
        flexible_items = []
        for line in lines:
            item = self.flexible_strategy.parse_item_line_flexible(line, debug=debug)
            if item:
                flexible_items.append(item)
        
        if flexible_items:
            if debug:
                logger.debug(f"[FLEXIBLE] Found {len(flexible_items)} items")
            return flexible_items
        
        # Final fallback strategy
        fallback_items = self.fallback_strategy.extract_items(lines, debug=debug)
        if debug:
            logger.debug(f"[FALLBACK] Found {len(fallback_items)} items")
        
        return fallback_items
    
    def find_items_section_flexible(self, lines: List[str], debug: bool = False) -> tuple:
        """Find the section of the receipt that contains item listings"""
        if not lines:
            return -1, -1
        
        # Look for start indicators (Croatian)
        start_indicators = [
            'stavke', 'stavka', 'proizvodi', 'artikli', 'artikal',
            'item', 'items', '---', '==='
        ]
        
        # Look for end indicators (Croatian)
        end_indicators = [
            'ukupno', 'total', 'suma', 'sveukupno', 'iznos',
            'povrat', 'gotovina', 'kartica', 'promjena', 'kusur'
        ]
        
        start_idx = -1
        end_idx = len(lines)
        
        # Find start
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            if any(indicator in line_lower for indicator in start_indicators):
                start_idx = i + 1
                break
            
            # Alternative: look for first line that looks like an item
            if start_idx == -1 and self.flexible_strategy.looks_like_item_line(line):
                # Check if this could be the start of items section
                # by looking for more item-like lines nearby
                item_count = 0
                for j in range(i, min(i + 5, len(lines))):
                    if self.flexible_strategy.looks_like_item_line(lines[j]):
                        item_count += 1
                
                if item_count >= 2:  # At least 2 item-like lines
                    start_idx = i
                    break
        
        # Find end
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            if any(indicator in line_lower for indicator in end_indicators):
                end_idx = i
                break
        
        # If no explicit start found, assume items start after header (around line 3-5)
        if start_idx == -1:
            start_idx = min(3, len(lines) // 4)
        
        # If end is too close to start, extend it
        if end_idx - start_idx < 3:
            end_idx = min(start_idx + 10, len(lines))
        
        if debug:
            logger.debug(f"[SECTION] Items section: lines {start_idx} to {end_idx}")
            if start_idx >= 0 and end_idx > start_idx:
                logger.debug(f"[SECTION] Content preview: {lines[start_idx:start_idx+3]}")

        return start_idx, end_idx

    def extract_items_with_boundaries(self, lines: List[str], debug: bool = False) -> List[Dict[str, Any]]:
        """
        EXPLICIT item extraction with boundary markers.

        Items appear between specific markers:
        - START: After "FISKALNI RACUN" line (or similar fiscal marker)
        - END: Before "TOTAL:" line (or UKUPNO/SUMA)

        This method:
        1. Finds the START and END boundaries
        2. Extracts lines between them
        3. Filters out tax/payment lines (PDV, PNP, OSN, KARTICA, GOTOVINA, etc.)
        4. Parses remaining lines as items

        Common item format:
        - "PRODUCT NAME QTYx PRICE TOTAL" (e.g., "KUPUS CRVENI H/KG 1,358x 2.85 3,87E")
        - "PRODUCT NAME" on one line, "QTYx PRICE TOTAL" on next line

        Args:
            lines: All receipt lines
            debug: Enable debug logging

        Returns:
            List of items: [{"name": str, "quantity": float, "price_per_item": float, "total": float}, ...]
        """
        if debug:
            logger.debug(f"[BOUNDED ITEMS] Searching for boundaries in {len(lines)} lines")

        # Find START boundary (after FISKALNI)
        start_idx = None
        for i, line in enumerate(lines):
            line_upper = line.upper()
            if 'FISKALNI' in line_upper or 'FISCAL' in line_upper:
                start_idx = i + 1  # Items start AFTER this line
                if debug:
                    logger.debug(f"[BOUNDED ITEMS] Found START marker on line {i}: '{line}'")
                break

        # Find END boundary (before TOTAL/UKUPNO/SUMA)
        end_idx = None
        for i, line in enumerate(lines):
            line_upper = line.upper()
            if any(keyword in line_upper for keyword in ['TOTAL', 'UKUPNO', 'SUMA']) and ':' in line:
                end_idx = i  # Items end BEFORE this line
                if debug:
                    logger.debug(f"[BOUNDED ITEMS] Found END marker on line {i}: '{line}'")
                break

        # Validate boundaries
        if start_idx is None:
            if debug:
                logger.debug("[BOUNDED ITEMS] No START boundary found, using line 5")
            start_idx = 5  # Default fallback

        if end_idx is None:
            if debug:
                logger.debug("[BOUNDED ITEMS] No END boundary found, using end of receipt")
            end_idx = len(lines)

        if start_idx >= end_idx:
            if debug:
                logger.debug(f"[BOUNDED ITEMS] Invalid boundaries: start={start_idx}, end={end_idx}")
            return []

        # Extract lines in bounded section
        bounded_lines = lines[start_idx:end_idx]
        if debug:
            logger.debug(f"[BOUNDED ITEMS] Bounded section: lines {start_idx}-{end_idx-1} ({len(bounded_lines)} lines)")

        # Filter out tax and payment lines
        tax_payment_keywords = [
            'PDV', 'PNP', 'OSN', 'KARTICA', 'GOTOVINA', 'CASH', 'CARD',
            'UPLAČENO', 'POVRAT', 'PROMJENA', 'KUSUR', 'CHANGE',
            'VE:', 'UE:', 'POUE', 'POU:', 'OSNOVICA', 'OSNO'
        ]

        filtered_lines = []
        for i, line in enumerate(bounded_lines):
            line_upper = line.upper()

            # Skip if line contains tax/payment keywords
            is_tax_payment = any(keyword in line_upper for keyword in tax_payment_keywords)
            if is_tax_payment:
                if debug:
                    logger.debug(f"[BOUNDED ITEMS] Skipping tax/payment line {start_idx+i}: '{line}'")
                continue

            # Skip empty lines
            if not line.strip():
                continue

            # Skip lines that are just numbers (likely tax amounts)
            if re.match(r'^\s*[\d.,\s]+\s*$', line):
                if debug:
                    logger.debug(f"[BOUNDED ITEMS] Skipping number-only line {start_idx+i}: '{line}'")
                continue

            filtered_lines.append(line)

        if debug:
            logger.debug(f"[BOUNDED ITEMS] After filtering: {len(filtered_lines)} potential item lines")

        # Parse items using flexible strategy
        items = []
        for i, line in enumerate(filtered_lines):
            item = self.flexible_strategy.parse_item_line_flexible(line, debug=debug)
            if item:
                items.append(item)
                if debug:
                    logger.debug(f"[BOUNDED ITEMS] Parsed item: {item.get('name')}")

        if debug:
            logger.debug(f"[BOUNDED ITEMS] Extraction complete - found {len(items)} items")

        return items