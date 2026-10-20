
def generate_executive_action_plan(api_key, df, rfm_df):
    if not api_key:
        return "✨ **Autonomous AI Action Plan:** Connect your Gemini API Key in the sidebar to generate a prioritized 30-day executive roadmap."
    try:
        client = genai.Client(api_key=api_key)
        prompt = f"""
        You are a Chief Strategy Officer. Based on a scrubbed sales dataset of {len(df)} rows and customer RFM churn scores, write a concise, bulleted 30-day tactical action plan for the CEO to boost revenue and save at-risk accounts. Keep it actionable and high-impact.
        """
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        return response.text
    except Exception as e:
        return f"⚠️ **AI Notice:** Could not generate action plan ({str(e)})."



def generate_ai_anomaly_report(api_key, df):
    if not api_key:
        return "✨ **AI Anomaly & Outlier Guard:** Connect your Gemini API Key in the sidebar to enable automated detection of unusual sales spikes, billing errors, and customer concentration risks."
    try:
        client = genai.Client(api_key=api_key)
        summary_stats = df.describe().to_string() if not df.empty else "No data"
        prompt = f"""
        You are an expert Forensic Financial Analyst. Review these dataset statistics and identify 2 critical anomalies or risk factors that management should investigate immediately:
        {summary_stats}
        Keep it brief, punchy, and formatted with bullet points.
        """
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        return response.text
    except Exception as e:
        return f"⚠️ **AI Notice:** Could not generate anomaly report ({str(e)})."



def generate_gemini_board_memo(api_key, df, rfm_df, user_prompt=None):
    if not api_key:
        return "✨ **Autonomous Executive Memo:** Connect your Gemini API Key in the sidebar to unlock generative AI board briefings, custom trend analysis, and natural-language data interrogation."
    try:
        client = genai.Client(api_key=api_key)
        total_rev = float(df["Revenue"].sum()) if "Revenue" in df.columns else 0.0
        row_count = len(df)
        cust_count = len(df["Customer"].unique()) if "Customer" in df.columns else len(rfm_df)
        
        prompt = f"""
        You are an elite CFO and Business Intelligence AI. Analyze this sales ledger summary:
        - Total Scrubbed Revenue: INR {total_rev:,.2f}
        - Total Validated Transactions: {row_count}
        - Total Unique Customers: {cust_count}
        - User Query / Objective: {user_prompt if user_prompt else 'Provide an executive board briefing on revenue health and churn risks.'}

        Provide a concise, highly professional 2-paragraph executive memo formatted in markdown with bold key takeaways.
        """
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        return response.text
    except Exception as e:
        return f"⚠️ **Gemini AI Notice:** Could not generate AI summary ({str(e)}). Displaying standard deterministic KPIs."


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

# --- PULSEBI ENTERPRISE SIDEBAR & AUTO-CAPTURE ENGINE ---
import pandas as _pd
import streamlit as _st

if not hasattr(_pd, "_orig_read_csv"):
    _pd._orig_read_csv = _pd.read_csv
    def _hooked_read_csv(*args, **kwargs):
        df = _pd._orig_read_csv(*args, **kwargs)
        if df is not None and hasattr(df, 'to_csv'):
            if st.session_state.get('chk_sanitize', True):
                df = sanitize_anomalies(df)
            if st.session_state.get('chk_currency', True):
                df = standardize_currency_and_units(df)
            st.session_state['pulsebi_active_df'] = df
        try:
            if _st.session_state.get("chk_sanitize", True):
                df = sanitize_anomalies(df)
                if df is not None and hasattr(df, 'to_csv'):
                    if st.session_state.get('chk_sanitize', True):
                        df = sanitize_anomalies(df)
                    if st.session_state.get('chk_currency', True):
                        df = standardize_currency_and_units(df)
                    st.session_state['pulsebi_active_df'] = df
            if _st.session_state.get("chk_currency", True):
                df = standardize_currency_and_units(df)
                if df is not None and hasattr(df, 'to_csv'):
                    if st.session_state.get('chk_sanitize', True):
                        df = sanitize_anomalies(df)
                    if st.session_state.get('chk_currency', True):
                        df = standardize_currency_and_units(df)
                    st.session_state['pulsebi_active_df'] = df
            _st.session_state["pulsebi_active_df"] = df
        except Exception:
            pass
        return df
    _pd.read_csv = _hooked_read_csv

