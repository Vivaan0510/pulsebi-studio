"""
PulseBI Studio — Main Streamlit Application Entry Point
End-to-End Automated Data Prep, Predictive Business Modelling & Power BI Star-Schema Suite.
Includes @st.cache_data pipeline caching + Interactive Manual Schema Override.
"""

from typing import Dict, Optional, Tuple
import pandas as pd
import streamlit as st

from config.settings import APP_TITLE, APP_VERSION
from core.data_scrubber import ScrubAuditReport, normalize_raw_dataframe, scrub_dataset
from core.forecast_engine import ForecastSummary, run_revenue_forecast
from core.rfm_churn_engine import ChurnModelSummary, run_rfm_and_churn_pipeline
from core.schema_mapper import auto_map_schema, gemini_assist_schema_map
from core.star_schema_compiler import (
    compile_star_schema,
    export_star_schema_excel,
    export_star_schema_zip,
)
from ui.etl_audit_view import render_etl_audit_view
from ui.executive_dashboard import render_executive_dashboard
from ui.html_exporter import compile_standalone_html_dashboard
from ui.sidebar import render_sidebar
from ui.what_if_simulator import render_what_if_simulator


@st.cache_data(show_spinner="⚡ Running PulseScrub ETL & RapidFuzz Entity Deduplication...")
def cached_scrub_pipeline(
    raw_df: pd.DataFrame,
    schema_map: Dict[str, Optional[str]],
    fuzzy_threshold: int,
) -> Tuple[pd.DataFrame, ScrubAuditReport]:
    """Cached wrapper around scrub_dataset so UI slider tweaks don't re-run ETL unnecessarily."""
    return scrub_dataset(raw_df, schema_map=schema_map, fuzzy_threshold=fuzzy_threshold)


@st.cache_data(show_spinner="🧠 Training Explainable Churn ML & Seasonal Forecast Models...")
def cached_ml_pipelines(
    clean_df: pd.DataFrame,
    ml_model_choice: str,
    inactivity_days: int,
    forecast_horizon: int,
) -> Tuple[pd.DataFrame, ChurnModelSummary, pd.DataFrame, ForecastSummary]:
    """Cached wrapper around RFM Churn and Revenue Forecast engines."""
    rfm_df, churn_summary = run_rfm_and_churn_pipeline(
        clean_df,
        model_choice=ml_model_choice,
        inactivity_threshold_days=inactivity_days,
    )
    ts_df, forecast_summary = run_revenue_forecast(
        clean_df,
        horizon_days=forecast_horizon,
    )
    return rfm_df, churn_summary, ts_df, forecast_summary


