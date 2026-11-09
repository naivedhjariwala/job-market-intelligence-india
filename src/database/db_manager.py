"""
SQLite Database Manager for Indian Tech Market Intelligence Platform.
Handles schema initialization, atomic upserts, relational joins, and analytical SQL queries in LPA & INR.
"""

import sqlite3
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
from ..nlp.taxonomy import SKILL_TAXONOMY, SKILL_TO_CATEGORY

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "job_market.db"

class DatabaseManager:
    """Relational SQL operations manager for Indian Tech Market."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = Path(db_path) if db_path else DEFAULT_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.schema_path = Path(__file__).resolve().parent / "schema.sql"
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        """Returns SQLite connection with WAL mode and foreign key constraints enabled."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA journal_mode = WAL;")
        return conn

    def init_db(self):
        """Initializes tables, indices, and baseline taxonomy."""
        with self.get_connection() as conn:
            with open(self.schema_path, "r", encoding="utf-8") as f:
                conn.executescript(f.read())
        self.seed_skills_taxonomy()

    def seed_skills_taxonomy(self):
        """Populates skills table with master taxonomy definitions."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            for skill, category in SKILL_TO_CATEGORY.items():
                cursor.execute(
                    "INSERT OR IGNORE INTO skills (name, category) VALUES (?, ?)",
                    (skill, category)
                )
            conn.commit()

    def save_parsed_job(self, parsed: Dict[str, Any], raw_record: Optional[Dict[str, Any]] = None) -> int:
        """
        Atomically saves raw job, cleaned job (with LPA and INR compensation), and links skills.
        Returns cleaned_job ID.
        """
        lpa_avg = parsed.get("salary_avg_lpa") or parsed.get("salary_avg_usd") or 18.0
        lpa_min = parsed.get("salary_min_lpa") or parsed.get("salary_min_usd") or round(lpa_avg * 0.85, 2)
        lpa_max = parsed.get("salary_max_lpa") or parsed.get("salary_max_usd") or round(lpa_avg * 1.15, 2)

        inr_avg = parsed.get("salary_avg_inr") or (lpa_avg * 100000.0)
        inr_min = parsed.get("salary_min_inr") or (lpa_min * 100000.0)
        inr_max = parsed.get("salary_max_inr") or (lpa_max * 100000.0)

        with self.get_connection() as conn:
            cursor = conn.cursor()

            # 1. Insert Raw Record if provided
            raw_id = None
            if raw_record:
                cursor.execute("""
                    INSERT OR REPLACE INTO raw_jobs 
                    (source_id, source_name, title, company, location, raw_description, raw_salary, url)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    str(raw_record.get("id", "") or parsed["source_id"]),
                    raw_record.get("source", "Realtime Feed"),
                    raw_record.get("title", ""),
                    raw_record.get("company_name", raw_record.get("company", "")),
                    raw_record.get("location", ""),
                    raw_record.get("description", ""),
                    str(raw_record.get("salary", "")),
                    raw_record.get("url", "")
                ))
                raw_id = cursor.lastrowid

            # 2. Insert or Replace Cleaned Job
            cursor.execute("""
                INSERT OR REPLACE INTO cleaned_jobs (
                    raw_job_id, source_id, title, company, job_family,
                    experience_tier, years_min, years_max, 
                    salary_min_lpa, salary_max_lpa, salary_avg_lpa,
                    salary_min_inr, salary_max_inr, salary_avg_inr,
                    salary_min_usd, salary_max_usd, salary_avg_usd,
                    is_remote, region, location_raw, skill_count, clean_description, posted_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                raw_id,
                parsed["source_id"],
                parsed["title"],
                parsed["company"],
                parsed["job_family"],
                parsed["experience_tier"],
                parsed["years_min"],
                parsed["years_max"],
                lpa_min,
                lpa_max,
                lpa_avg,
                inr_min,
                inr_max,
                inr_avg,
                lpa_min,  # usd alias pointing to lpa for model compatibility
                lpa_max,
                lpa_avg,
                1 if parsed["is_remote"] else 0,
                parsed["region"],
                parsed["location_raw"],
                parsed["skill_count"],
                parsed["clean_description"],
                parsed["posted_at"]
            ))
            job_id = cursor.lastrowid

            # 3. Associate Skills
            if parsed.get("skills"):
                for skill_name in parsed["skills"]:
                    cursor.execute("SELECT id FROM skills WHERE name = ?", (skill_name,))
                    row = cursor.fetchone()
                    if row:
                        skill_id = row[0]
                        cursor.execute("""
                            INSERT OR IGNORE INTO job_skills (job_id, skill_id)
                            VALUES (?, ?)
                        """, (job_id, skill_id))

            conn.commit()
            return job_id

    def bulk_save_jobs(self, parsed_jobs: List[Dict[str, Any]], raw_jobs: Optional[List[Dict[str, Any]]] = None) -> int:
        """Batch insert parsed records with transaction efficiency."""
        saved_count = 0
        raw_map = {str(r.get("id", "") or r.get("slug", "")): r for r in (raw_jobs or [])}
        for job in parsed_jobs:
            raw = raw_map.get(job["source_id"])
            try:
                self.save_parsed_job(job, raw)
                saved_count += 1
            except Exception as e:
                continue
        self.refresh_market_aggregates()
        return saved_count

    def refresh_market_aggregates(self):
        """Recalculates aggregated skill statistics in LPA and INR."""
        query = """
            INSERT OR REPLACE INTO skill_market_aggregates 
            (skill_name, category, job_count, avg_salary_lpa, median_salary_lpa, avg_salary_inr, remote_percentage, last_computed)
            SELECT 
                s.name AS skill_name,
                s.category AS category,
                COUNT(j.id) AS job_count,
                ROUND(AVG(j.salary_avg_lpa), 2) AS avg_salary_lpa,
                ROUND(AVG(j.salary_avg_lpa), 2) AS median_salary_lpa,
                ROUND(AVG(j.salary_avg_inr), 0) AS avg_salary_inr,
                ROUND(AVG(j.is_remote) * 100.0, 1) AS remote_percentage,
                CURRENT_TIMESTAMP
            FROM skills s
            JOIN job_skills js ON s.id = js.skill_id
            JOIN cleaned_jobs j ON js.job_id = j.id
            GROUP BY s.id, s.name, s.category
            HAVING job_count > 0;
        """
        with self.get_connection() as conn:
            conn.execute(query)
            conn.commit()

    def get_all_cleaned_jobs_df(self) -> pd.DataFrame:
        """Retrieves all cleaned jobs as a Pandas DataFrame with joined skill lists."""
        query = """
            SELECT 
                j.id,
                j.source_id,
                j.title,
                j.company,
                j.job_family,
                j.experience_tier,
                j.years_min,
                j.years_max,
                j.salary_min_lpa,
                j.salary_max_lpa,
                j.salary_avg_lpa,
                j.salary_min_inr,
                j.salary_max_inr,
                j.salary_avg_inr,
                j.salary_avg_usd,
                j.is_remote,
                j.region,
                j.location_raw,
                j.skill_count,
                j.posted_at,
                GROUP_CONCAT(s.name, ', ') AS skills_str
            FROM cleaned_jobs j
            LEFT JOIN job_skills js ON j.id = js.job_id
            LEFT JOIN skills s ON js.skill_id = s.id
            GROUP BY j.id
            ORDER BY j.id DESC;
        """
        with self.get_connection() as conn:
            df = pd.read_sql_query(query, conn)
        
        # Convert skills_str into list
        df["skills"] = df["skills_str"].apply(lambda x: [s.strip() for s in x.split(",")] if pd.notna(x) and x else [])
        # Ensure salary_avg_lpa is available
        if "salary_avg_lpa" not in df or df["salary_avg_lpa"].isna().all():
            df["salary_avg_lpa"] = df["salary_avg_usd"]
        return df

    def get_top_skills_by_demand(self, limit: int = 20) -> pd.DataFrame:
        """SQL query: Top demanded technical competencies in India with LPA compensation."""
        query = """
            SELECT 
                s.name AS skill,
                s.category,
                COUNT(js.job_id) AS demand_count,
                ROUND(AVG(j.salary_avg_lpa), 2) AS avg_salary_lpa,
                ROUND(AVG(j.salary_avg_inr), 0) AS avg_salary_inr,
                ROUND(AVG(j.is_remote) * 100, 1) AS remote_pct
            FROM skills s
            JOIN job_skills js ON s.id = js.skill_id
            JOIN cleaned_jobs j ON js.job_id = j.id
            GROUP BY s.id, s.name, s.category
            ORDER BY demand_count DESC
            LIMIT ?;
        """
        with self.get_connection() as conn:
            return pd.read_sql_query(query, conn, params=(limit,))

    def get_compensation_by_experience(self) -> pd.DataFrame:
        """SQL query: Average, min, max compensation across experience tiers in India (LPA)."""
        query = """
            SELECT 
                experience_tier,
                COUNT(*) as job_count,
                ROUND(AVG(salary_avg_lpa), 2) as avg_salary_lpa,
                ROUND(MIN(salary_min_lpa), 2) as min_salary_lpa,
                ROUND(MAX(salary_max_lpa), 2) as max_salary_lpa,
                ROUND(AVG(salary_avg_inr), 0) as avg_salary_inr
            FROM cleaned_jobs
            WHERE salary_avg_lpa IS NOT NULL
            GROUP BY experience_tier
            ORDER BY avg_salary_lpa ASC;
        """
        with self.get_connection() as conn:
            return pd.read_sql_query(query, conn)

    def get_compensation_by_job_family(self) -> pd.DataFrame:
        """SQL query: Compensation scales by job family in India (LPA)."""
        query = """
            SELECT 
                job_family,
                COUNT(*) as job_count,
                ROUND(AVG(salary_avg_lpa), 2) as avg_salary_lpa,
                ROUND(AVG(salary_avg_inr), 0) as avg_salary_inr,
                ROUND(AVG(is_remote) * 100, 1) as remote_pct
            FROM cleaned_jobs
            WHERE salary_avg_lpa IS NOT NULL
            GROUP BY job_family
            ORDER BY avg_salary_lpa DESC;
        """
        with self.get_connection() as conn:
            return pd.read_sql_query(query, conn)

    def get_compensation_by_hub(self) -> pd.DataFrame:
        """SQL query: Compensation across major Indian Tech Hubs (LPA)."""
        query = """
            SELECT 
                region as tech_hub,
                COUNT(*) as job_count,
                ROUND(AVG(salary_avg_lpa), 2) as avg_salary_lpa,
                ROUND(AVG(salary_avg_inr), 0) as avg_salary_inr,
                ROUND(AVG(is_remote) * 100, 1) as remote_pct
            FROM cleaned_jobs
            WHERE salary_avg_lpa IS NOT NULL
            GROUP BY region
            ORDER BY avg_salary_lpa DESC;
        """
        with self.get_connection() as conn:
            return pd.read_sql_query(query, conn)

    def execute_custom_query(self, sql_query: str) -> pd.DataFrame:
        """Executes arbitrary SQL query and returns results as DataFrame."""
        with self.get_connection() as conn:
            return pd.read_sql_query(sql_query, conn)
