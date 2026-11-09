"""
Model Training and Regression Baseline Comparison Pipeline.
Trains and compares Linear Regression, Ridge, Random Forest, and Gradient Boosting.
Saves champion model and metadata.
"""

from pathlib import Path
from typing import Dict, Any, Tuple
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor

from .feature_engineering import FeatureTransformer
from .evaluation import evaluate_predictions, calculate_bracket_coverage
from ..database.db_manager import DatabaseManager

MODELS_DIR = Path(__file__).resolve().parent.parent.parent / "artifacts" / "models"

class ModelTrainer:
    """Orchestrates baseline training, validation, and serialization."""

    def __init__(self, db_manager: DatabaseManager, output_dir: Path = MODELS_DIR):
        self.db = db_manager
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.transformer = FeatureTransformer()

    def load_data(self) -> pd.DataFrame:
        df = self.db.get_all_cleaned_jobs_df()
        target_col = "salary_avg_lpa" if "salary_avg_lpa" in df.columns else "salary_avg_usd"
        df = df[df[target_col].notna() & (df[target_col] >= 2.0)].copy()
        df["target_salary"] = df[target_col]
        return df

    def train_and_evaluate_all(self, test_size: float = 0.20, random_state: int = 42) -> Dict[str, Any]:
        """Trains all 4 regression baselines, benchmarks them, and saves the champion."""
        df = self.load_data()
        if len(df) < 50:
            raise ValueError(f"Insufficient training records ({len(df)} found). Please seed database first.")

        print(f"Loaded {len(df)} validated Indian tech market listings for training.")

        train_df, test_df = train_test_split(df, test_size=test_size, random_state=random_state)

        # Fit feature pipeline
        X_train = self.transformer.fit_transform(train_df)
        X_test = self.transformer.transform(test_df)

        y_train = train_df["target_salary"].values
        y_test = test_df["target_salary"].values

        # Baseline candidates
        candidates = {
            "Linear Regression (OLS)": LinearRegression(),
            "Ridge Regression (L2)": Ridge(alpha=1.0, random_state=random_state),
            "Random Forest Regressor": RandomForestRegressor(n_estimators=120, max_depth=16, random_state=random_state, n_jobs=-1),
            "Gradient Boosting Regressor": HistGradientBoostingRegressor(max_iter=150, learning_rate=0.08, random_state=random_state)
        }

        results: Dict[str, Dict[str, Any]] = {}
        trained_models: Dict[str, Any] = {}
        best_model_name = None
        best_r2 = -float("inf")

        print("\n" + "=" * 68)
        print(f"{'Regression Baseline':<30} | {'MAE (LPA)':<11} | {'RMSE (LPA)':<11} | {'R² Score':<8}")
        print("=" * 68)

        for name, model in candidates.items():
            model.fit(X_train, y_train)
            preds = model.predict(X_test)
            metrics = evaluate_predictions(y_test, preds)

            # Evaluate bracket coverage (predictions +/- 1.25 * MAE)
            bracket_margin = metrics["MAE"] * 1.25
            cov = calculate_bracket_coverage(y_test, preds - bracket_margin, preds + bracket_margin)
            metrics["bracket_coverage_pct"] = cov

            results[name] = metrics
            trained_models[name] = model

            print(f"{name:<30} | ₹{metrics['MAE']:<10.2f} | ₹{metrics['RMSE']:<10.2f} | {metrics['R2']:<8.4f}")

            if metrics["R2"] > best_r2:
                best_r2 = metrics["R2"]
                best_model_name = name

        print("=" * 68)
        print(f"Champion Model Selected: {best_model_name} (R² = {best_r2:.4f})\n")

        # Save champion model & artifacts
        champion_model = trained_models[best_model_name]
        champion_path = self.output_dir / "champion_salary_model.joblib"
        joblib.dump(champion_model, champion_path)

        # Save transformer
        transformer_path = self.output_dir / "feature_transformer.joblib"
        self.transformer.save(transformer_path)

        # Feature importances / coefficients
        importances = self._extract_feature_importances(champion_model, self.transformer.feature_names)

        # Save summary report
        summary = {
            "champion_model": best_model_name,
            "metrics": results,
            "sample_counts": {
                "total": len(df),
                "train": len(train_df),
                "test": len(test_df)
            },
            "top_features": importances[:25]
        }

        with open(self.output_dir / "model_benchmark.json", "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

        return summary

    def _extract_feature_importances(self, model: Any, feature_names: list) -> list:
        """Extracts top predictive features from the model."""
        pairs = []
        if hasattr(model, "feature_importances_"):
            vals = model.feature_importances_
            pairs = sorted(zip(feature_names, vals), key=lambda x: x[1], reverse=True)
        elif hasattr(model, "coef_"):
            vals = np.abs(model.coef_)
            pairs = sorted(zip(feature_names, vals), key=lambda x: x[1], reverse=True)
        else:
            return []

        return [{"feature": name, "importance": round(float(val), 5)} for name, val in pairs]

