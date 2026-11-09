"""
Interactive Streamlit Web Dashboard: Indian Tech Market Intelligence & Salary Prediction Platform (2025-2026).
Provides real-time Indian market ingestion, dynamic Matplotlib visualizations in LPA & INR,
interactive ML salary predictor, and live SQL exploration.
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import json

from src.database.db_manager import DatabaseManager
from src.ingestion.data_loader import DataLoader
from src.models.predictor import SalaryPredictor
from src.models.train_models import ModelTrainer
from src.nlp.taxonomy import ALL_CANONICAL_SKILLS, JOB_FAMILIES, EXPERIENCE_TIERS, SKILL_TAXONOMY, INDIAN_TECH_HUBS
from src.visualization.charts import MarketVisualizer

st.set_page_config(
    page_title="Indian Tech Market Intelligence & Salary Prediction Platform",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for crisp UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .salary-bracket-card {
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
        color: white;
        padding: 24px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    .salary-bracket-val {
        font-size: 2.8rem;
        font-weight: 900;
        margin: 8px 0;
    }
    .salary-bracket-sub {
        font-size: 1.15rem;
        opacity: 0.9;
    }
</style>
""", unsafe_allow_html=True)

# Initialize resources
@st.cache_resource
def get_db_manager():
    return DatabaseManager()

@st.cache_resource
def get_data_loader():
    return DataLoader(get_db_manager())

@st.cache_resource
def get_predictor():
    return SalaryPredictor()

@st.cache_resource
def get_visualizer():
    return MarketVisualizer()

db = get_db_manager()
loader = get_data_loader()
predictor = get_predictor()
viz = get_visualizer()

# Sidebar: Controls & Navigation
st.sidebar.markdown("## 🇮🇳 India Market Intelligence")
st.sidebar.caption("Bengaluru • Hyderabad • Pune • Delhi NCR • Mumbai • Chennai")

menu = st.sidebar.radio(
    "Navigation",
    ["📊 Indian Market Dynamics", "🧠 ML Salary Predictor (LPA)", "⚡ Real-Time Ingestion (India)", "🔍 SQL Query Console", "📖 Documentation & Taxonomy"]
)

# Load current data from SQLite
df_jobs = db.get_all_cleaned_jobs_df()
total_jobs = len(df_jobs)

if total_jobs == 0:
    st.warning("Database is currently initializing with Indian tech market data...")
    loader.load_initial_dataset(target_count=600, fetch_apis=False)
    df_jobs = db.get_all_cleaned_jobs_df()
    total_jobs = len(df_jobs)

# Determine LPA target column
target_lpa_col = "salary_avg_lpa" if "salary_avg_lpa" in df_jobs.columns else "salary_avg_usd"

