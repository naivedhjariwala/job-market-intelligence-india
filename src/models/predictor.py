"""
Indian Market Salary Predictor and Compensation Bracket Estimator (2025-2026).
Inference engine that computes expected market compensation in LPA and INR,
realistic 25th-75th brackets, and individual skill value additions for Indian tech roles.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
import json
import joblib
import numpy as np
import pandas as pd
from .feature_engineering import FeatureTransformer

MODELS_DIR = Path(__file__).resolve().parent.parent.parent / "artifacts" / "models"

class SalaryPredictor:
    """Predicts realistic salary brackets in LPA and INR for Indian tech roles."""

    def __init__(self, models_dir: Path = MODELS_DIR):
        self.models_dir = Path(models_dir)
        self.model = None
        self.transformer = None
        self.benchmark_metadata = {}
        self.mae = 2.45  # Default MAE in LPA

        self._load_artifacts()

    def _load_artifacts(self):
        model_path = self.models_dir / "champion_salary_model.joblib"
        transformer_path = self.models_dir / "feature_transformer.joblib"
        meta_path = self.models_dir / "model_benchmark.json"

        if model_path.exists() and transformer_path.exists():
            self.model = joblib.load(model_path)
            self.transformer = FeatureTransformer.load(transformer_path)
            if meta_path.exists():
                with open(meta_path, "r", encoding="utf-8") as f:
                    self.benchmark_metadata = json.load(f)
                    champ = self.benchmark_metadata.get("champion_model")
                    if champ and champ in self.benchmark_metadata.get("metrics", {}):
                        self.mae = self.benchmark_metadata["metrics"][champ].get("MAE", 2.45)

    @property
    def is_ready(self) -> bool:
        return self.model is not None and self.transformer is not None

    def estimate_salary(
        self,
        job_family: str,
        experience_tier: str,
        skills: List[str],
        region: str = "Bengaluru (Bangalore)",
        is_remote: bool = True,
        years_min: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Estimates expected salary bracket in LPA (Lakhs Per Annum) and INR.
        """
        if not self.is_ready:
            raise RuntimeError("Model artifacts not loaded. Train models before predicting.")

        if years_min is None:
            tier_years_map = {
                "Entry-Level (0-2 yrs)": 1,
                "Mid-Level (3-5 yrs)": 4,
                "Senior (6-8 yrs)": 7,
                "Lead / Staff (9-12 yrs)": 10,
                "Principal / Director (12+ yrs)": 14
            }
            years_min = tier_years_map.get(experience_tier, 4)

        # Build single-row DataFrame
        input_data = pd.DataFrame([{
            "job_family": job_family,
            "experience_tier": experience_tier,
            "region": region,
            "years_min": years_min,
            "skill_count": len(skills),
            "is_remote": 1 if is_remote else 0,
            "skills": skills
        }])

        X = self.transformer.transform(input_data)
        point_prediction = float(self.model.predict(X)[0])

        # Realistic bracket: +/- 1.20 * MAE (in LPA)
        margin = self.mae * 1.20
        bracket_low_lpa = max(3.5, round(point_prediction - margin, 1))
        bracket_high_lpa = round(point_prediction + margin, 1)
        median_lpa = round(point_prediction, 1)

        # Full INR conversion
        median_inr = int(median_lpa * 100000)
        bracket_low_inr = int(bracket_low_lpa * 100000)
        bracket_high_inr = int(bracket_high_lpa * 100000)

        # Baseline baseline without skills to estimate skill additive contribution
        base_input = input_data.copy()
        base_input["skills"] = [[]]
        base_input["skill_count"] = 0
        X_base = self.transformer.transform(base_input)
        baseline_pred = float(self.model.predict(X_base)[0])
        total_skill_premium_lpa = max(0.0, point_prediction - baseline_pred)

        # Individual skill premiums in LPA
        skill_premiums_lpa = {}
        for skill in skills:
            single_skill_input = base_input.copy()
            single_skill_input["skills"] = [[skill]]
            single_skill_input["skill_count"] = 1
            X_single = self.transformer.transform(single_skill_input)
            pred_single = float(self.model.predict(X_single)[0])
            diff = max(0.0, pred_single - baseline_pred)
            skill_premiums_lpa[skill] = round(diff, 1)

        return {
            "predicted_median_lpa": median_lpa,
            "salary_bracket_low_lpa": bracket_low_lpa,
            "salary_bracket_high_lpa": bracket_high_lpa,
            "predicted_median_inr": median_inr,
            "salary_bracket_low_inr": bracket_low_inr,
            "salary_bracket_high_inr": bracket_high_inr,
            "confidence_margin_lpa": round(margin, 1),
            "job_family": job_family,
            "experience_tier": experience_tier,
            "region": region,
            "is_remote": is_remote,
            "total_skill_premium_lpa": round(total_skill_premium_lpa, 1),
            "total_skill_premium_inr": int(total_skill_premium_lpa * 100000),
            "skill_breakdown_lpa": skill_premiums_lpa,
            # Backwards-compatibility aliases
            "predicted_median_usd": median_lpa,
            "salary_bracket_low_usd": bracket_low_lpa,
            "salary_bracket_high_usd": bracket_high_lpa,
            "confidence_margin_usd": round(margin, 1),
            "total_skill_premium_usd": round(total_skill_premium_lpa, 1),
            "skill_breakdown": skill_premiums_lpa,
            "model_used": self.benchmark_metadata.get("champion_model", "Trained ML Regressor")
        }
