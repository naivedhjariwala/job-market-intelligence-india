"""
Main Execution Script for Indian Tech Market Intelligence & Salary Prediction Platform (2025-2026).
Runs end-to-end pipeline:
1. Relational SQLite Schema & Taxonomy Seeding (SQL in LPA & INR)
2. Real-Time Indian Job Market Ingestion & Streaming
3. NLP Cleansing, Skill Taxonomy Extraction & SDE Seniority Classification
4. Machine Learning Regression Baselines (Scikit-Learn)
5. Analytical Visualizations Generation (Matplotlib in LPA)
6. Sample Inference & Realistic Indian CTC Bracket Estimation
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.database.db_manager import DatabaseManager
from src.ingestion.data_loader import DataLoader
from src.models.train_models import ModelTrainer
from src.models.predictor import SalaryPredictor
from src.visualization.charts import MarketVisualizer

def run_pipeline(fetch_live_apis: bool = False, target_jobs: int = 600):
    print("=" * 72)
    print("🇮🇳 JOB MARKET INTELLIGENCE & SALARY PREDICTION PLATFORM (INDIA 2025-2026)")
    print("=" * 72)

    # 1. Initialize Relational Database
    print("\n[Step 1/5] Initializing Relational SQLite Database & Seeding Taxonomy (India)...")
    # Remove existing db if re-seeding full Indian market schema
    db = DatabaseManager()
    print(f"Database initialized at: {db.db_path}")

    # 2. Ingest & Parse Indian Job Market Listings
    print("\n[Step 2/5] Ingesting Job Postings & Running NLP Parsing Pipeline (LPA & INR)...")
    loader = DataLoader(db)
    raw_count, clean_count = loader.load_initial_dataset(target_count=target_jobs, fetch_apis=fetch_live_apis)
    print(f"Ingestion complete: {clean_count} validated Indian tech listings stored.")

    # 3. Train Machine Learning Regression Baselines
    print("\n[Step 3/5] Training & Benchmarking Machine Learning Baselines (Scikit-Learn in LPA)...")
    trainer = ModelTrainer(db)
    benchmark_summary = trainer.train_and_evaluate_all()

    # 4. Generate Publication-Quality Analytical Visualizations
    print("\n[Step 4/5] Generating Analytical Visualizations (Matplotlib in LPA)...")
    viz = MarketVisualizer()
    df_jobs = db.get_all_cleaned_jobs_df()
    top_skills_df = db.get_top_skills_by_demand(25)
    chart_paths = viz.generate_all_visualizations(df_jobs, top_skills_df, benchmark_summary)
    print(f"Generated {len(chart_paths)} high-resolution visualization charts in {viz.output_dir}:")
    for cp in chart_paths:
        print(f"  - {cp.name}")

    # 5. Execute Sample Real-Time Salary Predictions in LPA & INR
    print("\n[Step 5/5] Testing Inference Engine with Real-World Indian Tech Archetypes...")
    predictor = SalaryPredictor()

    sample_queries = [
        {
            "job_family": "Machine Learning & AI",
            "experience_tier": "Senior (6-8 yrs)",
            "skills": ["Python", "PyTorch", "LLMs / Generative AI", "RAG (Retrieval-Augmented)", "Kubernetes"],
            "region": "Bengaluru (Bangalore)",
            "is_remote": False
        },
        {
            "job_family": "Backend & Distributed Systems",
            "experience_tier": "Lead / Staff (9-12 yrs)",
            "skills": ["Go (Golang)", "PostgreSQL", "Kubernetes", "Apache Kafka", "Docker", "Microservices"],
            "region": "Hyderabad",
            "is_remote": True
        },
        {
            "job_family": "Full Stack Engineering",
            "experience_tier": "Mid-Level (3-5 yrs)",
            "skills": ["TypeScript", "React", "Next.js", "Node.js", "PostgreSQL"],
            "region": "Pune",
            "is_remote": False
        }
    ]

    for q in sample_queries:
        res = predictor.estimate_salary(**q)
        print("\n" + "-" * 65)
        print(f"Role: {q['experience_tier']} {q['job_family']} ({q['region']}, Remote={q['is_remote']})")
        print(f"Skills: {', '.join(q['skills'])}")
        print(f"Estimated CTC Bracket: ₹{res['salary_bracket_low_lpa']} – ₹{res['salary_bracket_high_lpa']} LPA (₹{res['salary_bracket_low_inr']:,} – ₹{res['salary_bracket_high_inr']:,} INR)")
        print(f"Median CTC: ₹{res['predicted_median_lpa']} LPA (Skill Valuation Addition: +₹{res['total_skill_premium_lpa']} LPA)")

    print("\n" + "=" * 72)
    print("✅ Indian Market Pipeline executed successfully!")
    print("To launch the interactive dashboard, run:")
    print("  streamlit run app.py")
    print("=" * 72)

if __name__ == "__main__":
    run_pipeline()
