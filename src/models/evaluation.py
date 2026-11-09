"""
Model Evaluation Metrics and Residual Diagnostics.
Calculates MAE, RMSE, R2, MedAPE, and prediction bracket confidence coverage.
"""

from typing import Dict, Any
import numpy as np
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score

def evaluate_predictions(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """Computes comprehensive regression evaluation metrics."""
    mae = mean_absolute_error(y_true, y_pred)
    rmse = root_mean_squared_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)

    # Median Absolute Percentage Error
    ape = np.abs((y_true - y_pred) / np.maximum(y_true, 1e-5)) * 100.0
    med_ape = float(np.median(ape))
    mean_ape = float(np.mean(ape))

    return {
        "MAE": round(float(mae), 2),
        "RMSE": round(float(rmse), 2),
        "R2": round(float(r2), 4),
        "MedAPE_pct": round(med_ape, 2),
        "MeanAPE_pct": round(mean_ape, 2)
    }

def calculate_bracket_coverage(y_true: np.ndarray, y_low: np.ndarray, y_high: np.ndarray) -> float:
    """Calculates percentage of ground truth salaries falling inside predicted bracket."""
    inside = (y_true >= y_low) & (y_true <= y_high)
    return round(float(np.mean(inside) * 100.0), 2)

