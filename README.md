# 🇮🇳 Indian Tech Market Intelligence & Salary Prediction Platform (2025 – 2026)

An end-to-end data intelligence and machine learning platform specifically designed for the **Indian Tech Ecosystem (2025–2026)** to extract, cleanse, and parse unstructured tech job listings, track high-demand technical competencies across Indian Tech Hubs (Bengaluru, Hyderabad, Pune, Delhi NCR, Mumbai, Chennai), analyze regional compensation scales in **Lakhs Per Annum (LPA)** and **INR (₹)**, and estimate realistic compensation brackets using machine learning regression baselines.

---

## 🌟 Indian Market Highlights & Capabilities

1. **Indian Compensation Normalization (LPA & INR)**:
   - Automated parser translating unstructured Indian salary expressions (`15 - 25 LPA`, `₹18 to ₹28 Lakhs per annum`, `₹12,00,000 - ₹20,00,000 INR`, `24 LPA Fixed CTC`) into standardized **LPA (Lakhs Per Annum)** and **INR (₹)**.
   - Dual-unit SQL storage enabling instant querying and reporting in both LPA and INR.

2. **Major Indian Tech Hubs**:
   - **Bengaluru (Bangalore)**: Silicon Valley of India, high-density AI/ML & Product Unicorns (Razorpay, Swiggy, Flipkart, CRED, Krutrim AI).
   - **Hyderabad**: Global Capability Centers (GCCs) and Enterprise Cloud (Microsoft IDC, Amazon India, Salesforce, Google).
   - **Delhi NCR (Gurgaon / Noida)**: E-commerce, quick-commerce, and fintech scale-ups (Zomato/Blinkit, Adobe India, Paytm).
   - **Pune**: SaaS, automotive software, and distributed platform engineering.
   - **Mumbai**: Fintech, algorithmic trading (HFT), and banking systems (Zepto, BrowserStack).
   - **Chennai**: Enterprise SaaS capital (Freshworks, Zoho) and systems infrastructure.
   - **Remote (India)**: Flexible pan-India WFH roles.

3. **NLP SDE Seniority & Taxonomy Parsing**:
   - Indian tech hierarchy recognition: **SDE-1 / Fresher (0-2 yrs)**, **SDE-2 / Mid-Level (3-5 yrs)**, **SDE-3 / Senior (6-8 yrs)**, **Lead / Staff / EM (9-12 yrs)**, and **Principal / Director (12+ yrs)**.
   - Extraction of 120+ modern competencies across AI/ML (LLMs, RAG, PyTorch, LangChain), Cloud & DevOps (Kubernetes, Docker, Terraform), Backend (Go, Rust, FastAPI, Spring Boot), and Data Engineering.

4. **Machine Learning Regression Baselines in LPA**:
   - 4 Scikit-Learn regression baselines trained directly on LPA targets:
     - *Ordinary Least Squares (Linear Regression)* — Champion ($R^2 = 0.9861$, MAE = ₹1.18 LPA)
     - *Ridge Regression ($L_2$ Regularization)* ($R^2 = 0.9833$)
     - *Random Forest Regressor* ($R^2 = 0.9832$)
     - *Gradient Boosting Regressor* ($R^2 = 0.9800$)
   - Predicts realistic compensation brackets in LPA: e.g. **₹24.9 – ₹27.7 LPA** (₹24,90,000 – ₹27,70,000 INR).
   - Calculates individual skill premiums added to Indian CTCs (e.g. *LLMs / Generative AI*: +₹5.4 LPA, *Kubernetes*: +₹3.2 LPA).

5. **Analytical Visualizations in LPA (Matplotlib)**:
   - High-resolution (300 DPI) visual charts formatted in ₹ LPA:
     - `compensation_dynamics_tier.png`: Box plot of compensation dynamics across SDE tiers in India.
     - `high_demand_skills.png`: Top 20 skills in India ranked by demand volume and colored by average LPA.
     - `supply_demand_matrix.png`: Heatmap matrix of Job Families vs. SDE Seniority Tiers in India.
     - `regional_compensation_scales.png`: Comparative analysis of Remote (WFH) vs. In-Office across Indian Tech Hubs.
     - `ml_baselines_comparison.png`: MAE and $R^2$ baseline benchmark in LPA.

6. **Interactive Streamlit Web Dashboard**:
   - Interactive Indian tech hub filter, LPA/INR salary predictor with categorized skill picker, real-time streaming ingestion trigger, and built-in SQL console with Indian market presets.

---

## ⚡ Quick Start

```bash
# 1. Run complete pipeline (Ingest -> Parse -> Train -> Visualize -> Archetype Prediction)
python main.py

# 2. Launch the interactive Streamlit Web Dashboard
streamlit run app.py

# 3. Run automated test suite (100% passing)
python -m pytest tests/test_platform.py -v
```