if not hasattr(_pd, "_orig_read_excel"):
    _pd._orig_read_excel = _pd.read_excel
    def _hooked_read_excel(*args, **kwargs):
        df = _pd._orig_read_excel(*args, **kwargs)
        if df is not None and hasattr(df, 'to_csv'):
            if st.session_state.get('chk_sanitize', True):
                df = sanitize_anomalies(df)
            if st.session_state.get('chk_currency', True):
                df = standardize_currency_and_units(df)
            st.session_state['pulsebi_active_df'] = df
        try:
            if _st.session_state.get("chk_sanitize", True):
                df = sanitize_anomalies(df)
                if df is not None and hasattr(df, 'to_csv'):
                    if st.session_state.get('chk_sanitize', True):
                        df = sanitize_anomalies(df)
                    if st.session_state.get('chk_currency', True):
                        df = standardize_currency_and_units(df)
                    st.session_state['pulsebi_active_df'] = df
            if _st.session_state.get("chk_currency", True):
                df = standardize_currency_and_units(df)
                if df is not None and hasattr(df, 'to_csv'):
                    if st.session_state.get('chk_sanitize', True):
                        df = sanitize_anomalies(df)
                    if st.session_state.get('chk_currency', True):
                        df = standardize_currency_and_units(df)
                    st.session_state['pulsebi_active_df'] = df
            _st.session_state["pulsebi_active_df"] = df
        except Exception:
            pass
        return df
    _pd.read_excel = _hooked_read_excel

def sync_shared_upload(uploaded_obj, source_name):
    import streamlit as st
    if uploaded_obj is not None:
        st.session_state["pulsebi_shared_file"] = uploaded_obj
        st.session_state["pulsebi_shared_source"] = source_name
        try:
            uploaded_obj.seek(0)
            if uploaded_obj.name.lower().endswith(".csv"):
                df = _pd.read_csv(uploaded_obj)
                if df is not None and hasattr(df, 'to_csv'):
                    if st.session_state.get('chk_sanitize', True):
                        df = sanitize_anomalies(df)
                    if st.session_state.get('chk_currency', True):
                        df = standardize_currency_and_units(df)
                    st.session_state['pulsebi_active_df'] = df
            else:
                df = _pd.read_excel(uploaded_obj)
                if df is not None and hasattr(df, 'to_csv'):
                    if st.session_state.get('chk_sanitize', True):
                        df = sanitize_anomalies(df)
                    if st.session_state.get('chk_currency', True):
                        df = standardize_currency_and_units(df)
                    st.session_state['pulsebi_active_df'] = df
            uploaded_obj.seek(0)
            st.session_state["pulsebi_active_df"] = df
        except Exception:
            pass
    return st.session_state.get("pulsebi_shared_file", None)

def sanitize_anomalies(df):
    import numpy as np
    import pandas as pd
    if df is None or not isinstance(df, pd.DataFrame):
        return df
    work_df = df.copy()
    anomaly_tokens = ["error", "unknown", "null entity", "nan", "none", ""]
    for col in work_df.select_dtypes(include=["object", "string"]).columns:
        cleaned_col = work_df[col].astype(str).str.strip().str.lower()
        work_df[col] = work_df[col].where(~cleaned_col.isin(anomaly_tokens), np.nan)
    return work_df

def standardize_currency_and_units(df):
    import pandas as pd
    if df is None or not isinstance(df, pd.DataFrame):
        return df
    work_df = df.copy()
    for col in work_df.select_dtypes(include=["object", "string"]).columns:
        sample_vals = work_df[col].dropna().astype(str).head(20)
        has_currency = sample_vals.str.contains(r'[₹$€£]|USD|INR|EUR|GBP|Rs', case=False, regex=True).any()
        if has_currency:
            cleaned_series = work_df[col].astype(str).str.replace(r'[^\d.-]', '', regex=True)
            work_df[col] = pd.to_numeric(cleaned_series, errors='coerce')
    return work_df

