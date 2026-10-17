"""
Pillar 2B: Seasonal Revenue & Trend Forecasting Engine (PulsePredict)
- Aggregates cleaned transaction history into a continuous daily time series
- Engineers trend, calendar, Indian festive/FY-end, and Fourier seasonal harmonics
- Fits Ridge / Linear Regression to forecast next 30 / 60 / 90 days of revenue
- Provides upper/lower 90% prediction intervals and executive growth metrics
"""

from dataclasses import dataclass
from typing import Tuple
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression, Ridge


@dataclass
class ForecastSummary:
    """Executive summary metrics for the 30/60/90-day revenue forecast."""
    horizon_days: int
    historical_period_revenue: float
    forecasted_period_revenue: float
    expected_growth_pct: float
    daily_run_rate_hist: float
    daily_run_rate_forecast: float
    model_r2_score: float
    mae_daily: float


def _build_time_features(dates: pd.Series, origin_date: pd.Timestamp) -> pd.DataFrame:
    """
    Constructs deterministic trend + seasonal harmonic + calendar features
    for any sequence of dates so multi-step 90-day projections never suffer
    from recursive lag decay.
    """
    dt = pd.to_datetime(dates)
    t = (dt - origin_date).dt.days.astype(float)

    day_of_year = dt.dt.dayofyear.astype(float)
    day_of_week = dt.dt.dayofweek.astype(float)
    month = dt.dt.month

    features = pd.DataFrame(index=dates.index)
    # 1. Linear & slight damped trend
    features["trend_t"] = t / 365.0

    # 2. Yearly Fourier Harmonics (captures annual & half-yearly seasonality smoothly)
    features["sin_annual_1"] = np.sin(2 * np.pi * day_of_year / 365.25)
    features["cos_annual_1"] = np.cos(2 * np.pi * day_of_year / 365.25)
    features["sin_annual_2"] = np.sin(4 * np.pi * day_of_year / 365.25)
    features["cos_annual_2"] = np.cos(4 * np.pi * day_of_year / 365.25)

    # 3. Weekly Fourier Harmonics (captures B2B weekday vs weekend cycle)
    features["sin_weekly"] = np.sin(2 * np.pi * day_of_week / 7.0)
    features["cos_weekly"] = np.cos(2 * np.pi * day_of_week / 7.0)
    features["is_weekend"] = (day_of_week >= 5).astype(float)

    # 4. Indian Business Calendar Spikes (Festive Q3 Oct-Nov & Indian FY-End March)
    features["is_festive_or_fy_end"] = month.isin([3, 10, 11]).astype(float)
    features["is_month_end"] = (dt.dt.day >= 25).astype(float)

    return features


def run_revenue_forecast(
    clean_df: pd.DataFrame,
    horizon_days: int = 90,
    alpha_ridge: float = 1.5,
) -> Tuple[pd.DataFrame, ForecastSummary]:
    """
    Universal Seasonal Revenue Forecaster.
    Handles everything from 2-day snapshots to 10-year corporate histories.
    """
    if clean_df is None or clean_df.empty:
        empty_ts = pd.DataFrame(
            columns=["Date", "Actual_Revenue", "Rolling_7D_Revenue", "Model_Fit", "Forecast_Lower", "Forecast_Upper", "Series_Type"]
        )
        return empty_ts, ForecastSummary(horizon_days, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

    df = clean_df.copy()
    df["_day"] = df["_date"].dt.normalize()

    daily_raw = df.groupby("_day")["_revenue"].sum().reset_index()
    min_date = daily_raw["_day"].min()
    max_date = daily_raw["_day"].max()

    # Edge case: If dataset only spans 1 single day, pad 14 prior days so regression can still fit
    if min_date == max_date:
        min_date = max_date - pd.Timedelta(days=14)

    full_date_range = pd.date_range(start=min_date, end=max_date, freq="D")
    hist_ts = pd.DataFrame({"Date": full_date_range})
    hist_ts = hist_ts.merge(
        daily_raw.rename(columns={"_day": "Date", "_revenue": "Actual_Revenue"}),
        on="Date",
        how="left",
    )
    hist_ts["Actual_Revenue"] = hist_ts["Actual_Revenue"].fillna(0.0)
    hist_ts["Rolling_7D_Revenue"] = (
        hist_ts["Actual_Revenue"].rolling(window=7, min_periods=1).mean()
    )

    X_train = _build_time_features(hist_ts["Date"], origin_date=min_date)
    y_train = hist_ts["Rolling_7D_Revenue"].values

    model = Ridge(alpha=alpha_ridge, random_state=42) if alpha_ridge > 0 else LinearRegression()
    model.fit(X_train, y_train)

    hist_pred = np.maximum(0.0, model.predict(X_train))
    hist_ts["Model_Fit"] = hist_pred
    hist_ts["Series_Type"] = "Historical"

    residuals = y_train - hist_pred
    residual_std = float(np.std(residuals)) if len(residuals) > 1 else 0.0
    r2 = float(max(0.0, model.score(X_train, y_train))) if len(hist_ts) > 2 else 0.0
    mae = float(np.mean(np.abs(residuals))) if len(residuals) > 0 else 0.0

    future_dates = pd.date_range(
        start=max_date + pd.Timedelta(days=1), periods=horizon_days, freq="D"
    )
    future_ts = pd.DataFrame({"Date": future_dates})
    X_future = _build_time_features(future_ts["Date"], origin_date=min_date)
    future_pred = np.maximum(0.0, model.predict(X_future))

    step_index = np.arange(1, horizon_days + 1)
    fan_multiplier = 1.645 * (1.0 + 0.35 * (step_index / horizon_days))
    margin = residual_std * fan_multiplier

    future_ts["Actual_Revenue"] = np.nan
    future_ts["Rolling_7D_Revenue"] = np.nan
    future_ts["Model_Fit"] = future_pred
    future_ts["Forecast_Lower"] = np.maximum(0.0, future_pred - margin)
    future_ts["Forecast_Upper"] = future_pred + margin
    future_ts["Series_Type"] = "Forecast"

    hist_ts["Forecast_Lower"] = np.nan
    hist_ts["Forecast_Upper"] = np.nan

    combined_ts = pd.concat([hist_ts, future_ts], ignore_index=True)

    prior_window_df = hist_ts.tail(horizon_days)
    hist_period_rev = float(prior_window_df["Actual_Revenue"].sum())
    forecast_period_rev = float(future_ts["Model_Fit"].sum())

    if hist_period_rev > 0:
        growth_pct = ((forecast_period_rev - hist_period_rev) / hist_period_rev) * 100.0
    else:
        growth_pct = 0.0

    summary = ForecastSummary(
        horizon_days=horizon_days,
        historical_period_revenue=round(hist_period_rev, 2),
        forecasted_period_revenue=round(forecast_period_rev, 2),
        expected_growth_pct=round(growth_pct, 2),
        daily_run_rate_hist=round(hist_period_rev / max(1, len(prior_window_df)), 2),
        daily_run_rate_forecast=round(forecast_period_rev / max(1, horizon_days), 2),
        model_r2_score=round(r2, 3),
        mae_daily=round(mae, 2),
    )

    return combined_ts, summary