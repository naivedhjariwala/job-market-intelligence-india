-- SQL Schema for Indian Tech Market Intelligence & Salary Prediction Platform (2025-2026)

-- 1. Raw jobs storage
CREATE TABLE IF NOT EXISTS raw_jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id TEXT UNIQUE,
    source_name TEXT,
    title TEXT,
    company TEXT,
    location TEXT,
    raw_description TEXT,
    raw_salary TEXT,
    url TEXT,
    ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Cleaned and normalized jobs
CREATE TABLE IF NOT EXISTS cleaned_jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    raw_job_id INTEGER,
    source_id TEXT UNIQUE,
    title TEXT NOT NULL,
    company TEXT,
    job_family TEXT NOT NULL,
    experience_tier TEXT NOT NULL,
    years_min INTEGER,
    years_max INTEGER,
    salary_min_lpa REAL,
    salary_max_lpa REAL,
    salary_avg_lpa REAL,
    salary_min_inr REAL,
    salary_max_inr REAL,
    salary_avg_inr REAL,
    salary_min_usd REAL,
    salary_max_usd REAL,
    salary_avg_usd REAL,
    is_remote INTEGER DEFAULT 0,
    region TEXT NOT NULL,
    location_raw TEXT,
    skill_count INTEGER DEFAULT 0,
    clean_description TEXT,
    posted_at TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (raw_job_id) REFERENCES raw_jobs (id)
);

-- 3. Skills master taxonomy
CREATE TABLE IF NOT EXISTS skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    category TEXT NOT NULL
);

-- 4. Many-to-many relationship: Job to Skills
CREATE TABLE IF NOT EXISTS job_skills (
    job_id INTEGER NOT NULL,
    skill_id INTEGER NOT NULL,
    PRIMARY KEY (job_id, skill_id),
    FOREIGN KEY (job_id) REFERENCES cleaned_jobs (id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES skills (id) ON DELETE CASCADE
);

-- 5. Market aggregates / view cache
CREATE TABLE IF NOT EXISTS skill_market_aggregates (
    skill_name TEXT PRIMARY KEY,
    category TEXT,
    job_count INTEGER,
    avg_salary_lpa REAL,
    median_salary_lpa REAL,
    avg_salary_inr REAL,
    remote_percentage REAL,
    last_computed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Performance Indexes
CREATE INDEX IF NOT EXISTS idx_cleaned_jobs_family ON cleaned_jobs (job_family);
CREATE INDEX IF NOT EXISTS idx_cleaned_jobs_tier ON cleaned_jobs (experience_tier);
CREATE INDEX IF NOT EXISTS idx_cleaned_jobs_region ON cleaned_jobs (region);
CREATE INDEX IF NOT EXISTS idx_cleaned_jobs_salary ON cleaned_jobs (salary_avg_lpa);
CREATE INDEX IF NOT EXISTS idx_job_skills_skill ON job_skills (skill_id);
CREATE INDEX IF NOT EXISTS idx_job_skills_job ON job_skills (job_id);
