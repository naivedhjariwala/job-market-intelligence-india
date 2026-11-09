"""
Feature Engineering Pipeline for Salary Regression Models.
Encodes multi-hot technical skills, one-hot categorical features, and numerical experience vectors.
"""

from typing import List, Dict, Any, Tuple
import numpy as np
import pandas as pd
from sklearn.preprocessing import OneHotEncoder, MultiLabelBinarizer, StandardScaler
from sklearn.compose import ColumnTransformer
import joblib
from pathlib import Path
from ..nlp.taxonomy import ALL_CANONICAL_SKILLS, EXPERIENCE_TIERS, JOB_FAMILIES

class FeatureTransformer:
    """Transforms raw job records into tabular ML matrices."""

    def __init__(self):
        self.mlb = MultiLabelBinarizer(classes=ALL_CANONICAL_SKILLS)
        self.cat_encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
        self.scaler = StandardScaler()
        self.is_fitted = False
        self.feature_names: List[str] = []

    def fit(self, df: pd.DataFrame) -> "FeatureTransformer":
        """Fits encoders and scalers on training data."""
        # Multi-hot encode skills
        skills_series = df["skills"].apply(lambda s: s if isinstance(s, list) else [])
        self.mlb.fit(skills_series)

        # Categorical features: job_family, experience_tier, region
        cat_df = df[["job_family", "experience_tier", "region"]]
        self.cat_encoder.fit(cat_df)

        # Numerical features: years_min, skill_count, is_remote
        num_features = self._extract_numerical(df)
        self.scaler.fit(num_features)

        # Cache feature names
        skill_cols = [f"skill_{s}" for s in self.mlb.classes_]
        cat_cols = list(self.cat_encoder.get_feature_names_out(["job_family", "experience_tier", "region"]))
        num_cols = ["years_exp", "skill_count", "is_remote"]
        self.feature_names = cat_cols + num_cols + skill_cols

        self.is_fitted = True
        return self

    def _extract_numerical(self, df: pd.DataFrame) -> np.ndarray:
        years = df["years_min"].fillna(3).values.reshape(-1, 1)
        skill_cnt = df["skill_count"].fillna(df["skills"].apply(lambda s: len(s) if isinstance(s, list) else 0)).values.reshape(-1, 1)
        is_rem = df["is_remote"].astype(float).values.reshape(-1, 1)
        return np.hstack([years, skill_cnt, is_rem])

    def transform(self, df: pd.DataFrame) -> np.ndarray:
        """Transforms DataFrame into design matrix X."""
        if not self.is_fitted:
            raise ValueError("FeatureTransformer must be fitted before transform.")

        cat_df = df[["job_family", "experience_tier", "region"]]
        X_cat = self.cat_encoder.transform(cat_df)

        X_num = self._extract_numerical(df)
        X_num_scaled = self.scaler.transform(X_num)

        skills_series = df["skills"].apply(lambda s: s if isinstance(s, list) else [])
        X_skills = self.mlb.transform(skills_series)

        return np.hstack([X_cat, X_num_scaled, X_skills])

    def fit_transform(self, df: pd.DataFrame) -> np.ndarray:
        return self.fit(df).transform(df)

    def save(self, filepath: Path):
        """Serializes transformer state."""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self, filepath)

    @classmethod
    def load(cls, filepath: Path) -> "FeatureTransformer":
        """Loads serialized transformer state."""
        return joblib.load(filepath)

