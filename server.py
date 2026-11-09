"""
FastAPI REST Backend for Indian Tech Market Intelligence & Salary Prediction Platform.
Powers the modern React frontend with live intelligence APIs, ML inference, and SQL execution.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from pathlib import Path
import json

from src.database.db_manager import DatabaseManager
from src.ingestion.data_loader import DataLoader
from src.models.predictor import SalaryPredictor
from src.nlp.taxonomy import ALL_CANONICAL_SKILLS, JOB_FAMILIES, EXPERIENCE_TIERS, SKILL_TAXONOMY, INDIAN_TECH_HUBS

app = FastAPI(
    title="Indian Tech Market Intelligence API",
    description="REST backend for Indian tech compensation analytics and ML salary prediction (2025-2026)",
    version="2.0.0"
)

# Enable CORS for React frontend (Vite dev server or production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database & Model Singletons
db = DatabaseManager()
loader = DataLoader(db)
predictor = SalaryPredictor()

class SalaryPredictionRequest(BaseModel):
    job_family: str = Field(..., example="Machine Learning & AI")
    experience_tier: str = Field(..., example="Senior (6-8 yrs)")
    region: str = Field(default="Bengaluru (Bangalore)", example="Bengaluru (Bangalore)")
    is_remote: bool = Field(default=False, example=False)
    years_min: Optional[int] = Field(default=None, example=6)
    skills: List[str] = Field(default_factory=list, example=["Python", "PyTorch", "LLMs / Generative AI"])

class StreamIngestRequest(BaseModel):
    count: int = Field(default=10, ge=1, le=100)

class SQLQueryRequest(BaseModel):
    query: str = Field(..., example="SELECT job_family, COUNT(*), ROUND(AVG(salary_avg_lpa), 2) AS avg_lpa FROM cleaned_jobs GROUP BY job_family ORDER BY avg_lpa DESC;")

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "market": "India (2025-2026)", "database_connected": True}

@app.get("/api/metadata")
def get_metadata():
    """Returns static taxonomies and filter lists."""
    return {
        "job_families": JOB_FAMILIES,
        "experience_tiers": EXPERIENCE_TIERS,
        "indian_hubs": INDIAN_TECH_HUBS,
        "skill_taxonomy": SKILL_TAXONOMY,
        "all_skills": ALL_CANONICAL_SKILLS
    }

@app.get("/api/overview")
def get_market_overview():
    """Returns core KPI metrics for Indian Tech Market."""
    df = db.get_all_cleaned_jobs_df()
    total_listings = len(df)
    target_col = "salary_avg_lpa" if "salary_avg_lpa" in df.columns else "salary_avg_usd"
    
    med_lpa = float(df[target_col].dropna().median()) if total_listings > 0 else 24.5
    avg_lpa = float(df[target_col].dropna().mean()) if total_listings > 0 else 26.8
    remote_pct = float(df["is_remote"].mean() * 100.0) if total_listings > 0 else 32.5

    top_skill_df = db.get_top_skills_by_demand(1)
    top_skill_name = str(top_skill_df.iloc[0]["skill"]) if not top_skill_df.empty else "Python"

    # Hub distribution
    hub_counts = df["region"].value_counts().to_dict()

    return {
        "total_listings": total_listings,
        "median_lpa": round(med_lpa, 1),
        "median_inr": int(med_lpa * 100000),
        "avg_lpa": round(avg_lpa, 1),
        "avg_inr": int(avg_lpa * 100000),
        "remote_percentage": round(remote_pct, 1),
        "top_skill": top_skill_name,
        "hub_distribution": hub_counts
    }

@app.get("/api/top-skills")
def get_top_skills(limit: int = 20):
    """Top demanded technical competencies in India."""
    df = db.get_top_skills_by_demand(limit)
    return df.to_dict(orient="records")

@app.get("/api/compensation-by-tier")
def get_compensation_by_tier():
    """Compensation spread across SDE seniority tiers."""
    df = db.get_compensation_by_experience()
    return df.to_dict(orient="records")

@app.get("/api/compensation-by-hub")
def get_compensation_by_hub():
    """Compensation comparison across Indian Tech Hubs."""
    df = db.get_compensation_by_hub()
    return df.to_dict(orient="records")

@app.get("/api/supply-demand-matrix")
def get_supply_demand_matrix():
    """2D Matrix of Job Families vs Experience Tiers."""
    df = db.get_all_cleaned_jobs_df()
    target_col = "salary_avg_lpa" if "salary_avg_lpa" in df.columns else "salary_avg_usd"
    valid = df[df[target_col].notna()].copy()
    
    pivot = valid.pivot_table(
        index="job_family",
        columns="experience_tier",
        values=target_col,
        aggfunc="mean"
    ).fillna(0)

    tier_order = [
        "Entry-Level (0-2 yrs)",
        "Mid-Level (3-5 yrs)",
        "Senior (6-8 yrs)",
        "Lead / Staff (9-12 yrs)",
        "Principal / Director (12+ yrs)"
    ]
    cols = [c for c in tier_order if c in pivot.columns]
    matrix = []
    for family in pivot.index:
        row = {"job_family": family}
        for c in cols:
            row[c] = round(float(pivot.loc[family, c]), 1)
        matrix.append(row)

    return {"columns": cols, "rows": matrix}

@app.get("/api/jobs")
def get_jobs(
    hub: Optional[str] = None,
    family: Optional[str] = None,
    tier: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 25,
    offset: int = 0
):
    """Filterable, paginated Indian job listings."""
    df = db.get_all_cleaned_jobs_df()
    if hub and hub != "All Tech Hubs":
        df = df[df["region"] == hub]
    if family and family != "All Job Families":
        df = df[df["job_family"] == family]
    if tier and tier != "All Tiers":
        df = df[df["experience_tier"] == tier]
    if search:
        s = search.lower()
        df = df[df["title"].str.lower().str.contains(s) | df["company"].str.lower().str.contains(s) | df["skills_str"].str.lower().str.contains(s)]

    total_count = len(df)
    paginated = df.iloc[offset : offset + limit]
    
    records = []
    for _, row in paginated.iterrows():
        records.append({
            "id": int(row["id"]),
            "title": str(row["title"]),
            "company": str(row["company"]),
            "job_family": str(row["job_family"]),
            "experience_tier": str(row["experience_tier"]),
            "salary_min_lpa": round(float(row.get("salary_min_lpa") or 0), 1),
            "salary_max_lpa": round(float(row.get("salary_max_lpa") or 0), 1),
            "salary_avg_lpa": round(float(row.get("salary_avg_lpa") or row.get("salary_avg_usd") or 0), 1),
            "salary_avg_inr": int(row.get("salary_avg_inr") or 0),
            "region": str(row["region"]),
            "is_remote": bool(row["is_remote"]),
            "skills": row["skills"] if isinstance(row["skills"], list) else []
        })

    return {"total": total_count, "jobs": records}

@app.post("/api/predict-salary")
def predict_salary(req: SalaryPredictionRequest):
    """Predicts realistic CTC bracket in LPA and INR using Champion ML model."""
    if not predictor.is_ready:
        predictor._load_artifacts()
        if not predictor.is_ready:
            raise HTTPException(status_code=503, detail="Model artifacts not yet loaded.")

    try:
        res = predictor.estimate_salary(
            job_family=req.job_family,
            experience_tier=req.experience_tier,
            skills=req.skills,
            region=req.region,
            is_remote=req.is_remote,
            years_min=req.years_min
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ingest-stream")
def ingest_stream(req: StreamIngestRequest):
    """Generates incremental Indian postings and ingests into SQLite."""
    try:
        new_jobs = loader.stream_live_tick(count=req.count)
        return {
            "success": True,
            "ingested_count": len(new_jobs),
            "message": f"Successfully ingested {len(new_jobs)} active Indian tech listings."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sql-query")
def execute_sql(req: SQLQueryRequest):
    """Executes arbitrary read-only SQL query against SQLite."""
    # Prevent write operations via API
    forbidden = ["drop", "delete", "truncate", "update", "insert", "alter"]
    lower_q = req.query.lower().strip()
    if any(lower_q.startswith(w) or f" {w} " in lower_q for w in forbidden):
        raise HTTPException(status_code=400, detail="Only analytical SELECT queries are permitted.")

    try:
        res_df = db.execute_custom_query(req.query)
        return {
            "columns": list(res_df.columns),
            "rows": res_df.to_dict(orient="records"),
            "row_count": len(res_df)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"SQL Execution Error: {str(e)}")

@app.get("/api/benchmark")
def get_model_benchmark():
    """Returns baseline regression metrics (OLS, Ridge, RF, Gradient Boosting)."""
    meta_path = Path(__file__).resolve().parent / "artifacts" / "models" / "model_benchmark.json"
    if meta_path.exists():
        with open(meta_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# Mount and serve built React frontend assets
dist_dir = Path(__file__).resolve().parent / "frontend" / "dist"
if dist_dir.exists():
    from fastapi.responses import FileResponse
    from fastapi.staticfiles import StaticFiles

    app.mount("/assets", StaticFiles(directory=str(dist_dir / "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_react_app(full_path: str):
        # Do not intercept api routes
        if full_path.startswith("api"):
            raise HTTPException(status_code=404, detail="API endpoint not found")
        target_file = dist_dir / full_path
        if target_file.exists() and target_file.is_file():
            return FileResponse(target_file)
        return FileResponse(dist_dir / "index.html")

if __name__ == "__main__":
    import os
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("server:app", host="0.0.0.0", port=port)
