"""
Bosnian-specific OCR text correction.

This module handles post-processing of OCR text from Bosnian receipts,
fixing common OCR errors specific to Bosnian language and receipt formats.
"""

import re
import logging

logger = logging.getLogger(__name__)


class BosnianTextCorrector:
    """
    Handles Bosnian-specific OCR error corrections.

    Separated from Croatian corrections to maintain clean separation
    of concerns and language-specific processing.
    """

    @staticmethod
    def correct_bosnian_ocr_errors(text: str) -> str:
        """
        Correct common OCR errors in Bosnian receipts.

        Bosnian-specific issues:
        1. City names: MOSTAR, SARAJEVO (often misread as M0STAR, šARAJEVO)
        2. Business IDs: PIB, JIB, IBFM (often misread as P1B, J1B, 1BFM)
        3. Compound words: "FISKALNIRACUN" → "FISKALNI RACUN"

        IMPORTANT: Apply MINIMAL corrections. PaddleOCR's Latin dictionary
        handles Bosnian text well. Only fix known OCR mistakes.

        Args:
            text: Raw OCR text from Bosnian receipt

        Returns:
            Corrected text with Bosnian-specific fixes applied
        """
        if not text:
            return text

        corrected_text = text

        # FIX 1: Store name corrections (KONZUM is major chain)
        # Match various OCR errors: KDNZUM, KDNZM, KDNZ, K0NZUM, K0NZM, etc.
        # Don't use word boundary at end - allows matching "KDNZMd.o.o" format
        corrected_text = re.sub(r'\bKDNZ[UM]*', 'KONZUM', corrected_text, flags=re.IGNORECASE)
        corrected_text = re.sub(r'\bK[0O]NZ[UM]*', 'KONZUM', corrected_text, flags=re.IGNORECASE)

        # FIX 2: City name corrections
        corrected_text = re.sub(r'\bM[0O]STAR\b', 'MOSTAR', corrected_text, flags=re.IGNORECASE)
        # SARAJEVO variations: SARAJEUO, SAREUO, šARAJEVO, etc.
        corrected_text = re.sub(r'\bSARAJEUO\b', 'SARAJEVO', corrected_text, flags=re.IGNORECASE)
        corrected_text = re.sub(r'\bSARE[UV]O\b', 'SARAJEVO', corrected_text, flags=re.IGNORECASE)
        corrected_text = re.sub(r'\b[šŠśŚ]ARAJEVO\b', 'SARAJEVO', corrected_text, flags=re.IGNORECASE)

        # FIX 3: Business ID corrections (critical identifiers)
        # Fix JIB with "18" misread as IB
        corrected_text = re.sub(r'\bJ18(\d{13})\b', r'JIB\1', corrected_text)
        corrected_text = re.sub(r'\bP1B\b', 'PIB', corrected_text, flags=re.IGNORECASE)
        corrected_text = re.sub(r'\bJ1B\b', 'JIB', corrected_text, flags=re.IGNORECASE)
        corrected_text = re.sub(r'\b1BFM\b', 'IBFM', corrected_text, flags=re.IGNORECASE)

        # IBFM always starts with BP (not BF) - fix OCR errors
        # Pattern: BF followed by 6-8 digits → BP followed by same digits
        corrected_text = re.sub(r'\bBF(\d{6,8})\b', r'BP\1', corrected_text)

        # FIX 4: Tax field corrections (PDV = Porez na dodatu vrijednost - VAT)
        corrected_text = re.sub(r'\bPDU\b', 'PDV', corrected_text, flags=re.IGNORECASE)

        # FIX 5: Common words
        corrected_text = re.sub(r'\bPOURAT\b', 'POVRAT', corrected_text, flags=re.IGNORECASE)

        # FIX 6: Compound word spacing (fiscal receipt markers)
        corrected_text = re.sub(r'\bFISKALNIRACUN\b', 'FISKALNI RACUN', corrected_text, flags=re.IGNORECASE)
        corrected_text = re.sub(r'\bFISCALRECEIPT\b', 'FISCAL RECEIPT', corrected_text, flags=re.IGNORECASE)

        # FIX 7: Common store names
        corrected_text = re.sub(r'\bB[1I]NGO\b', 'BINGO', corrected_text, flags=re.IGNORECASE)
        corrected_text = re.sub(r'\bBING[0O]\b', 'BINGO', corrected_text, flags=re.IGNORECASE)

        # FIX 8: Fix d.0.0 → d.o.o (company suffix - same as Croatian)
        corrected_text = re.sub(r'\.0(?=\.|\b)', '.o', corrected_text)

        # FIX 9: Add space before d.o.o if missing (e.g., "KONZUMd.o.o" → "KONZUM d.o.o")
        # IMPORTANT: This must run AFTER the d.0.0 → d.o.o fix above
        # Match any word followed immediately by d.o.o (no space)
        corrected_text = re.sub(r'([A-Z]{3,})(d\.o\.o)', r'\1 \2', corrected_text, flags=re.IGNORECASE)

        # FIX 10: Add space after d.o.o. when followed by city name (e.g., "d.o.o.SARAJEVO" → "d.o.o. SARAJEVO")
        corrected_text = re.sub(r'(d\.o\.o\.)([A-Z])', r'\1 \2', corrected_text, flags=re.IGNORECASE)

        return corrected_text

    @staticmethod
    def clean_text(text: str) -> str:
        """
        Minimal text cleaning for Bosnian receipts.

        Unlike Croatian cleaning, this is very minimal - just normalize
        whitespace and remove empty lines.

        Args:
            text: Corrected OCR text

        Returns:
            Cleaned text
        """
        if not text:
            return text

        lines = text.split('\n')
        cleaned_lines = []

        for line in lines:
            line = line.strip()
            if line:
                # Normalize whitespace
                line = re.sub(r'\s+', ' ', line)
                cleaned_lines.append(line)

        return '\n'.join(cleaned_lines)
