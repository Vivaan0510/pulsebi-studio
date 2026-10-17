"""
Pillar 3B UI: Interactive 'What-If' Margin, Pricing & Churn Retention Simulator
"""

import plotly.graph_objects as go
import streamlit as st

from core.forecast_engine import ForecastSummary
from core.rfm_churn_engine import ChurnModelSummary


def render_what_if_simulator(
    churn_summary: ChurnModelSummary,
    forecast_summary: ForecastSummary,
) -> None:
    """
    Allows executives to simulate the bottom-line impact of:
    1. Price adjustments (+/- %)
    2. Price elasticity volume trade-off
    3. Saving X% of At-Risk Churned Customers
    4. Gross Margin % improvements
    """
    st.subheader("🎛️ Interactive 'What-If' Executive Profit & Retention Simulator")
    st.caption(
        "Simulate how pricing changes, retention campaigns on At-Risk accounts, and COGS optimization affect projected bottom-line profit."
    )

    s1, s2, s3, s4 = st.columns(4)
    with s1:
        price_change_pct = st.slider("Price Change (%)", -15.0, 25.0, 5.0, step=0.5)
    with s2:
        churn_saved_pct = st.slider(
            "At-Risk Churn Saved (%)", 0.0, 100.0, 35.0, step=5.0
        )
    with s3:
        base_margin_pct = st.slider("Baseline Gross Margin (%)", 10.0, 80.0, 32.0, step=1.0)
    with s4:
        elasticity = st.slider(
            "Price Elasticity Factor",
            0.0,
            1.5,
            0.4,
            step=0.1,
            help="Volume drop per 1% price hike (0.4 means a 10% price hike reduces unit volume by 4%).",
        )

    # Baseline annualized revenue from historical + forecast run rate
    baseline_rev = churn_summary.total_revenue
    baseline_profit = baseline_rev * (base_margin_pct / 100.0)

    # 1. Volume effect from price change
    vol_multiplier = 1.0 - (price_change_pct / 100.0) * elasticity
    price_multiplier = 1.0 + (price_change_pct / 100.0)
    rev_after_pricing = baseline_rev * vol_multiplier * price_multiplier
    pricing_rev_delta = rev_after_pricing - baseline_rev

    # 2. Retention recovery from saving At-Risk accounts
    recovered_churn_rev = churn_summary.revenue_at_risk * (churn_saved_pct / 100.0)

    # 3. Simulated Total Revenue & New Gross Profit
    simulated_total_rev = baseline_rev + pricing_rev_delta + recovered_churn_rev
    # Price increases flow directly to gross margin above baseline COGS
    baseline_cogs = baseline_rev * (1.0 - base_margin_pct / 100.0) * vol_multiplier
    recovered_cogs = recovered_churn_rev * (1.0 - base_margin_pct / 100.0)
    simulated_profit = simulated_total_rev - (baseline_cogs + recovered_cogs)
    profit_delta = simulated_profit - baseline_profit
    profit_delta_pct = (profit_delta / max(1.0, baseline_profit)) * 100.0

    m1, m2, m3, m4 = st.columns(4)
    m1.metric(
        "Simulated Total Revenue",
        f"₹ {simulated_total_rev:,.0f}",
        f"₹ {simulated_total_rev - baseline_rev:+,.0f} vs baseline",
    )
    m2.metric(
        "Churn Revenue Rescued",
        f"₹ {recovered_churn_rev:,.0f}",
        f"From saving {churn_saved_pct:.0f}% of At-Risk accounts",
    )
    m3.metric(
        "Net Pricing Impact",
        f"₹ {pricing_rev_delta:+,.0f}",
        f"At {price_change_pct:+.1f}% price & {(vol_multiplier - 1)*100:+.1f}% volume",
    )
    m4.metric(
        "Simulated Gross Profit",
        f"₹ {simulated_profit:,.0f}",
        f"₹ {profit_delta:+,.0f} ({profit_delta_pct:+.1f}%)",
    )

    # Waterfall Chart of Revenue Bridge
    fig_wf = go.Figure(
        go.Waterfall(
            name="Revenue Bridge",
            orientation="v",
            measure=["absolute", "relative", "relative", "total"],
            x=[
                "Baseline Revenue",
                "Net Price/Volume Effect",
                "Rescued Churn Revenue",
                "Simulated Revenue",
            ],
            textposition="outside",
            text=[
                f"₹{baseline_rev/1e5:.1f}L",
                f"{pricing_rev_delta/1e5:+.1f}L",
                f"+₹{recovered_churn_rev/1e5:.1f}L",
                f"₹{simulated_total_rev/1e5:.1f}L",
            ],
            y=[
                baseline_rev,
                pricing_rev_delta,
                recovered_churn_rev,
                simulated_total_rev,
            ],
            connector={"line": {"color": "#64748b"}},
        )
    )
    fig_wf.update_layout(
        title="🌉 Executive What-If Revenue Bridge (INR in Lakhs)",
        template="plotly_dark",
        height=340,
        margin=dict(l=20, r=20, t=50, b=20),
    )
    st.plotly_chart(fig_wf, use_container_width=True)