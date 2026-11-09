"""
Automated Unit and Integration Test Suite for Indian Tech Market.
Verifies Indian LPA/INR salary extraction, SDE seniority mapping, SQLite schema, and ML prediction.
"""

import pytest
import sqlite3
import numpy as np
import pandas as pd
from pathlib import Path

from src.nlp.taxonomy import ALL_CANONICAL_SKILLS, SKILL_TAXONOMY, INDIAN_TECH_HUBS
from src.nlp.salary_extractor import SalaryExtractor
from src.nlp.parser import JobTextParser
from src.database.db_manager import DatabaseManager
from src.models.feature_engineering import FeatureTransformer
from src.models.predictor import SalaryPredictor

def test_indian_salary_extractor():
    extractor = SalaryExtractor()

    # Range test with LPA
    res1 = extractor.extract_salary("Competitive CTC: ₹15 - ₹25 LPA plus performance bonus")
    assert res1 is not None
    assert res1[0] == 15.0
    assert res1[1] == 25.0
    assert res1[2] == 20.0

    # Range with Lakhs / Lacs
    res2 = extractor.extract_salary("Salary range: 18 to 28 Lakhs per annum")
    assert res2 is not None
    assert res2[0] == 18.0
    assert res2[1] == 28.0

    # Full INR range (₹12,00,000 - ₹20,00,000)
    res3 = extractor.extract_salary("Compensation: ₹12,00,000 - ₹20,00,000 INR")
    assert res3 is not None
    assert res3[0] == 12.0
    assert res3[1] == 20.0

    # Single LPA
    res4 = extractor.extract_salary("Fixed CTC: 30 LPA")
    assert res4 is not None
    assert res4[2] == 30.0

def test_nlp_parser_indian_tech_hubs():
    parser = JobTextParser()
    assert parser.normalize_region("Koramangala, Bangalore, Karnataka") == "Bengaluru (Bangalore)"
    assert parser.normalize_region("Hitec City, Hyderabad") == "Hyderabad"
    assert parser.normalize_region("Cyber City, Gurugram, Delhi NCR") == "Delhi NCR (Gurgaon / Noida)"
    assert parser.normalize_region("Hinjewadi, Pune") == "Pune"
    assert parser.normalize_region("BKC, Mumbai") == "Mumbai"
    assert parser.normalize_region("OMR, Chennai") == "Chennai"
    assert parser.normalize_region("Pan-India Remote", remote=True) == "Remote (India)"

def test_nlp_parser_sde_seniority_extraction():
    parser = JobTextParser()
    res1 = parser.extract_experience("Hands on coding", title="SDE-1 (Backend Engineer)")
    assert res1["experience_tier"] == "Entry-Level (0-2 yrs)"

    res2 = parser.extract_experience("Microservices experience", title="SDE-2 Full Stack Developer")
    assert res2["experience_tier"] == "Mid-Level (3-5 yrs)"

    res3 = parser.extract_experience("System design and scaling", title="SDE-3 / Senior Software Engineer")
    assert res3["experience_tier"] == "Senior (6-8 yrs)"

    res4 = parser.extract_experience("Looking for 8-12 years of hands-on experience", title="Tech Lead / Staff Engineer")
    assert res4["experience_tier"] == "Lead / Staff (9-12 yrs)"

def test_database_manager_indian_market(tmp_path):
    db_file = tmp_path / "test_india_market.db"
    db = DatabaseManager(db_path=db_file)
    
    # Check skills seeded
    with db.get_connection() as conn:
        count = conn.execute("SELECT COUNT(*) FROM skills;").fetchone()[0]
        assert count > 50

    # Insert test Indian tech job
    job_id = db.save_parsed_job({
        "source_id": "ind-test-101",
        "title": "SDE-3 Machine Learning Engineer",
        "company": "Razorpay",
        "job_family": "Machine Learning & AI",
        "experience_tier": "Senior (6-8 yrs)",
        "years_min": 6,
        "years_max": 8,
        "salary_min_lpa": 38.0,
        "salary_max_lpa": 55.0,
        "salary_avg_lpa": 46.5,
        "salary_min_inr": 3800000.0,
        "salary_max_inr": 5500000.0,
        "salary_avg_inr": 4650000.0,
        "is_remote": False,
        "region": "Bengaluru (Bangalore)",
        "location_raw": "Koramangala, Bengaluru",
        "skill_count": 3,
        "clean_description": "Building fraud detection AI models.",
        "posted_at": "2026-03-01T00:00:00Z",
        "skills": ["Python", "PyTorch", "Kubernetes"]
    })
    assert job_id is not None

    df = db.get_all_cleaned_jobs_df()
    assert len(df) == 1
    assert df.iloc[0]["title"] == "SDE-3 Machine Learning Engineer"
    assert df.iloc[0]["salary_avg_lpa"] == 46.5
    assert "Python" in df.iloc[0]["skills"]