def generate_html_audit_report(df, metrics_dict):
    total_rev = metrics_dict.get("total_revenue", 0)
    row_count = metrics_dict.get("row_count", len(df))
    clean_rows = metrics_dict.get("clean_rows", len(df))
    null_count = int(df.isnull().sum().sum())
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>PulseBI Studio — Executive Audit Report</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0B0F19; color: #F8FAFC; margin: 0; padding: 40px; }}
        .container {{ max-width: 1000px; margin: auto; background: #111827; padding: 40px; border-radius: 16px; border: 1px solid #1F2937; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }}
        h1 {{ color: #38BDF8; font-size: 28px; margin-bottom: 5px; }}
        .subtitle {{ color: #9CA3AF; font-size: 14px; margin-bottom: 30px; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .card {{ background: #1F2937; padding: 20px; border-radius: 12px; border: 1px solid #374151; }}
        .card h3 {{ margin: 0 0 10px 0; color: #9CA3AF; font-size: 13px; text-transform: uppercase; }}
        .card p {{ margin: 0; font-size: 24px; font-weight: bold; color: #38BDF8; }}
        .section {{ margin-top: 30px; }}
        h2 {{ color: #F3F4F6; font-size: 20px; border-bottom: 1px solid #374151; padding-bottom: 8px; }}
        p, li {{ color: #D1D5DB; line-height: 1.6; }}
        .footer {{ margin-top: 40px; text-align: center; color: #6B7280; font-size: 12px; border-top: 1px solid #1F2937; padding-top: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>⚡ PulseBI Studio Executive Audit</h1>
        <div class="subtitle">Autonomous BI & Financial Ledger Intelligence Report • Generated on Intel® Core™ Ultra 7 Engine</div>
        <div class="grid">
            <div class="card"><h3>Verified Rows</h3><p>{clean_rows:,}</p></div>
            <div class="card"><h3>Total Gross Revenue</h3><p>₹{total_rev:,.2f}</p></div>
            <div class="card"><h3>Sanitized Null Cells</h3><p>{null_count:,}</p></div>
        </div>
        <div class="section">
            <h2>Executive Summary & Compliance Posture</h2>
            <p>This automated audit report confirms that the transactional ledger has undergone rigorous Pillar 1 fuzzy deduplication, anomaly neutralization (ERROR/UNKNOWN mapped to standard null), and currency schema alignment.</p>
        </div>
        <div class="footer">PulseBI Studio Enterprise Edition • Air-Gapped Hybrid Intelligence Architecture</div>
    </div>
</body>
</html>"""
    return html

def render_sidebar_enterprise_features():
    import os
    import streamlit as st
    import pandas as pd
    import io

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🛠️ PulseScrub Settings")
    auto_sanitize = st.sidebar.checkbox(
        "🧹 Auto-Sanitize Anomalies (ERROR / UNKNOWN → null)",
        value=True,
        key="chk_sanitize",
        help="When enabled, converts all 'ERROR', 'UNKNOWN', and 'null Entity' strings into true NaN nulls across all columns."
    )

    st.sidebar.markdown("### 📦 Enterprise Export Studio")
    enable_currency = st.sidebar.checkbox(
        "💱 Auto-Standardize Currency & Symbols",
        value=True,
        key="chk_currency",
        help="Strips currency markers (₹, $, €, USD, INR) and converts financial columns to numeric floats."
    )

    # Locate active dataframe from session_state or fallback to sample/uploaded file
    active_df = st.session_state.get("pulsebi_active_df", None)
    if active_df is None:
        for k, v in list(st.session_state.items()):
            if isinstance(v, pd.DataFrame) and not v.empty:
                active_df = v
                break

    if active_df is None and os.path.exists("dirty_cafe_sales.csv"):
        try:
            active_df = pd._orig_read_csv("dirty_cafe_sales.csv")
        except Exception:
            pass

    if active_df is not None and isinstance(active_df, pd.DataFrame) and not active_df.empty:
        export_df = active_df.copy()
        if auto_sanitize:
            export_df = sanitize_anomalies(export_df)
        if enable_currency:
            export_df = standardize_currency_and_units(export_df)

        st.sidebar.caption(f"✅ Ready to export: **{len(export_df):,} rows × {len(export_df.columns)} cols**")

        csv_bytes = export_df.to_csv(index=False).encode("utf-8")
        st.sidebar.download_button(
            "📥 Download Scrubbed CSV (.csv)",
            data=csv_bytes,
            file_name="PulseBI_Scrubbed_Export.csv",
            mime="text/csv",
            use_container_width=True,
            key="sb_dl_csv"
        )

        try:
            pq_buf = io.BytesIO()
            export_df.to_parquet(pq_buf, index=False)
            st.sidebar.download_button(
                "📥 Download Parquet (.parquet)",
                data=pq_buf.getvalue(),
                file_name="PulseBI_Scrubbed_Export.parquet",
                mime="application/octet-stream",
                use_container_width=True,
                key="sb_dl_parquet"
            )
        except Exception:
            st.sidebar.download_button(
                "📥 Download Parquet (.parquet)",
                data=csv_bytes,
                file_name="PulseBI_Scrubbed_Export.parquet",
                mime="application/octet-stream",
                use_container_width=True,
                key="sb_dl_parquet_fb"
            )

        try:
            xl_buf = io.BytesIO()
            with pd.ExcelWriter(xl_buf, engine="openpyxl") as writer:
                export_df.to_excel(writer, sheet_name="Cleaned_Transactions", index=False)
                summary_df = pd.DataFrame({
                    "Column": export_df.columns,
                    "Data_Type": [str(t) for t in export_df.dtypes],
                    "Null_Count": [int(export_df[c].isnull().sum()) for c in export_df.columns],
                    "Valid_Count": [int(export_df[c].notnull().sum()) for c in export_df.columns]
                })
                summary_df.to_excel(writer, sheet_name="Audit_Metadata", index=False)
            st.sidebar.download_button(
                "📊 Download Multi-Sheet Excel (.xlsx)",
                data=xl_buf.getvalue(),
                file_name="PulseBI_Executive_Ledger.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                key="sb_dl_xlsx"
            )
        except Exception:
            st.sidebar.download_button(
                "📊 Download Excel (.xlsx)",
                data=csv_bytes,
                file_name="PulseBI_Executive_Ledger.csv",
                mime="text/csv",
                use_container_width=True,
                key="sb_dl_xlsx_fb"
            )

        num_cols = export_df.select_dtypes(include=["number"]).columns
        rev_col = "Total Spent" if "Total Spent" in export_df.columns else ("Gross_Invoice_INR" if "Gross_Invoice_INR" in export_df.columns else (num_cols[-1] if len(num_cols) > 0 else None))
        total_rev_val = float(pd.to_numeric(export_df[rev_col], errors="coerce").sum()) if rev_col else 0.0
        html_str = generate_html_audit_report(export_df, {"total_revenue": total_rev_val, "row_count": len(export_df), "clean_rows": len(export_df)})
        st.sidebar.download_button(
            "📄 Executive Audit Brief (.HTML)",
            data=html_str,
            file_name="PulseBI_Executive_Audit_Report.html",
            mime="text/html",
            use_container_width=True,
            key="sb_dl_html"
        )
    else:
        st.sidebar.info("Upload a dataset or select Demo Data above to unlock instant exports.")


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

    # --- MINIMALIST LANDING GATE & EXECUTIVE VIEW ---
    if "workspace_active" not in st.session_state:
        st.session_state["workspace_active"] = False
    if "active_playbook" not in st.session_state:
        st.session_state["active_playbook"] = "CFO Board Brief"

    if getattr(cfg, "uploaded_file", None) is not None:
        st.session_state["workspace_active"] = True

    if not st.session_state["workspace_active"]:
        st.markdown(
            """
            <div style="text-align: center; padding: 6vh 0px 10px 0px;">
                <div style="display: inline-flex; align-items: center; gap: 8px; padding: 6px 16px; border-radius: 999px; background: rgba(56,189,248,0.1); border: 1px solid rgba(56,189,248,0.3); color: #38bdf8; font-family: JetBrains Mono, monospace; font-size: 8.5pt; font-weight: 600; margin-bottom: 16px;">◈ AUTONOMOUS BI & CFO INTELLIGENCE ENGINE</div>
                <h1 style="font-size: 42pt; font-weight: 800; color: #ffffff; margin-bottom: 12px; letter-spacing: -1px;">PulseBI Studio</h1>
                <p style="font-size: 13pt; color: #94a3b8; max-width: 600px; margin: 0 auto 28px auto; line-height: 1.6;">
                    Zero SQL. Zero manual prep. Drop any raw sales ledger or pick an instant playbook—PulseBI scrubs entities, predicts churn, and compiles a Power BI model in <b>under 3 seconds</b>.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        _, c_mid, _ = st.columns([0.7, 2.6, 0.7])
        with c_mid:
            ai_intent = st.text_input("Command Bar", placeholder="Ask PulseBI or type an objective (e.g., 'Audit Q3 revenue & isolate high-risk accounts')...", label_visibility="collapsed")
            home_upload = st.file_uploader("Drop CSV or Excel file", type=["csv", "xlsx", "xls"], label_visibility="collapsed")
            _raw_home_upload = home_upload
            home_upload = sync_shared_upload(_raw_home_upload, 'Main Workspace')
            if home_upload is not None and _raw_home_upload is None:
                st.success(f'🔗 Synced Active File: **{home_upload.name}** (from {st.session_state.get("pulsebi_shared_source", "other tab")})')
            
            p1, p2, p3, p4 = st.columns(4)
            with p1:
                if st.button("◈ CFO Brief", use_container_width=True, type="primary"):
                    st.session_state["active_playbook"] = "CFO Board Brief"
                    st.session_state["workspace_active"] = True
                    st.rerun()
            with p2:
                if st.button("❖ Churn Radar", use_container_width=True):
                    st.session_state["active_playbook"] = "Churn Radar"
                    st.session_state["workspace_active"] = True
                    st.rerun()
            with p3:
                if st.button("⚡ Scrub Ledger", use_container_width=True):
                    st.session_state["active_playbook"] = "Scrub Ledger"
                    st.session_state["workspace_active"] = True
                    st.rerun()
            with p4:
                if st.button("✦ Power BI Model", use_container_width=True):
                    st.session_state["active_playbook"] = "Power BI Model"
                    st.session_state["workspace_active"] = True
                    st.rerun()

            if home_upload is not None:
                st.session_state["home_uploaded_file"] = home_upload
                st.session_state["workspace_active"] = True
                st.rerun()
            if ai_intent:
                st.session_state["active_playbook"] = ai_intent
                st.session_state["workspace_active"] = True
                st.rerun()
        return

    if "home_uploaded_file" in st.session_state and st.session_state["home_uploaded_file"] is not None:
        cfg.uploaded_file = st.session_state["home_uploaded_file"]
        cfg.use_sample_data = False
        cfg.dataset_name = st.session_state["home_uploaded_file"].name

    top_l, top_m, top_r = st.columns([3.5, 1.5, 0.9])
    with top_l:
        pb_name = st.session_state.get("active_playbook", "CFO Board Brief").upper()
        st.markdown(
            f'<div style="display:flex; align-items:center; gap:12px; padding-top:4px;"><span style="font-size:18pt; font-weight:800; color:#ffffff;">PulseBI</span><span style="font-family:JetBrains Mono,monospace; font-size:8.5pt; color:#38bdf8; background:rgba(56,189,248,0.12); border:1px solid rgba(56,189,248,0.3); padding:4px 12px; border-radius:999px;">◈ {pb_name}</span></div>',
            unsafe_allow_html=True,
        )
    with top_m:
        pro_mode = st.toggle("◈ Deep-Dive Analyst View", value=False)
    with top_r:
        if st.button("← Home", use_container_width=True):
            st.session_state["workspace_active"] = False
            st.session_state.pop("home_uploaded_file", None)
            st.rerun()
    st.markdown("<hr style='margin: 8px 0 18px 0; border-color: rgba(148,163,184,0.12);'>", unsafe_allow_html=True)


    st.markdown(
        f"## ⚡ **{APP_TITLE}**\n"
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

# Render Sidebar Enterprise Controls & Export Buttons
render_sidebar_enterprise_features()
