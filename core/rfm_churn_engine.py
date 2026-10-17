"""
Pillar 2A: RFM Segmentation & Explainable Customer Churn Engine (PulsePredict)
- Computes Recency, Frequency, Monetary (RFM) + Inter-Purchase Interval (IPI) velocity features
- Assigns Executive RFM Segments (Champions, Loyal, Potential Loyalist, At-Risk, Hibernating)
- Trains a Scikit-Learn Decision Tree / Random Forest Classifier to predict Churn Probability
- Generates human-readable 'Explainable Risk Reasons' and calculates Revenue-at-Risk
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier


@dataclass
class ChurnModelSummary:
    """Executive summary metrics from the RFM & Churn ML pipeline."""
    total_customers: int
    at_risk_customers: int
    total_revenue: float
    revenue_at_risk: float
    avg_churn_probability: float
    feature_importances: Dict[str, float]
    model_type: str


def _assign_rfm_segment(row: pd.Series) -> str:
    """Maps R, F, M tertile scores (1-3) and churn risk into clear executive segments."""
    r, f, m = row["R_Score"], row["F_Score"], row["M_Score"]
    if r == 3 and f == 3 and m == 3:
        return "Champions"
    if r >= 2 and f >= 2 and m >= 2:
        return "Loyal Accounts"
    if r == 1 and (f >= 2 or m >= 2):
        return "At-Risk (High Value)"
    if r == 1 and f == 1:
        return "Churned / Dormant"
    if r >= 2 and f == 1:
        return "Promising / Recent"
    return "Need Attention"


def _build_explainable_reason(row: pd.Series, median_recency: float) -> str:
    """Generates a deterministic, human-readable explanation for a customer's risk status."""
    reasons: List[str] = []
    recency = int(row["Recency_Days"])
    ipi = float(row["Avg_InterPurchase_Days"])
    overdue_ratio = float(row["Overdue_Ratio"])
    h2_drop = float(row["Second_Half_Activity_Ratio"])

    if recency > max(45, median_recency * 1.3):
        reasons.append(f"Inactive for {recency} days")
    if overdue_ratio >= 2.0 and ipi > 0:
        reasons.append(f"{overdue_ratio:.1f}x past normal {int(round(ipi))}d reorder cycle")
    if h2_drop < 0.35:
        drop_pct = int(round((1.0 - h2_drop) * 100))
        reasons.append(f"{drop_pct}% drop in recent period order volume")

    if not reasons:
        if row["Churn_Probability"] >= 0.50:
            return f"Slowing purchase cadence ({recency}d since last invoice)"
        return "Healthy ordering cadence & active engagement"

    return " + ".join(reasons[:2])


