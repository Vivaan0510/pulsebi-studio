"""
Pillar 3C: 1-Click Standalone Offline HTML Dashboard Compiler
Bundles Plotly interactive charts, KPI cards, and the Top-100 Churn Watchlist into a single shareable HTML report.
"""

from datetime import datetime
from typing import Dict
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio

from core.data_scrubber import ScrubAuditReport
from core.forecast_engine import ForecastSummary
from core.rfm_churn_engine import ChurnModelSummary


def compile_standalone_html_dashboard(
    dataset_name: str,
    audit_report: ScrubAuditReport,
    churn_summary: ChurnModelSummary,
    forecast_summary: ForecastSummary,
    figs: Dict[str, go.Figure],
    rfm_df: pd.DataFrame,
) -> bytes:
    """Generates a self-contained HTML file with interactive Plotly charts and executive tables."""
    generated_ts = datetime.now().strftime("%d %b %Y, %I:%M %p IST")

    fcst_html = pio.to_html(figs["forecast"], full_html=False, include_plotlyjs="cdn")
    pareto_html = pio.to_html(figs["pareto"], full_html=False, include_plotlyjs=False)
    rfm_html = pio.to_html(figs["rfm_segments"], full_html=False, include_plotlyjs=False)
    prod_html = pio.to_html(figs["products"], full_html=False, include_plotlyjs=False)

    table_cols = [
        "_customer",
        "RFM_Segment",
        "Recency_Days",
        "Frequency",
        "Monetary",
        "Churn_Probability",
        "Risk_Level",
        "Risk_Explanation",
    ]
    # Cap at Top 100 highest-risk accounts so HTML stays fast on 50,000-customer datasets
    clean_table = rfm_df[table_cols].head(100).copy()
    clean_table["Monetary"] = clean_table["Monetary"].map(lambda v: f"₹ {v:,.0f}")
    clean_table["Churn_Probability"] = clean_table["Churn_Probability"].map(lambda v: f"{v:.1%}")
    clean_table.columns = [
        "Customer",
        "Segment",
        "Inactive Days",
        "Orders",
        "Revenue",
        "Churn Risk %",
        "Risk Tier",
        "Explainable AI Reason",
    ]
    watchlist_html = clean_table.to_html(index=False, classes="exec-table", border=0)

    html_doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>PulseBI Executive Report — {dataset_name}</title>
    <style>
        body {{
            background-color: #0f172a;
            color: #f8fafc;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            margin: 0;
            padding: 28px;
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #334155;
            padding-bottom: 16px;
            margin-bottom: 24px;
        }}
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
            margin-bottom: 24px;
        }}
        .kpi-card {{
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 10px;
            padding: 18px;
        }}
        .kpi-label {{ color: #94a3b8; font-size: 13px; text-transform: uppercase; }}
        .kpi-val {{ font-size: 26px; font-weight: 700; margin: 6px 0; color: #38bdf8; }}
        .kpi-sub {{ font-size: 12px; color: #cbd5e1; }}
        .chart-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
            margin-bottom: 28px;
        }}
        .chart-box {{
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 10px;
            padding: 12px;
        }}
        .exec-table {{
            width: 100%;
            border-collapse: collapse;
            background: #1e293b;
            border-radius: 8px;
            overflow: hidden;
            font-size: 13px;
        }}
        .exec-table th {{
            background: #334155;
            color: #f8fafc;
            text-align: left;
            padding: 10px 12px;
        }}
        .exec-table td {{
            padding: 10px 12px;
            border-bottom: 1px solid #334155;
            color: #e2e8f0;
        }}
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1 style="margin:0; font-size:24px;">⚡ PulseBI Studio — Executive Intelligence Report</h1>
            <p style="margin:4px 0 0 0; color:#94a3b8; font-size:13px;">
                Source: <b>{dataset_name}</b> | Scrubbed {audit_report.initial_row_count:,} &rarr; {audit_report.final_row_count:,} rows | Deduplicated {audit_report.unique_entities_before:,} &rarr; {audit_report.unique_entities_after:,} entities
            </p>
        </div>
        <div style="text-align:right; color:#94a3b8; font-size:12px;">
            Generated: {generated_ts}<br> Standalone Interactive HTML
        </div>
    </div>

    <div class="kpi-grid">
        <div class="kpi-card">
            <div class="kpi-label">Total Verified Revenue</div>
            <div class="kpi-val">₹ {churn_summary.total_revenue:,.0f}</div>
            <div class="kpi-sub">{audit_report.final_row_count:,} Clean Transactions</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">At-Risk Accounts (Churn ML)</div>
            <div class="kpi-val" style="color:#f87171;">{churn_summary.at_risk_customers:,} / {churn_summary.total_customers:,}</div>
            <div class="kpi-sub">₹ {churn_summary.revenue_at_risk:,.0f} Revenue at Risk</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Next {forecast_summary.horizon_days}D Revenue Forecast</div>
            <div class="kpi-val" style="color:#34d399;">₹ {forecast_summary.forecasted_period_revenue:,.0f}</div>
            <div class="kpi-sub">{forecast_summary.expected_growth_pct:+.1f}% vs prior {forecast_summary.horizon_days}D</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Projected Daily Run-Rate</div>
            <div class="kpi-val">₹ {forecast_summary.daily_run_rate_forecast:,.0f}/day</div>
            <div class="kpi-sub">Trend R² = {forecast_summary.model_r2_score}</div>
        </div>
    </div>

    <div class="chart-grid">
        <div class="chart-box">{fcst_html}</div>
        <div class="chart-box">{pareto_html}</div>
        <div class="chart-box">{rfm_html}</div>
        <div class="chart-box">{prod_html}</div>
    </div>

    <h2 style="font-size:18px; margin-bottom:12px;">🚨 Explainable AI Customer Churn Watchlist (Top 100 Priority Accounts)</h2>
    {watchlist_html}
</body>
</html>"""
    return html_doc.encode("utf-8")