def main() -> None:
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon="⚡",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    cfg = render_sidebar()

    st.markdown(
        f"## ⚡ **{APP_TITLE}** `v{APP_VERSION}`\n"
        "Automated Dirty Excel/CSV Scrubber • Explainable RFM Churn ML • 90-Day Revenue Forecasting • Power BI Star-Schema & DAX Compiler"
    )

    if cfg.raw_df is None or len(cfg.raw_df) == 0:
        st.info("👈 Please select the Demo Dataset or upload a CSV/Excel file from the sidebar to begin.")
        return

    # Normalize buried header rows first so column names are clean for mapping
    norm_raw_df = normalize_raw_dataframe(cfg.raw_df)

    # 1. Auto-Detect Schema Mapping
    if cfg.gemini_api_key:
        auto_schema = gemini_assist_schema_map(norm_raw_df, cfg.gemini_api_key)
    else:
        auto_schema = auto_map_schema(norm_raw_df)

    # 2. Interactive Manual Schema Mapping Override (Handles any custom corporate ERP schema)
    col_options = ["(None / Auto-Fallback)"] + list(norm_raw_df.columns)
    schema_map: Dict[str, Optional[str]] = {}

    with st.expander("🧭 Universal Schema Mapper (Auto-Detected — Click to Override Any Column)", expanded=False):
        st.caption(
            "PulseBI automatically maps your headers using heuristics & data-type profiling. You can manually remap any role below:"
        )
        m_cols = st.columns(5)
        roles = [
            ("date", "📅 Date Column"),
            ("customer", "🏢 Customer / Party"),
            ("product", "📦 Product / Item"),
            ("quantity", "🔢 Quantity"),
            ("revenue", "💰 Revenue / Amount"),
        ]
        for idx, (role_key, role_label) in enumerate(roles):
            detected_val = auto_schema.get(role_key)
            default_idx = (
                col_options.index(detected_val)
                if detected_val in col_options
                else 0
            )
            with m_cols[idx]:
                chosen = st.selectbox(
                    role_label,
                    options=col_options,
                    index=default_idx,
                    key=f"schema_override_{cfg.dataset_name}_{role_key}",
                )
                schema_map[role_key] = None if chosen == "(None / Auto-Fallback)" else chosen

    # 3. Execute Cached ETL & ML Pipelines
    clean_df, audit_report = cached_scrub_pipeline(
        norm_raw_df,
        schema_map=schema_map,
        fuzzy_threshold=cfg.fuzzy_threshold,
    )

    rfm_df, churn_summary, ts_df, forecast_summary = cached_ml_pipelines(
        clean_df,
        ml_model_choice=cfg.ml_model_choice,
        inactivity_days=cfg.inactivity_days,
        forecast_horizon=cfg.forecast_horizon,
    )

    # 4. Organize Workspace Tabs dynamically based on Sidebar Pillar toggles
    tab_labels = ["🧹 Pillar 1: ETL & Fuzzy Audit (PulseScrub)"]
    if cfg.enable_exec_dashboard:
        tab_labels.append("📊 Pillar 2 & 3: Executive Dashboard & What-If Simulator")
    if cfg.enable_star_compiler:
        tab_labels.append("⭐ Pillar 4: Power BI Star-Schema & DAX Compiler (PulseStar)")

    tabs = st.tabs(tab_labels)
    tab_idx = 0

    # --- TAB 1: ETL & FUZZY AUDIT ---
    with tabs[tab_idx]:
        render_etl_audit_view(norm_raw_df, clean_df, schema_map, audit_report)
    tab_idx += 1

    # --- TAB 2: EXECUTIVE DASHBOARD, WHAT-IF SIMULATOR & HTML EXPORT ---
    if cfg.enable_exec_dashboard:
        with tabs[tab_idx]:
            figs = render_executive_dashboard(
                clean_df, rfm_df, ts_df, churn_summary, forecast_summary
            )
            st.divider()
            render_what_if_simulator(churn_summary, forecast_summary)
            st.divider()

            html_bytes = compile_standalone_html_dashboard(
                dataset_name=cfg.dataset_name,
                audit_report=audit_report,
                churn_summary=churn_summary,
                forecast_summary=forecast_summary,
                figs=figs,
                rfm_df=rfm_df,
            )
            st.download_button(
                label="🌐 1-Click Export Standalone Interactive HTML Dashboard (Offline Shareable)",
                data=html_bytes,
                file_name=f"PulseBI_Executive_Report_{cfg.dataset_name.split('.')[0]}.html",
                mime="text/html",
                type="primary",
            )
        tab_idx += 1

    # --- TAB 3: POWER BI STAR-SCHEMA & DAX / M COMPILER ---
    if cfg.enable_star_compiler:
        with tabs[tab_idx]:
            st.subheader("⭐ Pillar 4: Automated Power BI Star-Schema & DAX Compiler (PulseStar)")
            st.caption(
                "Automatically normalizes flat transactions into a Kimball Star Schema with Indian Financial Year (Apr–Mar) support and ready-to-paste DAX + Power Query (M) scripts."
            )

            bundle = compile_star_schema(clean_df, rfm_df, schema_map)

            s1, s2, s3, s4 = st.columns(4)
            s1.metric("Fact_Transactions", f"{len(bundle.fact_transactions):,} rows", "Surrogate Keys Linked")
            s2.metric("Dim_Customers", f"{len(bundle.dim_customers):,} entities", "Enriched w/ RFM & Churn ML")
            s3.metric("Dim_Products", f"{len(bundle.dim_products):,} SKUs", "With Unit Price & Share %")
            s4.metric("Dim_Calendar (Indian FY)", f"{len(bundle.dim_calendar):,} days", "Apr–Mar FY & FQ1–FQ4 Ready")

            dl_col1, dl_col2 = st.columns(2)
            with dl_col1:
                zip_bytes = export_star_schema_zip(bundle)
                st.download_button(
                    label="📦 Download Complete Power BI Star-Schema Bundle (.ZIP: 4 CSVs + .DAX + .PQ)",
                    data=zip_bytes,
                    file_name="PulseBI_StarSchema_PowerBI_Bundle.zip",
                    mime="application/zip",
                    type="primary",
                )
            with dl_col2:
                xlsx_bytes = export_star_schema_excel(bundle)
                st.download_button(
                    label="📗 Download Multi-Sheet Star-Schema Workbook (.XLSX)",
                    data=xlsx_bytes,
                    file_name="PulseBI_StarSchema_Workbook.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )

            with st.expander("🗂️ Preview Normalized Star-Schema Tables (Fact & Dimensions)", expanded=True):
                t_fact, t_cust, t_prod, t_cal = st.tabs(
                    ["Fact_Transactions", "Dim_Customers", "Dim_Products", "Dim_Calendar (Indian FY)"]
                )
                with t_fact:
                    st.dataframe(bundle.fact_transactions.head(50), use_container_width=True, hide_index=True)
                with t_cust:
                    st.dataframe(bundle.dim_customers.head(100), use_container_width=True, hide_index=True)
                with t_prod:
                    st.dataframe(bundle.dim_products.head(100), use_container_width=True, hide_index=True)
                with t_cal:
                    st.dataframe(bundle.dim_calendar.head(50), use_container_width=True, hide_index=True)

            code_col1, code_col2 = st.columns(2)
            with code_col1:
                st.markdown("#### 📐 Auto-Generated Power BI DAX Measures (`.dax`)")
                st.code(bundle.dax_measures_code, language="dax")
            with code_col2:
                st.markdown("#### ⚙️ Auto-Generated Power Query Script (`.pq` / `M`)")
                st.code(bundle.power_query_m_code, language="powerquery")


if __name__ == "__main__":
    main()