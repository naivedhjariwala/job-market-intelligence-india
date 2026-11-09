"""
Indian Market Salary Extractor and Normalizer (2025-2026).
Parses unstructured salary text, Indian Lakhs Per Annum (LPA), CTC formats,
and multi-currency expressions into standardized LPA and INR.
"""

import re
from typing import Optional, Tuple, Dict, Any

# Current USD to INR conversion baseline (1 USD ≈ 86.0 INR)
USD_TO_INR = 86.0

class SalaryExtractor:
    """Extracts, parses, and standardizes Indian tech compensation (LPA & INR)."""

    def __init__(self):
        # 1. LPA / Lakhs pattern: e.g. "₹12 - ₹18 LPA", "15 to 22 Lakhs", "8-14 lac", "25 LPA CTC"
        self.lpa_range_pattern = re.compile(
            r"(?:₹|rs\.?|inr)?\s*"
            r"(?P<min>\d+(?:\.\d+)?)\s*"
            r"(?:-|–|—|to)\s*"
            r"(?:₹|rs\.?|inr)?\s*"
            r"(?P<max>\d+(?:\.\d+)?)\s*"
            r"(?:lpa|lakhs?|lacs?|lac|l\b)",
            re.IGNORECASE
        )

        self.lpa_single_pattern = re.compile(
            r"(?:₹|rs\.?|inr)?\s*"
            r"(?P<val>\d+(?:\.\d+)?)\s*"
            r"(?:lpa|lakhs?|lacs?|lac)\b",
            re.IGNORECASE
        )

        # 2. Full INR pattern: e.g. "₹8,00,000 - ₹15,00,000" or "1200000 - 1800000"
        self.inr_full_pattern = re.compile(
            r"(?:₹|rs\.?|inr)?\s*"
            r"(?P<min>\d{1,2}(?:[,\.]\d{2})*(?:[,\.]\d{3})|\d{6,8})\s*"
            r"(?:-|–|—|to)\s*"
            r"(?:₹|rs\.?|inr)?\s*"
            r"(?P<max>\d{1,2}(?:[,\.]\d{2})*(?:[,\.]\d{3})|\d{6,8})",
            re.IGNORECASE
        )

        # 3. Global USD pattern (for global remote tech roles paying in USD to Indian developers)
        self.usd_range_pattern = re.compile(
            r"(?:\$|USD)\s*"
            r"(?P<min>\d{1,3}(?:,\d{3})*|\d+)\s*(?P<kmin>[kK])?\s*"
            r"(?:-|–|—|to)\s*"
            r"(?:\$|USD)?\s*"
            r"(?P<max>\d{1,3}(?:,\d{3})*|\d+)\s*(?P<kmax>[kK])?",
            re.IGNORECASE
        )

    def extract_salary(self, text: str) -> Optional[Tuple[float, float, float]]:
        """
        Parses salary text and returns (min_lpa, max_lpa, avg_lpa) in Lakhs Per Annum.
        1 LPA = ₹1,00,000 INR.
        Returns None if no realistic salary is found.
        """
        if not text:
            return None

        # 1. Match Indian LPA Range (e.g. 15 - 25 LPA)
        match_lpa = self.lpa_range_pattern.search(text)
        if match_lpa:
            try:
                min_v = float(match_lpa.group("min"))
                max_v = float(match_lpa.group("max"))
                if min_v > max_v:
                    min_v, max_v = max_v, min_v
                # Validate reasonable Indian tech bracket: 3 LPA to 160 LPA
                if 2.5 <= min_v <= 160.0 and 2.5 <= max_v <= 160.0:
                    avg_v = (min_v + max_v) / 2.0
                    return (round(min_v, 2), round(max_v, 2), round(avg_v, 2))
            except (ValueError, TypeError):
                pass

        # 2. Match Single LPA (e.g. 24 LPA)
        single_lpa = self.lpa_single_pattern.search(text)
        if single_lpa:
            try:
                val = float(single_lpa.group("val"))
                if 2.5 <= val <= 160.0:
                    min_v = round(val * 0.88, 2)
                    max_v = round(val * 1.12, 2)
                    return (min_v, max_v, round(val, 2))
            except (ValueError, TypeError):
                pass

        # 3. Match Full INR numerical range (e.g. ₹10,00,000 - ₹18,00,000)
        inr_match = self.inr_full_pattern.search(text)
        if inr_match:
            try:
                clean_min = inr_match.group("min").replace(",", "").replace(".", "").replace(" ", "")
                clean_max = inr_match.group("max").replace(",", "").replace(".", "").replace(" ", "")
                raw_min = float(clean_min)
                raw_max = float(clean_max)
                if raw_min > raw_max:
                    raw_min, raw_max = raw_max, raw_min
                # Convert INR to LPA (divide by 100,000)
                lpa_min = raw_min / 100000.0
                lpa_max = raw_max / 100000.0
                if 2.5 <= lpa_min <= 160.0 and 2.5 <= lpa_max <= 160.0:
                    lpa_avg = (lpa_min + lpa_max) / 2.0
                    return (round(lpa_min, 2), round(lpa_max, 2), round(lpa_avg, 2))
            except (ValueError, TypeError):
                pass

        # 4. Match USD range and convert to INR LPA (e.g. $60k - $90k -> converted to INR LPA)
        usd_match = self.usd_range_pattern.search(text)
        if usd_match:
            try:
                min_str = usd_match.group("min").replace(",", "")
                max_str = usd_match.group("max").replace(",", "")
                u_min = float(min_str) * (1000 if usd_match.group("kmin") or float(min_str) < 1000 else 1)
                u_max = float(max_str) * (1000 if usd_match.group("kmax") or float(max_str) < 1000 else 1)
                if u_min > u_max:
                    u_min, u_max = u_max, u_min
                # Convert USD to INR LPA: (USD * 86) / 100,000
                lpa_min = (u_min * USD_TO_INR) / 100000.0
                lpa_max = (u_max * USD_TO_INR) / 100000.0
                if 3.0 <= lpa_min <= 180.0 and 3.0 <= lpa_max <= 180.0:
                    lpa_avg = (lpa_min + lpa_max) / 2.0
                    return (round(lpa_min, 2), round(lpa_max, 2), round(lpa_avg, 2))
            except (ValueError, TypeError):
                pass

        return None