# -------------------------------------------------------------
# TAB 1: INDIAN MARKET DYNAMICS DASHBOARD
# -------------------------------------------------------------
if menu == "📊 Indian Market Dynamics":
    st.markdown('<div class="main-header">🇮🇳 Indian Tech Market Intelligence & Compensation Dynamics</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Tracking high-demand technical competencies, hiring trends, and regional compensation scales across Indian Tech Hubs (2025–2026).</div>', unsafe_allow_html=True)

    # Key KPI Metrics
    col1, col2, col3, col4 = st.columns(4)
    avg_lpa = df_jobs[target_lpa_col].dropna().mean()
    med_lpa = df_jobs[target_lpa_col].dropna().median()
    remote_ratio = (df_jobs["is_remote"].mean()) * 100
    top_skill_row = db.get_top_skills_by_demand(1)
    top_skill_name = top_skill_row.iloc[0]["skill"] if not top_skill_row.empty else "Python"

    col1.metric("Active Indian Listings", f"{total_jobs:,}", "Tech Hubs Feed")
    col2.metric("Median Tech CTC (India)", f"₹{med_lpa:.1f} LPA", f"₹{int(med_lpa*100000):,}/yr")
    col3.metric("Remote / WFH Ratio", f"{remote_ratio:.1f}%", "Pan-India Remote")
    col4.metric("#1 High-Demand Skill", top_skill_name, "Taxonomy Leader")

    st.markdown("---")

    # Filters
    st.subheader("Filter Market View")
    fcol1, fcol2, fcol3 = st.columns(3)
    selected_family = fcol1.selectbox("Job Family", ["All Job Families"] + JOB_FAMILIES)
    selected_tier = fcol2.selectbox("Experience Tier", ["All Tiers"] + EXPERIENCE_TIERS)
    selected_hub = fcol3.selectbox("Indian Tech Hub", ["All Tech Hubs"] + INDIAN_TECH_HUBS)

    filtered_df = df_jobs.copy()
    if selected_family != "All Job Families":
        filtered_df = filtered_df[filtered_df["job_family"] == selected_family]
    if selected_tier != "All Tiers":
        filtered_df = filtered_df[filtered_df["experience_tier"] == selected_tier]
    if selected_hub != "All Tech Hubs":
        filtered_df = filtered_df[filtered_df["region"] == selected_hub]

    st.caption(f"Displaying **{len(filtered_df)}** matching listings.")

    # Visualizations
    vcol1, vcol2 = st.columns(2)

    with vcol1:
        st.markdown("#### Compensation Dynamics by Experience Tier (LPA)")
        fig_tier_path = viz.plot_compensation_by_tier(filtered_df, "tmp_tier.png")
        if fig_tier_path.exists():
            st.image(str(fig_tier_path), use_container_width=True)

    with vcol2:
        st.markdown("#### Top 20 In-Demand Technical Competencies in India")
        top_skills_df = db.get_top_skills_by_demand(20)
        fig_skills_path = viz.plot_top_skills_demand_and_salary(top_skills_df, "tmp_skills.png")
        if fig_skills_path.exists():
            st.image(str(fig_skills_path), use_container_width=True)

    st.markdown("---")
    vcol3, vcol4 = st.columns(2)

    with vcol3:
        st.markdown("#### Talent Compensation Matrix across Indian Job Families (₹ LPA)")
        fig_matrix_path = viz.plot_supply_demand_gap_matrix(df_jobs, "tmp_matrix.png")
        if fig_matrix_path.exists():
            st.image(str(fig_matrix_path), use_container_width=True)

    with vcol4:
        st.markdown("#### Major Indian Tech Hubs: Remote vs In-Office Dynamics")
        fig_reg_path = viz.plot_regional_compensation_breakdown(df_jobs, "tmp_region.png")
        if fig_reg_path.exists():
            st.image(str(fig_reg_path), use_container_width=True)

    # Model baselines overview
    meta_path = Path(__file__).resolve().parent / "artifacts" / "models" / "model_benchmark.json"
    if meta_path.exists():
        with open(meta_path, "r", encoding="utf-8") as f:
            bench = json.load(f)
        st.markdown("---")
        st.markdown("#### Machine Learning Regression Baselines Benchmark (LPA)")
        fig_bench_path = viz.plot_baseline_models_comparison(bench, "tmp_bench.png")
        if fig_bench_path.exists():
            st.image(str(fig_bench_path), use_container_width=True)

