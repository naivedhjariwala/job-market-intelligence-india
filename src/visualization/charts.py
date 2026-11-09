"""
Publication-Quality Matplotlib Analytical Visualizations for the Indian Tech Market.
Illustrates compensation dynamics (LPA & INR), skill demand, Indian tech hub comparisons,
and talent supply-demand gaps.
"""

import os
from pathlib import Path
from typing import Optional, List, Dict, Any

# Configure local writable directory for matplotlib cache
mpl_cache_dir = Path(__file__).resolve().parent.parent.parent / "data" / ".matplotlib"
mpl_cache_dir.mkdir(parents=True, exist_ok=True)
os.environ["MPLCONFIGDIR"] = str(mpl_cache_dir)

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for headless / script generation
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
import seaborn as sns

FIGURES_DIR = Path(__file__).resolve().parent.parent.parent / "artifacts" / "figures"

# Style theme configuration
plt.rcParams["font.sans-serif"] = ["Segoe UI", "DejaVu Sans", "Helvetica", "Arial"]
plt.rcParams["axes.edgecolor"] = "#D0D7DE"
plt.rcParams["axes.linewidth"] = 0.8

class MarketVisualizer:
    """Generates analytical charts for Indian Tech Market using Matplotlib and Pandas."""

    def __init__(self, output_dir: Path = FIGURES_DIR):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _get_target_col(self, df: pd.DataFrame) -> str:
        if "salary_avg_lpa" in df.columns and df["salary_avg_lpa"].notna().any():
            return "salary_avg_lpa"
        return "salary_avg_usd"

    def plot_compensation_by_tier(self, df: pd.DataFrame, save_filename: str = "compensation_dynamics_tier.png") -> Path:
        """Box plot of compensation dynamics across experience tiers in India (LPA)."""
        target_col = self._get_target_col(df)
        valid_df = df[df[target_col].notna() & (df[target_col] >= 2.0)].copy()
        
        tier_order = [
            "Entry-Level (0-2 yrs)",
            "Mid-Level (3-5 yrs)",
            "Senior (6-8 yrs)",
            "Lead / Staff (9-12 yrs)",
            "Principal / Director (12+ yrs)"
        ]
        existing_tiers = [t for t in tier_order if t in valid_df["experience_tier"].unique()]

        fig, ax = plt.subplots(figsize=(11, 6), dpi=300)
        fig.patch.set_facecolor("#FFFFFF")
        ax.set_facecolor("#FAFBFC")

        palette = ["#3B82F6", "#10B981", "#F59E0B", "#8B5CF6", "#EC4899"]
        
        sns.boxplot(
            data=valid_df,
            x="experience_tier",
            y=target_col,
            hue="experience_tier",
            legend=False,
            order=existing_tiers,
            palette=palette[:len(existing_tiers)],
            boxprops=dict(alpha=0.85, linewidth=1.2),
            whiskerprops=dict(linewidth=1.2, color="#4B5563"),
            capprops=dict(linewidth=1.2, color="#4B5563"),
            medianprops=dict(linewidth=2.2, color="#111827"),
            ax=ax,
            width=0.55
        )

        # Overlay jittered stripplot for sample density
        sns.stripplot(
            data=valid_df,
            x="experience_tier",
            y=target_col,
            order=existing_tiers,
            color="#1F2937",
            alpha=0.25,
            size=4,
            jitter=0.2,
            ax=ax
        )

        # Annotate median salary values in LPA
        medians = valid_df.groupby("experience_tier")[target_col].median()
        for idx, tier in enumerate(existing_tiers):
            if tier in medians:
                val = medians[tier]
                ax.text(
                    idx, val + 2.5, f"₹{val:.1f} LPA",
                    horizontalalignment="center",
                    size=10, weight="bold", color="#111827",
                    bbox=dict(boxstyle="round,pad=0.2", facecolor="#FFFFFF", edgecolor="#D1D5DB", alpha=0.9)
                )

        ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, _: f"₹{y:.0f} LPA"))
        ax.grid(axis="y", linestyle="--", alpha=0.6, color="#E5E7EB")
        ax.set_title("Compensation Dynamics by Experience Tier across Indian Tech Hubs (2025–2026)", fontsize=13, weight="bold", pad=15, color="#111827")
        ax.set_xlabel("Experience Tier (SDE-1 to Principal/Director)", fontsize=11, weight="semibold", labelpad=10, color="#374151")
        ax.set_ylabel("Annual Compensation (₹ Lakhs Per Annum - LPA)", fontsize=11, weight="semibold", labelpad=10, color="#374151")

        plt.tight_layout()
        save_path = self.output_dir / save_filename
        fig.savefig(save_path, bbox_inches="tight")
        plt.close(fig)
        return save_path

    def plot_top_skills_demand_and_salary(self, top_skills_df: pd.DataFrame, save_filename: str = "high_demand_skills.png") -> Path:
        """Horizontal bar chart of top technical competencies in India colored by average LPA."""
        salary_col = "avg_salary_lpa" if "avg_salary_lpa" in top_skills_df.columns else "avg_salary"
        df_sorted = top_skills_df.sort_values(by="demand_count", ascending=True).tail(20)

        fig, ax = plt.subplots(figsize=(12, 8), dpi=300)
        fig.patch.set_facecolor("#FFFFFF")
        ax.set_facecolor("#FAFBFC")

        norm = plt.Normalize(df_sorted[salary_col].min(), df_sorted[salary_col].max())
        cmap = matplotlib.colormaps["viridis"]
        colors = [cmap(norm(val)) for val in df_sorted[salary_col]]

        bars = ax.barh(df_sorted["skill"], df_sorted["demand_count"], color=colors, height=0.68, edgecolor="#4B5563", linewidth=0.5)

        # Value annotations
        for bar, (_, row) in zip(bars, df_sorted.iterrows()):
            width = bar.get_width()
            val = row[salary_col]
            salary_str = f"₹{val:.1f} LPA" if pd.notna(val) else "N/A"
            ax.text(
                width + 2, bar.get_y() + bar.get_height() / 2,
                f" {int(width)} postings | Avg: {salary_str}",
                va="center", ha="left", fontsize=9, color="#1F2937", weight="medium"
            )

        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])
        cbar = fig.colorbar(sm, ax=ax, orientation="vertical", pad=0.02, shrink=0.8)
        cbar.set_label("Average Compensation in India (₹ LPA)", fontsize=10, weight="semibold", labelpad=10)
        cbar.ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, _: f"₹{y:.0f} LPA"))

        ax.grid(axis="x", linestyle="--", alpha=0.6, color="#E5E7EB")
        ax.set_title("Top 20 In-Demand Technical Competencies in India & Compensation Scales (2025–2026)", fontsize=13, weight="bold", pad=15, color="#111827")
        ax.set_xlabel("Listing Frequency / Demand Count", fontsize=11, weight="semibold", labelpad=10, color="#374151")
        ax.set_ylabel("Technical Skill", fontsize=11, weight="semibold", labelpad=10, color="#374151")

        plt.tight_layout()
        save_path = self.output_dir / save_filename
        fig.savefig(save_path, bbox_inches="tight")
        plt.close(fig)
        return save_path

    def plot_supply_demand_gap_matrix(self, df: pd.DataFrame, save_filename: str = "supply_demand_matrix.png") -> Path:
        """2D Heatmap matrix of Job Families vs Experience Tiers in India (LPA)."""
        target_col = self._get_target_col(df)
        valid_df = df[df[target_col].notna()].copy()
        pivot = valid_df.pivot_table(
            index="job_family",
            columns="experience_tier",
            values=target_col,
            aggfunc="mean"
        )

        tier_order = [
            "Entry-Level (0-2 yrs)",
            "Mid-Level (3-5 yrs)",
            "Senior (6-8 yrs)",
            "Lead / Staff (9-12 yrs)",
            "Principal / Director (12+ yrs)"
        ]
        cols = [c for c in tier_order if c in pivot.columns]
        pivot = pivot[cols].sort_values(by=cols[-1] if cols else pivot.columns[0], ascending=False)

        fig, ax = plt.subplots(figsize=(12, 7), dpi=300)
        fig.patch.set_facecolor("#FFFFFF")

        sns.heatmap(
            pivot,
            annot=True,
            fmt=".1f",
            cmap="YlGnBu",
            linewidths=1,
            linecolor="#E5E7EB",
            cbar_kws={"label": "Mean Salary (₹ LPA)", "format": "₹%.0f LPA"},
            ax=ax
        )

        ax.set_title("Talent Compensation & Seniority Matrix across Indian Job Families (₹ LPA)", fontsize=13, weight="bold", pad=15, color="#111827")
        ax.set_xlabel("Experience Tier", fontsize=11, weight="semibold", labelpad=10, color="#374151")
        ax.set_ylabel("Job Family", fontsize=11, weight="semibold", labelpad=10, color="#374151")

        plt.tight_layout()
        save_path = self.output_dir / save_filename
        fig.savefig(save_path, bbox_inches="tight")
        plt.close(fig)
        return save_path

    def plot_regional_compensation_breakdown(self, df: pd.DataFrame, save_filename: str = "regional_compensation_scales.png") -> Path:
        """Grouped bar chart comparing Major Indian Tech Hubs: Remote vs On-Site Dynamics."""
        target_col = self._get_target_col(df)
        valid_df = df[df[target_col].notna()].copy()
        valid_df["Workplace"] = valid_df["is_remote"].apply(lambda r: "Remote" if r == 1 else "On-Site / Hybrid")

        pivot = valid_df.groupby(["region", "Workplace"])[target_col].mean().unstack().fillna(0)
        pivot = pivot.sort_values(by="On-Site / Hybrid" if "On-Site / Hybrid" in pivot.columns else pivot.columns[0], ascending=False)

        fig, ax = plt.subplots(figsize=(11, 6), dpi=300)
        fig.patch.set_facecolor("#FFFFFF")
        ax.set_facecolor("#FAFBFC")

        x = np.arange(len(pivot.index))
        width = 0.35

        ax.bar(x - width/2, pivot.get("Remote", 0), width, label="Remote (WFH)", color="#3B82F6", edgecolor="#1E40AF")
        ax.bar(x + width/2, pivot.get("On-Site / Hybrid", 0), width, label="On-Site / In-Office", color="#10B981", edgecolor="#065F46")

        ax.set_xticks(x)
        ax.set_xticklabels(pivot.index, rotation=15, ha="right", fontsize=9.5, weight="medium")
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, _: f"₹{y:.0f} LPA"))
        ax.grid(axis="y", linestyle="--", alpha=0.6, color="#E5E7EB")

        ax.set_title("Compensation Scales across Major Indian Tech Hubs (₹ LPA): Remote vs In-Office", fontsize=13, weight="bold", pad=15, color="#111827")
        ax.set_ylabel("Mean Annual Compensation (₹ LPA)", fontsize=11, weight="semibold", labelpad=10, color="#374151")
        ax.legend(frameon=True, facecolor="#FFFFFF", edgecolor="#D1D5DB")

        plt.tight_layout()
        save_path = self.output_dir / save_filename
        fig.savefig(save_path, bbox_inches="tight")
        plt.close(fig)
        return save_path

    def plot_baseline_models_comparison(self, benchmark_dict: Dict[str, Any], save_filename: str = "ml_baselines_comparison.png") -> Path:
        """Visual comparison of ML regression baselines in LPA (MAE and R2 Score)."""
        metrics = benchmark_dict.get("metrics", {})
        if not metrics:
            return Path("")

        model_names = list(metrics.keys())
        mae_vals = [metrics[m]["MAE"] for m in model_names]
        r2_vals = [metrics[m]["R2"] for m in model_names]

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5), dpi=300)
        fig.patch.set_facecolor("#FFFFFF")

        # MAE plot (lower is better)
        colors_mae = ["#60A5FA", "#34D399", "#FBBF24", "#A78BFA"]
        bars1 = ax1.barh(model_names, mae_vals, color=colors_mae[:len(model_names)], edgecolor="#374151", height=0.55)
        ax1.set_title("Mean Absolute Error in LPA (Lower is Better)", fontsize=12, weight="bold", pad=10)
        ax1.set_xlabel("MAE (₹ LPA)", fontsize=10, weight="semibold")
        ax1.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"₹{x:.1f} LPA"))
        ax1.grid(axis="x", linestyle="--", alpha=0.6)
        for bar in bars1:
            w = bar.get_width()
            ax1.text(w + 0.1, bar.get_y() + bar.get_height()/2, f"₹{w:.2f} LPA", va="center", ha="left", fontsize=9, weight="bold")

        # R2 plot (higher is better)
        colors_r2 = ["#93C5FD", "#6EE7B7", "#FDE68A", "#C4B5FD"]
        bars2 = ax2.barh(model_names, r2_vals, color=colors_r2[:len(model_names)], edgecolor="#374151", height=0.55)
        ax2.set_title("Coefficient of Determination R² (Higher is Better)", fontsize=12, weight="bold", pad=10)
        ax2.set_xlabel("R² Score", fontsize=10, weight="semibold")
        ax2.set_xlim(0, 1.0)
        ax2.grid(axis="x", linestyle="--", alpha=0.6)
        for bar in bars2:
            w = bar.get_width()
            ax2.text(w + 0.02, bar.get_y() + bar.get_height()/2, f"{w:.4f}", va="center", ha="left", fontsize=9, weight="bold")

        plt.suptitle("Machine Learning Regression Baselines Benchmark (Indian Tech Market)", fontsize=14, weight="bold", y=1.02)
        plt.tight_layout()
        save_path = self.output_dir / save_filename
        fig.savefig(save_path, bbox_inches="tight")
        plt.close(fig)
        return save_path

    def generate_all_visualizations(self, df: pd.DataFrame, top_skills_df: pd.DataFrame, benchmark_dict: Optional[Dict[str, Any]] = None) -> List[Path]:
        """Generates full suite of publication-quality charts."""
        paths = []
        paths.append(self.plot_compensation_by_tier(df))
        paths.append(self.plot_top_skills_demand_and_salary(top_skills_df))
        paths.append(self.plot_supply_demand_gap_matrix(df))
        paths.append(self.plot_regional_compensation_breakdown(df))
        if benchmark_dict:
            paths.append(self.plot_baseline_models_comparison(benchmark_dict))
        return paths
