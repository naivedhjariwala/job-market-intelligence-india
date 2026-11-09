"""
NLP Text Processing Pipeline.
Cleans unstructured job descriptions, extracts technical skills, detects experience tiers,
classifies job families, and standardizes metadata.
"""

import html
import re
from typing import Dict, List, Optional, Any, Set
from .taxonomy import (
    COMPILED_PATTERNS,
    SKILL_TO_CATEGORY,
    JOB_FAMILIES,
    EXPERIENCE_TIERS
)
from .salary_extractor import SalaryExtractor

class JobTextParser:
    """Full NLP routine to parse technical job listings into structured intelligence records."""

    def __init__(self):
        self.salary_extractor = SalaryExtractor()

        # HTML cleaner
        self.html_tag_re = re.compile(r"<[^>]+>")
        self.whitespace_re = re.compile(r"\s+")

        # Experience pattern regexes
        self.exp_patterns = [
            # "3-5 years of experience", "3 to 5 years"
            re.compile(r"(?P<min>\d{1,2})\s*(?:-|–|—|to)\s*(?P<max>\d{1,2})\s*\+?\s*(?:years?|yrs?)(?:\s+of\s+experience)?", re.IGNORECASE),
            # "5+ years of experience", "at least 3 years"
            re.compile(r"(?:at\s+least|minimum|min|over)?\s*(?P<min>\d{1,2})\s*\+?\s*(?:years?|yrs?)(?:\s+of\s+(?:relevant|hands-on|professional|software|technical)?\s*experience)?", re.IGNORECASE)
        ]

        # Seniority titles (including Indian tech ladder: SDE-1, SDE-2, SDE-3, MTS, Tech Lead)
        self.seniority_mapping = {
            "intern": ("Entry-Level (0-2 yrs)", 0),
            "junior": ("Entry-Level (0-2 yrs)", 1),
            "entry": ("Entry-Level (0-2 yrs)", 1),
            "sde 1": ("Entry-Level (0-2 yrs)", 1),
            "sde-1": ("Entry-Level (0-2 yrs)", 1),
            "sde i": ("Entry-Level (0-2 yrs)", 1),
            "associate": ("Entry-Level (0-2 yrs)", 2),
            "graduate": ("Entry-Level (0-2 yrs)", 1),
            "mid": ("Mid-Level (3-5 yrs)", 4),
            "sde 2": ("Mid-Level (3-5 yrs)", 4),
            "sde-2": ("Mid-Level (3-5 yrs)", 4),
            "sde ii": ("Mid-Level (3-5 yrs)", 4),
            "senior": ("Senior (6-8 yrs)", 6),
            "sr": ("Senior (6-8 yrs)", 6),
            "sde 3": ("Senior (6-8 yrs)", 7),
            "sde-3": ("Senior (6-8 yrs)", 7),
            "sde iii": ("Senior (6-8 yrs)", 7),
            "sse": ("Senior (6-8 yrs)", 6),
            "lead": ("Lead / Staff (9-12 yrs)", 9),
            "tech lead": ("Lead / Staff (9-12 yrs)", 9),
            "engineering manager": ("Lead / Staff (9-12 yrs)", 10),
            "em": ("Lead / Staff (9-12 yrs)", 10),
            "staff": ("Lead / Staff (9-12 yrs)", 10),
            "principal": ("Principal / Director (12+ yrs)", 13),
            "director": ("Principal / Director (12+ yrs)", 14),
            "head": ("Principal / Director (12+ yrs)", 12),
            "vp": ("Principal / Director (12+ yrs)", 15),
            "chief": ("Principal / Director (12+ yrs)", 16),
            "architect": ("Lead / Staff (9-12 yrs)", 10)
        }

    def clean_text(self, raw_html: str) -> str:
        """Strips HTML tags, resolves entities, and standardizes spacing."""
        if not raw_html:
            return ""
        # Unescape HTML entities (&amp;, &lt;, &nbsp;)
        text = html.unescape(raw_html)
        # Remove tags
        text = self.html_tag_re.sub(" ", text)
        # Normalize whitespace
        text = self.whitespace_re.sub(" ", text).strip()
        return text

    def extract_experience(self, text: str, title: str = "") -> Dict[str, Any]:
        """Extracts numerical years of experience and maps to canonical experience tier."""
        years_min = None
        years_max = None

        combined_text = f"{title}. {text}"
        for pat in self.exp_patterns:
            matches = list(pat.finditer(combined_text))
            for m in matches:
                gd = m.groupdict()
                try:
                    val_min = int(gd.get("min", 0))
                    # Avoid matching unrealistic numbers (e.g. 2024 years, 50 years)
                    if 0 <= val_min <= 25:
                        val_max = int(gd.get("max")) if gd.get("max") else val_min
                        if years_min is None or val_min < years_min:
                            years_min = val_min
                            years_max = val_max
                except (ValueError, TypeError):
                    continue
            if years_min is not None:
                break

        # Fallback to title keywords if explicit years aren't stated
        if years_min is None:
            lower_title = title.lower()
            for key, (tier_name, default_yrs) in self.seniority_mapping.items():
                if re.search(rf"\b{key}\b", lower_title):
                    years_min = default_yrs
                    years_max = default_yrs
                    return {
                        "years_min": years_min,
                        "years_max": years_max,
                        "experience_tier": tier_name
                    }
            # Default to Mid-Level if unspecified
            years_min = 3
            years_max = 5

        # Map years to tier
        avg_yrs = (years_min + (years_max or years_min)) / 2.0
        if avg_yrs <= 2:
            tier = "Entry-Level (0-2 yrs)"
        elif avg_yrs <= 5:
            tier = "Mid-Level (3-5 yrs)"
        elif avg_yrs <= 8:
            tier = "Senior (6-8 yrs)"
        elif avg_yrs <= 12:
            tier = "Lead / Staff (9-12 yrs)"
        else:
            tier = "Principal / Director (12+ yrs)"

        return {
            "years_min": years_min,
            "years_max": years_max,
            "experience_tier": tier
        }

    def classify_job_family(self, title: str, text: str = "") -> str:
        """Classifies role into one of the canonical job families."""
        blob = f"{title} {text}".lower()

        # Rule-based priority matching
        if re.search(r"\b(ai engineer|machine learning|ml engineer|deep learning|data scientist|nlp|computer vision|llm)\b", blob):
            return "Machine Learning & AI"
        elif re.search(r"\b(data engineer|big data|analytics engineer|etl|data platform|data warehouse)\b", blob):
            return "Data Engineering & Warehousing"
        elif re.search(r"\b(devops|cloud engineer|sre|site reliability|infrastructure engineer|platform engineer)\b", blob):
            return "DevOps, Cloud & SRE"
        elif re.search(r"\b(ios|android|mobile engineer|mobile developer|react native|flutter|swift|kotlin)\b", blob):
            return "Mobile Engineering"
        elif re.search(r"\b(security engineer|cybersecurity|infosec|qa engineer|quality assurance|sdet|test engineer)\b", blob):
            return "Security & QA Engineering"
        elif re.search(r"\b(vp of engineering|director of engineering|head of engineering|chief architect|staff architect)\b", blob):
            return "Engineering Leadership & Architecture"
        elif re.search(r"\b(full\s*stack|fullstack)\b", blob):
            return "Full Stack Engineering"
        elif re.search(r"\b(frontend|front[- ]end|web developer|ui/ux engineer|react developer|vue developer)\b", blob):
            return "Frontend & Web Engineering"
        elif re.search(r"\b(backend|back[- ]end|golang developer|python developer|java developer|systems engineer)\b", blob):
            return "Backend & Distributed Systems"

        # Default fallback
        if "data" in blob:
            return "Data Engineering & Warehousing"
        elif "cloud" in blob or "infra" in blob:
            return "DevOps, Cloud & SRE"
        return "Backend & Distributed Systems"

    def extract_skills(self, text: str) -> Dict[str, Any]:
        """
        Scans text against compiled technical skill taxonomy.
        Returns list of matched canonical skills and taxonomy counts by category.
        """
        matched_skills: Set[str] = set()
        skills_by_category: Dict[str, List[str]] = {}

        for category, skill_dict in COMPILED_PATTERNS.items():
            category_matches = []
            for skill_name, pattern_list in skill_dict.items():
                for pat in pattern_list:
                    if pat.search(text):
                        matched_skills.add(skill_name)
                        category_matches.append(skill_name)
                        break
            if category_matches:
                skills_by_category[category] = category_matches

        return {
            "skills": sorted(list(matched_skills)),
            "skills_by_category": skills_by_category,
            "skill_count": len(matched_skills)
        }

    def normalize_region(self, location: str, remote: bool = False) -> str:
        """Maps freeform location text into normalized Indian tech hubs."""
        loc = (location or "").lower()
        if any(w in loc for w in ["bangalore", "bengaluru", "karnataka", "whitefield", "koramangala", "electronic city", "bellandur", "indiranagar"]):
            return "Bengaluru (Bangalore)"
        elif any(w in loc for w in ["hyderabad", "telangana", "hitec city", "gachibowli", "secunderabad", "cyberabad"]):
            return "Hyderabad"
        elif any(w in loc for w in ["gurgaon", "gurugram", "noida", "delhi", "ncr", "cyber city", "greater noida"]):
            return "Delhi NCR (Gurgaon / Noida)"
        elif any(w in loc for w in ["pune", "maharashtra", "hinjewadi", "magarpatta", "kharadi", "viman nagar"]):
            return "Pune"
        elif any(w in loc for w in ["mumbai", "bkc", "bandra", "navi mumbai", "powai", "andheri"]):
            return "Mumbai"
        elif any(w in loc for w in ["chennai", "tamil nadu", "omr", "taramani", "guindy"]):
            return "Chennai"
        elif remote or any(w in loc for w in ["remote", "pan india", "anywhere in india", "work from home", "wfh"]):
            return "Remote (India)"
        return "Bengaluru (Bangalore)"  # Benchmark tech capital of India

    def parse_job_record(self, raw_job: Dict[str, Any]) -> Dict[str, Any]:
        """Processes raw job dictionary and outputs cleaned, standardized Indian market record."""
        title = raw_job.get("title", "") or ""
        company = raw_job.get("company_name", "") or raw_job.get("company", "") or "Indian Tech Enterprise"
        raw_desc = raw_job.get("description", "") or ""
        location = raw_job.get("location", "") or ""
        is_remote = bool(raw_job.get("remote", False) or "remote" in location.lower() or "remote" in title.lower() or "wfh" in location.lower())
        
        # 1. Clean HTML & normalize text
        clean_desc = self.clean_text(raw_desc)
        combined_text = f"{title}. {clean_desc}"

        # 2. Extract technical skills
        skill_res = self.extract_skills(combined_text)

        # 3. Extract experience requirements
        exp_res = self.extract_experience(clean_desc, title)

        # 4. Classify job family
        job_family = self.classify_job_family(title, clean_desc)

        # 5. Extract Indian compensation scales (in LPA)
        salary_text = raw_job.get("salary", "") or ""
        salary_res = self.salary_extractor.extract_salary(salary_text)
        if not salary_res:
            salary_res = self.salary_extractor.extract_salary(clean_desc)

        salary_min_lpa, salary_max_lpa, salary_avg_lpa = salary_res if salary_res else (None, None, None)

        # Compute full INR values
        salary_min_inr = round(salary_min_lpa * 100000.0, 2) if salary_min_lpa is not None else None
        salary_max_inr = round(salary_max_lpa * 100000.0, 2) if salary_max_lpa is not None else None
        salary_avg_inr = round(salary_avg_lpa * 100000.0, 2) if salary_avg_lpa is not None else None

        # 6. Normalize Indian tech hub region
        region = self.normalize_region(location, is_remote)

        return {
            "source_id": str(raw_job.get("id", "") or raw_job.get("slug", "")),
            "title": title.strip(),
            "company": company.strip(),
            "job_family": job_family,
            "experience_tier": exp_res["experience_tier"],
            "years_min": exp_res["years_min"],
            "years_max": exp_res["years_max"],
            "skills": skill_res["skills"],
            "skills_by_category": skill_res["skills_by_category"],
            "skill_count": skill_res["skill_count"],
            "salary_min_lpa": salary_min_lpa,
            "salary_max_lpa": salary_max_lpa,
            "salary_avg_lpa": salary_avg_lpa,
            "salary_min_inr": salary_min_inr,
            "salary_max_inr": salary_max_inr,
            "salary_avg_inr": salary_avg_inr,
            # Aliases for compatibility
            "salary_min_usd": salary_min_lpa,
            "salary_max_usd": salary_max_lpa,
            "salary_avg_usd": salary_avg_lpa,
            "is_remote": is_remote,
            "region": region,
            "location_raw": location,
            "clean_description": clean_desc[:2000],
            "posted_at": raw_job.get("created_at") or raw_job.get("publication_date") or "2026-03-01T00:00:00Z",
            "url": raw_job.get("url", "")
        }

