"""
Date and Time Extractor
=======================
Extracts date and time information from Croatian and Bosnian receipts.
"""

import re
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)


class DateExtractor:
    """Extracts date and time from receipt text"""
    
    def extract_date_time_simple(self, lines: list[str]) -> Tuple[Optional[str], Optional[str]]:
        """Extract date and time from receipt lines"""
        date = None
        time = None
        
        for line in lines:
            line_lower = line.lower()
            
            # Look for date pattern
            date_match = re.search(r'datum[:\s]*(\d{1,2})[.,/](\d{1,2})[.,/](\d{4})', line_lower)
            if date_match:
                day, month, year = date_match.groups()
                try:
                    date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                except ValueError:
                    pass
            
            # Alternative date patterns
            if not date:
                date_match = re.search(r'(\d{1,2})[.,/](\d{1,2})[.,/](\d{4})', line)
                if date_match:
                    day, month, year = date_match.groups()
                    try:
                        if int(day) <= 31 and int(month) <= 12:
                            date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                    except ValueError:
                        pass
            
            # Look for time pattern  
            time_match = re.search(r'vrijeme[:\s]*(\d{1,2}):(\d{2})', line_lower)
            if time_match:
                hour, minute = time_match.groups()
                time = f"{hour.zfill(2)}:{minute}"
            
            # Alternative time pattern
            if not time:
                time_match = re.search(r'(\d{1,2}):(\d{2})', line)
                if time_match:
                    hour, minute = time_match.groups()
                    if int(hour) < 24 and int(minute) < 60:
                        time = f"{hour.zfill(2)}:{minute}"
        
        return date, time

    def extract_date_time_explicit(self, lines: list[str], debug: bool = False) -> Tuple[Optional[str], Optional[str]]:
        """
        EXPLICIT date/time extraction with location-based rules.

        Date and time typically appear:
        - Near "FISKALNI RACUN" line (around lines 4-7)
        - In the header section (lines 5-12)
        - Often on the same line or adjacent lines

        Common formats:
        - Combined: "01.12.2025.19:36" or "01.12.2025. 19:36"
        - Separate: "01.12.2025" and "19:36" on adjacent lines
        - With labels: "Datum: 01.12.2025" "Vrijeme: 19:36"

        Args:
            lines: All receipt lines
            debug: Enable debug logging

        Returns:
            Tuple of (date_str, time_str):
                - date_str: "2025-12-01" (ISO format) or None
                - time_str: "19:36" or None
        """
        # Search in header section where date/time usually appears (lines 4-12)
        # Start at line 4 to skip store name and address
        search_start = 4
        search_end = min(12, len(lines))
        search_lines = lines[search_start:search_end] if len(lines) > search_start else lines

        if debug:
            logger.debug(f"[EXPLICIT DATE/TIME] Searching in lines {search_start}-{search_end-1} ({len(search_lines)} lines)")

        date_str = None
        time_str = None

        for i, line in enumerate(search_lines, start=search_start):
            if debug:
                logger.debug(f"[EXPLICIT DATE/TIME] Checking line {i}: '{line}'")

            # Pattern 1: Combined date and time on same line
            # Format: "01.12.2025.19:36" or "01.12.2025. 19:36"
            # Also handles OCR errors: "61.12.2825.19:33" (0→6, 0→8)
            combined_match = re.search(r'(\d{1,2})\.(\d{1,2})\.(\d{4})[.\s]*(\d{1,2}):(\d{2})', line)
            if combined_match and not date_str:
                day, month, year, hour, minute = combined_match.groups()

                # OCR error correction: Fix common digit misreads in dates
                # Thermal receipts often have 0→6, 0→8, 5→9 misreads
                day_corrected = day
                year_corrected = year

                # If day starts with 6 and is > 31, try correcting to 0
                if day.startswith('6') and int(day) > 31:
                    day_corrected = '0' + day[1:]

                # If year starts with 28 or 26, likely should be 20 (2025 → 2825/2625)
                if year.startswith('28') or year.startswith('26'):
                    year_corrected = '20' + year[2:]

                try:
                    if int(day_corrected) <= 31 and int(month) <= 12 and int(hour) < 24 and int(minute) < 60:
                        date_str = f"{year_corrected}-{month.zfill(2)}-{day_corrected.zfill(2)}"
                        time_str = f"{hour.zfill(2)}:{minute}"
                        if debug:
                            if day != day_corrected or year != year_corrected:
                                logger.debug(f"[EXPLICIT DATE/TIME] OCR error corrected: {day}.{month}.{year} → {day_corrected}.{month}.{year_corrected}")
                            logger.debug(f"[EXPLICIT DATE/TIME] Found combined on line {i}: date={date_str}, time={time_str}")
                        break  # Found both, can stop searching
                except ValueError:
                    pass

            # Pattern 2: Date only (if not found in combined format)
            if not date_str:
                # With label: "Datum: 01.12.2025"
                date_match = re.search(r'datum[:\s]*(\d{1,2})[.,](\d{1,2})[.,](\d{4})', line, re.IGNORECASE)
                if not date_match:
                    # Without label: just "01.12.2025"
                    date_match = re.search(r'\b(\d{1,2})[.,](\d{1,2})[.,](\d{4})\b', line)

                if date_match:
                    day, month, year = date_match.groups()
                    try:
                        if int(day) <= 31 and int(month) <= 12:
                            date_str = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                            if debug:
                                logger.debug(f"[EXPLICIT DATE/TIME] Found date on line {i}: {date_str}")
                    except ValueError:
                        pass

            # Pattern 3: Time only (if not found in combined format)
            if not time_str:
                # With label: "Vrijeme: 19:36"
                time_match = re.search(r'vrijeme[:\s]*(\d{1,2}):(\d{2})', line, re.IGNORECASE)
                if not time_match:
                    # Without label: just "19:36" (but verify it's a valid time)
                    time_match = re.search(r'\b(\d{1,2}):(\d{2})\b', line)

                if time_match:
                    hour, minute = time_match.groups()
                    try:
                        if int(hour) < 24 and int(minute) < 60:
                            time_str = f"{hour.zfill(2)}:{minute}"
                            if debug:
                                logger.debug(f"[EXPLICIT DATE/TIME] Found time on line {i}: {time_str}")
                    except ValueError:
                        pass

            # If we found both, no need to continue
            if date_str and time_str:
                break

        if debug:
            if date_str or time_str:
                logger.debug(f"[EXPLICIT DATE/TIME] Extraction complete - date: {date_str}, time: {time_str}")
            else:
                logger.debug("[EXPLICIT DATE/TIME] No date/time found in search range")

        return date_str, time_str