# -------------------------------------------------------------
# TAB 2: ML SALARY PREDICTOR (LPA & INR)
# -------------------------------------------------------------
elif menu == "🧠 ML Salary Predictor (LPA)":
    st.markdown('<div class="main-header">🧠 Machine Learning Salary Bracket Estimator (India)</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Multi-variate regression estimating realistic compensation brackets in Lakhs Per Annum (LPA) and INR based on experience tier, required skills, and Indian tech hub.</div>', unsafe_allow_html=True)

    if not predictor.is_ready:
        st.warning("Model artifacts not yet generated. Training ML regression models on Indian market data...")
        trainer = ModelTrainer(db)
        trainer.train_and_evaluate_all()
        predictor._load_artifacts()
        st.success("Champion model trained and loaded successfully!")

    pcol1, pcol2 = st.columns([1, 1.2])

    with pcol1:
        st.markdown("### Profile Parameters")
        pred_family = st.selectbox("Job Family", JOB_FAMILIES, index=0)
        pred_tier = st.selectbox("Experience Tier / Level", EXPERIENCE_TIERS, index=1)
        pred_hub = st.selectbox("Target Indian Tech Hub", INDIAN_TECH_HUBS, index=0)
        pred_remote = st.toggle("Remote / WFH Role", value=False)
        pred_years = st.slider("Specific Experience (Years)", min_value=0, max_value=20, value=4)

        # Categorized skill selector
        st.markdown("### Technical Skill Taxonomy Selection")
        selected_skills = []
        for cat_name, skill_dict in SKILL_TAXONOMY.items():
            with st.expander(f"{cat_name} ({len(skill_dict)} competencies)", expanded=(cat_name in ["AI & Machine Learning", "Backend & Systems"])):
                chosen = st.multiselect(
                    f"Select {cat_name} Skills",
                    options=list(skill_dict.keys()),
                    key=f"skill_cat_{cat_name}"
                )
                selected_skills.extend(chosen)

        predict_btn = st.button("🚀 Calculate Estimated Indian Salary Bracket", type="primary", use_container_width=True)

    with pcol2:
        st.markdown("### Estimated CTC & Compensation Breakdown")
        if predict_btn or True:  # Default display
            res = predictor.estimate_salary(
                job_family=pred_family,
                experience_tier=pred_tier,
                skills=selected_skills,
                region=pred_hub,
                is_remote=pred_remote,
                years_min=pred_years
            )

            st.markdown(f"""
            <div class="salary-bracket-card">
                <div class="salary-bracket-sub">PREDICTED COMPENSATION BRACKET (2025–2026 CTC)</div>
                <div class="salary-bracket-val">₹{res['salary_bracket_low_lpa']} – ₹{res['salary_bracket_high_lpa']} LPA</div>
                <div class="salary-bracket-sub">Estimated Median CTC: <strong>₹{res['predicted_median_lpa']} LPA (₹{res['predicted_median_inr']:,} INR / year)</strong></div>
                <div style="margin-top: 10px; font-size: 0.9rem; opacity: 0.85;">Model Engine: {res['model_used']} | Margin: ±₹{res['confidence_margin_lpa']} LPA</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("#### Value Breakdown & Skill Premiums in India")
            bcol1, bcol2 = st.columns(2)
            bcol1.metric("Total Skill Valuation Premium", f"+₹{res['total_skill_premium_lpa']} LPA", f"+₹{res['total_skill_premium_inr']:,}/yr")
            bcol2.metric("Selected Skills Count", f"{len(selected_skills)} skills")

            if res["skill_breakdown_lpa"]:
                st.markdown("**Individual Skill Premiums (Estimated Annual Value Addition in India):**")
                breakdown_df = pd.DataFrame([
                    {"Technical Skill": k, "Estimated Annual Premium (LPA)": f"+₹{v:.1f} LPA", "Annual INR Addition": f"+₹{int(v*100000):,}"}
                    for k, v in res["skill_breakdown_lpa"].items()
                ])
                st.dataframe(breakdown_df, use_container_width=True)
            else:
                st.info("Tip: Select technical competencies on the left to observe individual skill premiums in the Indian market.")

# -------------------------------------------------------------
# TAB 3: REAL-TIME DATA INGESTION
# -------------------------------------------------------------
elif menu == "⚡ Real-Time Ingestion (India)":
    st.markdown('<div class="main-header">⚡ Indian Market Real-Time Ingestion & Stream Engine</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Continuous streaming of active job listings from Indian tech enterprises, unicorn startups, and GCCs.</div>', unsafe_allow_html=True)

    icol1, icol2 = st.columns(2)

    with icol1:
        st.markdown("### Stream Live Indian Tech Postings")
        stream_count = st.slider("Number of Postings to Stream", min_value=5, max_value=50, value=15)
        
        if st.button("⚡ Ingest Indian Market Stream Now", type="primary"):
            with st.spinner("Ingesting and running NLP parsing pipeline..."):
                new_jobs = loader.stream_live_tick(count=stream_count)
                st.success(f"Successfully parsed and ingested {len(new_jobs)} live Indian job records into SQLite!")
                st.rerun()

    with icol2:
        st.markdown("### Reseed Indian Market Baseline")
        st.write("Generate full realistic 2025–2026 Indian tech market seed across all 9 job families and 5 experience tiers:")
        if st.button("🇮🇳 Reseed Full India Dataset (600+ Jobs)"):
            with st.spinner("Populating SQLite with Indian tech listings..."):
                raw_c, clean_c = loader.load_initial_dataset(target_count=600, fetch_apis=False)
                st.success(f"Synchronization complete: {clean_c} jobs stored in SQLite.")
                st.rerun()

    st.markdown("---")
    st.markdown("### Latest Ingested Job Listings (India)")
    cols_to_show = ["id", "title", "company", "job_family", "experience_tier", "salary_avg_lpa", "region", "is_remote", "skills_str"]
    available_cols = [c for c in cols_to_show if c in df_jobs.columns]
    st.dataframe(df_jobs[available_cols].head(25), use_container_width=True)

# -------------------------------------------------------------
# TAB 4: SQL QUERY CONSOLE
# -------------------------------------------------------------
elif menu == "🔍 SQL Query Console":
    st.markdown('<div class="main-header">🔍 Interactive SQL Analytics Console (Indian Market)</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Direct SQL execution against the relational schema in LPA and INR (raw_jobs, cleaned_jobs, skills, job_skills).</div>', unsafe_allow_html=True)

    preset_queries = {
        "Top 10 Highest-Paying Tech Skills in India (LPA)": """
SELECT 
    s.name AS skill,
    s.category,
    COUNT(j.id) AS job_count,
    ROUND(AVG(j.salary_avg_lpa), 2) AS avg_salary_lpa,
    ROUND(AVG(j.salary_avg_inr), 0) AS avg_salary_inr
FROM skills s
JOIN job_skills js ON s.id = js.skill_id
JOIN cleaned_jobs j ON js.job_id = j.id
GROUP BY s.name, s.category
HAVING job_count >= 5
ORDER BY avg_salary_lpa DESC
LIMIT 10;
""",
        "Compensation across Indian Tech Hubs (LPA)": """
SELECT 
    region as tech_hub,
    COUNT(*) as total_postings,
    ROUND(AVG(salary_avg_lpa), 2) as avg_ctc_lpa,
    ROUND(MIN(salary_min_lpa), 2) as min_ctc_lpa,
    ROUND(MAX(salary_max_lpa), 2) as max_ctc_lpa,
    ROUND(AVG(is_remote) * 100, 1) as remote_pct
FROM cleaned_jobs
GROUP BY region
ORDER BY avg_ctc_lpa DESC;
""",
        "SDE Experience Tier Ladder (SDE-1 to Principal Engineer) in India": """
SELECT 
    experience_tier,
    COUNT(*) as total_roles,
    ROUND(AVG(salary_avg_lpa), 2) as avg_ctc_lpa,
    ROUND(AVG(salary_avg_inr), 0) as avg_ctc_inr,
    ROUND(AVG(skill_count), 1) as avg_required_skills
FROM cleaned_jobs
GROUP BY experience_tier
ORDER BY avg_ctc_lpa ASC;
"""
    }

    selected_preset = st.selectbox("Choose a Preset Analytical SQL Query", list(preset_queries.keys()))
    default_query = preset_queries[selected_preset]

    query_input = st.text_area("SQL Statement", value=default_query, height=180)

    if st.button("▶️ Execute SQL Query", type="primary"):
        try:
            res_df = db.execute_custom_query(query_input)
            st.success(f"Query returned {len(res_df)} rows.")
            st.dataframe(res_df, use_container_width=True)
        except Exception as e:
            st.error(f"SQL Execution Error: {e}")

# -------------------------------------------------------------
# TAB 5: DOCUMENTATION & TAXONOMY
# -------------------------------------------------------------
elif menu == "📖 Documentation & Taxonomy":
    st.markdown('<div class="main-header">📖 Indian Market Architecture & Skill Taxonomy</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Technical specifications and taxonomies tailored for the Indian tech ecosystem.</div>', unsafe_allow_html=True)

    st.markdown("""
    ### Indian Market Adaptation Overview
    1. **Compensation Standards**: Standardized in **LPA (Lakhs Per Annum)** and **INR (₹)** reflecting Indian tech hiring dynamics (Fixed CTC + ESOPs + Variable).
    2. **Hub Representation**: Covers Tier-1 tech centers: **Bengaluru (Bangalore)**, **Hyderabad**, **Delhi NCR (Gurgaon / Noida)**, **Pune**, **Mumbai**, **Chennai**, and **Remote (Pan-India)**.
    3. **NLP Seniority Mapping**: Accurately recognizes SDE-1, SDE-2, SDE-3, SSE, MTS, Tech Lead, Engineering Manager, Staff, and Principal tiers.
    4. **Machine Learning Baselines**: Regression algorithms (Random Forest, Gradient Boosting, Ridge, OLS) trained directly on LPA targets with bracket estimation confidence intervals.
    """)

    st.markdown("### Technical Competencies Master Taxonomy")
    for cat, skills in SKILL_TAXONOMY.items():
        with st.expander(f"{cat} ({len(skills)} skills)"):
            st.write(", ".join([f"`{s}`" for s in skills.keys()]))