def run_rfm_and_churn_pipeline(
    clean_df: pd.DataFrame,
    model_choice: str = "RandomForest",
    inactivity_threshold_days: int = 45,
) -> Tuple[pd.DataFrame, ChurnModelSummary]:
    """
    Computes customer-level RFM metrics,behavioral velocity features, and trains
    an explainable Scikit-Learn classifier to score churn probability (0.0 to 1.0).
    """
    df = clean_df.copy()
    max_date = df["_date"].max()
    min_date = df["_date"].min()
    midpoint_date = min_date + (max_date - min_date) / 2

    # 1. Aggregate behavioral features per canonical customer
    cust_groups = df.groupby("_customer", as_index=False).agg(
        Last_Order_Date=("_date", "max"),
        First_Order_Date=("_date", "min"),
        Frequency=("_date", "count"),
        Unique_Order_Days=("_date", lambda s: s.dt.normalize().nunique()),
        Monetary=("_revenue", "sum"),
        Avg_Order_Value=("_revenue", "mean"),
        Total_Quantity=("_quantity", "sum"),
    )

    # Calculate H1 vs H2 activity ratio (detects sudden drop-offs in second half of dataset)
    h2_counts = (
        df[df["_date"] >= midpoint_date]
        .groupby("_customer")["_date"]
        .count()
        .to_dict()
    )

    cust_groups["Recency_Days"] = (max_date - cust_groups["Last_Order_Date"]).dt.days
    cust_groups["Tenure_Days"] = np.maximum(
        1, (cust_groups["Last_Order_Date"] - cust_groups["First_Order_Date"]).dt.days
    )

    # Average Inter-Purchase Interval (IPI) in days
    cust_groups["Avg_InterPurchase_Days"] = np.where(
        cust_groups["Frequency"] > 1,
        cust_groups["Tenure_Days"] / np.maximum(1, cust_groups["Frequency"] - 1),
        cust_groups["Tenure_Days"],
    )

    # Overdue Ratio: How many times longer than their usual reorder cycle has the customer been silent?
    cust_groups["Overdue_Ratio"] = cust_groups["Recency_Days"] / np.maximum(
        1.0, cust_groups["Avg_InterPurchase_Days"]
    )

    # Second-half activity ratio
    cust_groups["H2_Orders"] = cust_groups["_customer"].map(h2_counts).fillna(0)
    cust_groups["Second_Half_Activity_Ratio"] = cust_groups["H2_Orders"] / np.maximum(
        1, cust_groups["Frequency"]
    )

    # 2. Compute RFM Quantile Scores (1 = Low, 3 = High) safely even on small customer counts
    def _safe_tertile(series: pd.Series, invert: bool = False) -> pd.Series:
        ranks = series.rank(method="first", pct=True)
        if invert:
            ranks = 1.0 - ranks
        return pd.cut(ranks, bins=[-0.01, 0.33, 0.66, 1.01], labels=[1, 2, 3]).astype(int)

    cust_groups["R_Score"] = _safe_tertile(cust_groups["Recency_Days"], invert=True)
    cust_groups["F_Score"] = _safe_tertile(cust_groups["Frequency"], invert=False)
    cust_groups["M_Score"] = _safe_tertile(cust_groups["Monetary"], invert=False)
    cust_groups["RFM_Score"] = (
        cust_groups["R_Score"] * 100 + cust_groups["F_Score"] * 10 + cust_groups["M_Score"]
    )
    cust_groups["RFM_Segment"] = cust_groups.apply(_assign_rfm_segment, axis=1)

    # 3. Construct Behavioral Churn Target Label for Supervised ML Training
    # A customer is labeled as behavioral churn (1) if they exceed inactivity threshold
    # OR their overdue ratio is > 2.5x with dropping H2 activity.
    adaptive_cutoff = max(
        inactivity_threshold_days,
        float(np.percentile(cust_groups["Recency_Days"], 65)),
    )
    y_label = (
        (cust_groups["Recency_Days"] >= adaptive_cutoff)
        | (
            (cust_groups["Overdue_Ratio"] >= 2.2)
            & (cust_groups["Second_Half_Activity_Ratio"] < 0.35)
        )
    ).astype(int)

    # Ensure both classes (0 and 1) exist so classifier can train cleanly
    if y_label.nunique() < 2:
        median_rec = cust_groups["Recency_Days"].median()
        y_label = (cust_groups["Recency_Days"] > median_rec).astype(int)

    feature_cols = [
        "Recency_Days",
        "Frequency",
        "Monetary",
        "Avg_Order_Value",
        "Avg_InterPurchase_Days",
        "Overdue_Ratio",
        "Second_Half_Activity_Ratio",
    ]
    X = cust_groups[feature_cols].fillna(0.0)

    # 4. Train Explainable Scikit-Learn Classifier (Random Forest or Decision Tree)
    if model_choice.lower() == "decisiontree":
        clf = DecisionTreeClassifier(max_depth=4, min_samples_leaf=1, random_state=42)
        model_label = "Decision Tree Classifier (max_depth=4)"
    else:
        clf = RandomForestClassifier(
            n_estimators=100, max_depth=4, min_samples_leaf=1, random_state=42
        )
        model_label = "Random Forest Classifier (100 trees)"

    clf.fit(X, y_label)

    # Predict continuous churn probabilities blended with behavioral overdue sigmoid for smooth gradation
    if hasattr(clf, "predict_proba") and len(clf.classes_) == 2:
        ml_probs = clf.predict_proba(X)[:, 1]
    else:
        ml_probs = clf.predict(X).astype(float)

    # Blend 70% ML probability + 30% continuous overdue score so probabilities rank smoothly
    continuous_risk = 1.0 / (1.0 + np.exp(-(cust_groups["Recency_Days"] - adaptive_cutoff) / 15.0))
    cust_groups["Churn_Probability"] = np.clip(
        0.70 * ml_probs + 0.30 * continuous_risk, 0.02, 0.98
    ).round(3)

    cust_groups["Risk_Level"] = pd.cut(
        cust_groups["Churn_Probability"],
        bins=[-0.01, 0.35, 0.65, 1.01],
        labels=["Low Risk", "Medium Risk", "High Risk (At-Risk)"],
    ).astype(str)

    # Explainable AI Reason per Customer
    median_recency = float(cust_groups["Recency_Days"].median())
    cust_groups["Risk_Explanation"] = cust_groups.apply(
        lambda r: _build_explainable_reason(r, median_recency), axis=1
    )

    # Calculate Revenue at Risk (Expected Monetary loss weighted by churn risk for High/Medium risk accounts)
    cust_groups["Revenue_At_Risk"] = np.where(
        cust_groups["Churn_Probability"] >= 0.50,
        cust_groups["Monetary"] * cust_groups["Churn_Probability"],
        0.0,
    ).round(2)

    # Extract Feature Importances
    importances = {
        col: round(float(imp), 4)
        for col, imp in zip(feature_cols, clf.feature_importances_)
    }
    importances = dict(sorted(importances.items(), key=lambda x: x[1], reverse=True))

    # Sort table by highest Revenue at Risk / Churn Probability
    cust_groups = cust_groups.sort_values(
        by=["Churn_Probability", "Monetary"], ascending=[False, False]
    ).reset_index(drop=True)

    at_risk_mask = cust_groups["Churn_Probability"] >= 0.50
    summary = ChurnModelSummary(
        total_customers=len(cust_groups),
        at_risk_customers=int(at_risk_mask.sum()),
        total_revenue=float(cust_groups["Monetary"].sum()),
        revenue_at_risk=float(cust_groups.loc[at_risk_mask, "Monetary"].sum()),
        avg_churn_probability=float(cust_groups["Churn_Probability"].mean()),
        feature_importances=importances,
        model_type=model_label,
    )

    return cust_groups, summary