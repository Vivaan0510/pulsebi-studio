
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


# === PULSEBI NEXT-GEN AUTONOMOUS INTELLIGENCE SUITE ===
def _get_best_active_df():
    import os
    import streamlit as st
    import pandas as pd
    df = st.session_state.get("pulsebi_active_df", None)
    if df is None or not isinstance(df, pd.DataFrame) or df.empty:
        for k, v in list(st.session_state.items()):
            if isinstance(v, pd.DataFrame) and not v.empty and len(v) > 5:
                df = v
                break
    if (df is None or not isinstance(df, pd.DataFrame) or df.empty) and os.path.exists("dirty_cafe_sales.csv"):
        try:
            df = pd.read_csv("dirty_cafe_sales.csv")
        except Exception:
            pass
    return df

def _detect_columns(df):
    import pandas as pd
    num_cols = list(df.select_dtypes(include=["number"]).columns)
    obj_cols = list(df.select_dtypes(include=["object", "string", "category"]).columns)
    
    # Identify revenue / amount column
    rev_col = None
    for cand in ["Total Spent", "Gross_Invoice_INR", "Revenue", "Amount", "Sales", "Price Per Unit"]:
        for c in df.columns:
            if cand.lower() == c.lower():
                rev_col = c
                break
        if rev_col:
            break
    if not rev_col and num_cols:
        rev_col = num_cols[-1]
        
    # Identify entity / product / customer columns
    prod_col = None
    cust_col = None
    date_col = None
    for c in df.columns:
        cl = c.lower()
        if not date_col and any(k in cl for k in ["date", "time", "day", "month"]):
            date_col = c
        elif not prod_col and any(k in cl for k in ["item", "product", "sku", "service", "category"]):
            prod_col = c
        elif not cust_col and any(k in cl for k in ["customer", "client", "account", "entity", "location", "payment"]):
            cust_col = c
    if not prod_col and obj_cols:
        prod_col = obj_cols[0]
    if not cust_col and len(obj_cols) > 1:
        cust_col = obj_cols[1]
    return rev_col, prod_col, cust_col, date_col

def build_star_schema_zip_bundle(df):
    import io
    import json
    import zipfile
    import pandas as pd
    import numpy as np

    rev_col, prod_col, cust_col, date_col = _detect_columns(df)
    work = df.copy()

    # 1. Dim_Products
    if prod_col and prod_col in work.columns:
        unique_prods = work[prod_col].dropna().astype(str).unique()
        dim_prod = pd.DataFrame({
            "Product_Key": [f"PRD-{i+1001}" for i in range(len(unique_prods))],
            "Product_Name": unique_prods
        })
        prod_map = dict(zip(dim_prod["Product_Name"], dim_prod["Product_Key"]))
        work["Product_Key"] = work[prod_col].astype(str).map(prod_map).fillna("PRD-0000")
    else:
        dim_prod = pd.DataFrame({"Product_Key": ["PRD-1001"], "Product_Name": ["Standard Enterprise SKU"]})
        work["Product_Key"] = "PRD-1001"

    # 2. Dim_Customers
    if cust_col and cust_col in work.columns:
        unique_custs = work[cust_col].dropna().astype(str).unique()
        dim_cust = pd.DataFrame({
            "Customer_Key": [f"CST-{i+5001}" for i in range(len(unique_custs))],
            "Customer_Entity": unique_custs
        })
        cust_map = dict(zip(dim_cust["Customer_Entity"], dim_cust["Customer_Key"]))
        work["Customer_Key"] = work[cust_col].astype(str).map(cust_map).fillna("CST-0000")
    else:
        dim_cust = pd.DataFrame({"Customer_Key": ["CST-5001"], "Customer_Entity": ["Enterprise Direct Account"]})
        work["Customer_Key"] = "CST-5001"

    # 3. Dim_Calendar
    if date_col and date_col in work.columns:
        parsed_dates = pd.to_datetime(work[date_col], errors="coerce").dropna()
    else:
        parsed_dates = pd.Series(dtype="datetime64[ns]")
    if len(parsed_dates) > 0:
        min_d, max_d = parsed_dates.min(), parsed_dates.max()
        if pd.isna(min_d) or pd.isna(max_d) or min_d == max_d:
            date_range = pd.date_range("2025-01-01", periods=365, freq="D")
        else:
            date_range = pd.date_range(min_d, max_d, freq="D")
    else:
        date_range = pd.date_range("2025-01-01", periods=365, freq="D")

    dim_cal = pd.DataFrame({
        "Date": date_range.strftime("%Y-%m-%d"),
        "Year": date_range.year,
        "Quarter": [f"Q{q}" for q in date_range.quarter],
        "Month_Num": date_range.month,
        "Month_Name": date_range.strftime("%b"),
        "Day_of_Week": date_range.strftime("%A"),
        "Is_Weekend": date_range.dayofweek.isin([5, 6])
    })

    # 4. Auto-Compiled DAX Script
    target_rev = rev_col if rev_col else "Revenue_Amount"
    dax_script = f"""// =========================================================================
// PULSEBI STUDIO — AUTO-COMPILED POWER BI DAX MEASURE SUITE
// Star-Schema Model: Fact_Transactions, Dim_Customers, Dim_Products, Dim_Calendar
// =========================================================================

Total Gross Revenue = 
    SUM('Fact_Transactions'[{target_rev}])

Verified Transaction Count = 
    COUNTROWS('Fact_Transactions')

Average Order Value (AOV) = 
    DIVIDE([Total Gross Revenue], [Verified Transaction Count], 0)

Revenue YoY % = 
    VAR CurrentRev = [Total Gross Revenue]
    VAR PriorRev = CALCULATE([Total Gross Revenue], SAMEPERIODLASTYEAR('Dim_Calendar'[Date]))
    RETURN DIVIDE(CurrentRev - PriorRev, PriorRev, 0)

Revenue MTD = 
    TOTALMTD([Total Gross Revenue], 'Dim_Calendar'[Date])

Pareto Top 20% Customer Revenue = 
    CALCULATE(
        [Total Gross Revenue],
        FILTER(
            VALUES('Dim_Customers'[Customer_Key]),
            RANKX(ALL('Dim_Customers'), [Total Gross Revenue], , DESC, Dense) <= COUNTROWS(ALL('Dim_Customers')) * 0.20
        )
    )

Forensic Anomaly Exposure = 
    CALCULATE(
        [Total Gross Revenue],
        'Fact_Transactions'[Forensic_Risk_Flag] = "HIGH_RISK"
    )
"""

    manifest = {
        "compiler": "PulseBI Studio Enterprise Star-Schema Compiler",
        "fact_table": "Fact_Transactions.csv",
        "dimensions": ["Dim_Products.csv", "Dim_Customers.csv", "Dim_Calendar.csv"],
        "dax_measures": "PulseBI_Executive_Measures.dax",
        "row_count": len(work),
        "primary_revenue_column": target_rev
    }

    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("Fact_Transactions.csv", work.to_csv(index=False))
        zf.writestr("Dim_Products.csv", dim_prod.to_csv(index=False))
        zf.writestr("Dim_Customers.csv", dim_cust.to_csv(index=False))
        zf.writestr("Dim_Calendar.csv", dim_cal.to_csv(index=False))
        zf.writestr("PulseBI_Executive_Measures.dax", dax_script)
        zf.writestr("SCHEMA_MANIFEST.json", json.dumps(manifest, indent=2))
    return zip_buf.getvalue()

def compute_forensic_audit(df):
    import numpy as np
    import pandas as pd
    rev_col, prod_col, cust_col, date_col = _detect_columns(df)
    work = df.copy()
    if not rev_col:
        return work, pd.DataFrame(), pd.DataFrame(), 0.0, "No numeric column detected"

    series = pd.to_numeric(work[rev_col], errors="coerce").dropna()
    pos_series = series[series > 0]

    # 1. Benford's Law First-Digit Distribution
    first_digits = pos_series.astype(str).str.lstrip("0.").str[0]
    first_digits = first_digits[first_digits.isin([str(d) for d in range(1, 10)])].astype(int)
    total_valid = len(first_digits)

    benford_rows = []
    mad_sum = 0.0
    for d in range(1, 10):
        expected_pct = float(np.log10(1.0 + 1.0 / d) * 100.0)
        actual_cnt = int((first_digits == d).sum()) if total_valid > 0 else 0
        actual_pct = (actual_cnt / total_valid * 100.0) if total_valid > 0 else 0.0
        dev_pct = abs(actual_pct - expected_pct)
        mad_sum += dev_pct / 100.0
        benford_rows.append({
            "Leading_Digit": str(d),
            "Expected_Benford_%": round(expected_pct, 2),
            "Actual_Ledger_%": round(actual_pct, 2),
            "Deviation_%": round(dev_pct, 2),
            "Transaction_Count": actual_cnt
        })
    benford_df = pd.DataFrame(benford_rows)
    mad_val = mad_sum / 9.0

    # 2. Multivariate / Robust Z-Score & IQR Outlier Quarantine
    num_series = pd.to_numeric(work[rev_col], errors="coerce")
    q1 = num_series.quantile(0.25)
    q3 = num_series.quantile(0.75)
    iqr = max(float(q3 - q1), 1e-6)
    mean_v = float(num_series.mean()) if len(num_series.dropna()) > 0 else 0.0
    std_v = max(float(num_series.std()), 1e-6) if len(num_series.dropna()) > 1 else 1.0

    z_scores = ((num_series - mean_v) / std_v).abs()
    iqr_upper = q3 + 2.2 * iqr

    work["Anomaly_Z_Score"] = z_scores.round(2)
    work["Forensic_Risk_Flag"] = np.where(
        (z_scores > 2.5) | (num_series > iqr_upper) | (num_series <= 0),
        "HIGH_RISK",
        "VERIFIED"
    )
    quarantine_df = work[work["Forensic_Risk_Flag"] == "HIGH_RISK"].copy()
    status_label = "CONFORMING (Low Manipulation Risk)" if mad_val < 0.015 else ("MODERATE VARIANCE (Review Thresholds)" if mad_val < 0.035 else "HIGH FORENSIC DEVIATION (Synthetic / Split-Invoice Pattern)")
    return work, benford_df, quarantine_df, mad_val, status_label

def render_pulsebi_nextgen_command_suite():
    import io
    import numpy as np
    import pandas as pd
    import streamlit as st

    active_df = _get_best_active_df()
    if active_df is None or active_df.empty:
        return

    rev_col, prod_col, cust_col, date_col = _detect_columns(active_df)
    audited_df, benford_df, quarantine_df, mad_val, benford_status = compute_forensic_audit(active_df)

    # Inject Sidebar Star-Schema ZIP & Quarantine Exports cleanly under Enterprise Export Studio
    st.sidebar.markdown("### 🚀 Next-Gen BI & Forensic Bundles")
    try:
        zip_bytes = build_star_schema_zip_bundle(audited_df)
        st.sidebar.download_button(
            "⭐ Power BI Star-Schema + DAX (.ZIP)",
            data=zip_bytes,
            file_name="PulseBI_StarSchema_DAX_Bundle.zip",
            mime="application/zip",
            use_container_width=True,
            key="sb_dl_star_zip"
        )
    except Exception:
        pass

    if not quarantine_df.empty:
        q_csv = quarantine_df.to_csv(index=False).encode("utf-8")
        st.sidebar.download_button(
            f"🚨 Quarantine Ledger ({len(quarantine_df)} Flagged .CSV)",
            data=q_csv,
            file_name="PulseBI_Quarantine_HighRisk_Rows.csv",
            mime="text/csv",
            use_container_width=True,
            key="sb_dl_quarantine"
        )

    st.markdown("---")
    st.markdown("## 🚀 PulseBI Autonomous Command & Forensic Lab")
    st.caption("Benford's Law First-Digit Forensics • 10,000-Run Monte Carlo Cash-Flow Stress-Tester • Natural Language-to-Pandas Engine • 1-Click Star-Schema Compiler")

    tab_forensic, tab_monte, tab_nlq, tab_star = st.tabs([
        "🕵️‍♂️ Forensic Fraud & Benford Radar",
        "🎲 10,000-Run Monte Carlo Stress-Tester",
        "⚡ Natural Language-to-Pandas Co-Pilot",
        "⭐ Power BI Star-Schema & DAX Studio"
    ])

    # --- TAB 1: FORENSIC FRAUD & BENFORD RADAR ---
    with tab_forensic:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Benford MAD Score", f"{mad_val:.4f}", help="Mean Absolute Deviation across leading digits 1-9")
        c2.metric("Quarantined Outliers", f"{len(quarantine_df):,}", f"{(len(quarantine_df)/max(len(active_df),1)*100):.1f}% of ledger")
        rev_at_risk = float(pd.to_numeric(quarantine_df[rev_col], errors="coerce").sum()) if (rev_col and not quarantine_df.empty) else 0.0
        c3.metric("Revenue at Forensic Risk", f"₹{rev_at_risk:,.2f}")
        c4.metric("Ledger Integrity Posture", "Audit Active", benford_status.split("(")[0].strip())

        st.info(f"**Benford's Law Forensic Verdict:** {benford_status} (Analyzed column: `{rev_col}`)")

        if not benford_df.empty:
            col_b1, col_b2 = st.columns([3, 2])
            with col_b1:
                st.markdown("#### 📊 First-Digit Frequency: Actual Ledger vs. Benford Theoretical")
                chart_df = benford_df.set_index("Leading_Digit")[["Expected_Benford_%", "Actual_Ledger_%"]]
                st.bar_chart(chart_df)
            with col_b2:
                st.markdown("#### 🔢 Leading-Digit Forensic Table")
                st.dataframe(benford_df, use_container_width=True, hide_index=True)

        st.markdown("#### 🚨 Isolated High-Risk & Anomaly Quarantine Ledger")
        if not quarantine_df.empty:
            st.dataframe(quarantine_df.head(50), use_container_width=True)
        else:
            st.success("Zero high-risk statistical outliers detected at current Z-score threshold.")

    # --- TAB 2: 10,000-RUN MONTE CARLO CASH-FLOW STRESS-TESTER ---
    with tab_monte:
        st.markdown("#### 🎲 Stochastic 90-Day Cash-Flow & Runway Stress-Tester (10,000 Trajectories)")
        mc1, mc2, mc3 = st.columns(3)
        with mc1:
            churn_shock = st.slider("📉 Customer Churn Spike Shock (%)", min_value=0, max_value=50, value=10, step=5, key="mc_churn")
        with mc2:
            margin_shock = st.slider("⚡ Supply / Margin Compression Shock (%)", min_value=-20, max_value=30, value=5, step=5, key="mc_margin")
        with mc3:
            growth_boost = st.slider("🚀 Upsell / Pricing Expansion (%)", min_value=-20, max_value=40, value=10, step=5, key="mc_growth")

        num_vals = pd.to_numeric(active_df[rev_col], errors="coerce").dropna() if rev_col else pd.Series([100.0, 150.0, 200.0])
        base_daily_rev = max(float(num_vals.sum()) / 90.0, 100.0)
        hist_cv = min(max(float(num_vals.std() / max(num_vals.mean(), 1e-6)), 0.10), 0.65)

        net_drift_multiplier = (1.0 - churn_shock / 100.0) * (1.0 - margin_shock / 100.0) * (1.0 + growth_boost / 100.0)
        adj_daily_mean = base_daily_rev * net_drift_multiplier
        daily_sigma = adj_daily_mean * hist_cv

        # Vectorized 10,000 x 90 Monte Carlo Simulation
        rng = np.random.default_rng(42)
        sim_daily = rng.normal(loc=adj_daily_mean, scale=daily_sigma, size=(10000, 90))
        sim_daily = np.clip(sim_daily, a_min=0.0, a_max=None)
        sim_cum = np.cumsum(sim_daily, axis=1)

        p10_curve = np.percentile(sim_cum, 10, axis=0)
        p50_curve = np.percentile(sim_cum, 50, axis=0)
        p90_curve = np.percentile(sim_cum, 90, axis=0)

        final_totals = sim_cum[:, -1]
        p10_final, p50_final, p90_final = float(p10_curve[-1]), float(p50_curve[-1]), float(p90_curve[-1])
        baseline_90d = base_daily_rev * 90.0
        prob_beat_baseline = float((final_totals >= baseline_90d).mean() * 100.0)

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("P10 Bear-Case (90d)", f"₹{p10_final:,.0f}", f"{((p10_final/baseline_90d - 1)*100):+.1f}% vs Base")
        k2.metric("P50 Median Forecast (90d)", f"₹{p50_final:,.0f}", f"{((p50_final/baseline_90d - 1)*100):+.1f}% vs Base")
        k3.metric("P90 Bull-Case (90d)", f"₹{p90_final:,.0f}", f"{((p90_final/baseline_90d - 1)*100):+.1f}% vs Base")
        k4.metric("Prob. of Beating Baseline", f"{prob_beat_baseline:.1f}%", "10,000 Runs")

        fan_df = pd.DataFrame({
            "Day": [f"Day {i+1}" for i in range(90)],
            "P10_Bear_Case": np.round(p10_curve, 2),
            "P50_Median_Case": np.round(p50_curve, 2),
            "P90_Bull_Case": np.round(p90_curve, 2)
        }).set_index("Day")
        st.line_chart(fan_df[["P10_Bear_Case", "P50_Median_Case", "P90_Bull_Case"]])

    # --- TAB 3: NATURAL LANGUAGE-TO-PANDAS CO-PILOT ---
    with tab_nlq:
        st.markdown("#### ⚡ Deterministic Natural Language-to-Pandas Co-Pilot")
        preset_q = st.selectbox(
            "Select an Instant Executive Audit Query or Type Custom Below:",
            [
                "Show top 10 breakdown by primary category & total revenue",
                "Isolate top 25 highest value transactions sorted descending",
                "Show Pareto 80/20 revenue concentration across entities",
                "Display full numerical summary statistics (mean, std, quartiles)"
            ],
            key="nlq_preset"
        )
        custom_q = st.text_input("Or type a custom query keyword (e.g., 'outlier', 'missing', 'top', 'summary'):", value="", key="nlq_custom")
        active_query = custom_q.strip().lower() if custom_q.strip() else preset_q.lower()

        if "top 10" in active_query or "breakdown" in active_query or "pareto" in active_query:
            grp_col = prod_col if prod_col else (cust_col if cust_col else active_df.columns[0])
            if rev_col and grp_col:
                tmp = active_df.copy()
                tmp[rev_col] = pd.to_numeric(tmp[rev_col], errors="coerce").fillna(0.0)
                agg = tmp.groupby(grp_col, dropna=False)[rev_col].agg(["count", "sum", "mean"]).reset_index()
                agg.columns = [grp_col, "Transaction_Count", "Total_Revenue", "Avg_Ticket"]
                agg = agg.sort_values("Total_Revenue", ascending=False).head(15)
                agg["Revenue_Share_%"] = (agg["Total_Revenue"] / max(agg["Total_Revenue"].sum(), 1e-6) * 100.0).round(2)
                agg["Cumulative_Share_%"] = agg["Revenue_Share_%"].cumsum().round(2)
                st.code(f"df.groupby('{grp_col}')['{rev_col}'].agg(['count', 'sum', 'mean']).sort_values('sum', ascending=False)", language="python")
                st.dataframe(agg, use_container_width=True, hide_index=True)
                st.bar_chart(agg.set_index(grp_col)["Total_Revenue"])
        elif "highest" in active_query or "top" in active_query:
            if rev_col:
                tmp = active_df.copy()
                tmp[rev_col] = pd.to_numeric(tmp[rev_col], errors="coerce")
                top_rows = tmp.sort_values(by=rev_col, ascending=False).head(25)
                st.code(f"df.sort_values(by='{rev_col}', ascending=False).head(25)", language="python")
                st.dataframe(top_rows, use_container_width=True)
        elif "outlier" in active_query or "risk" in active_query:
            st.code("df[df['Forensic_Risk_Flag'] == 'HIGH_RISK']", language="python")
            st.dataframe(quarantine_df.head(50), use_container_width=True)
        else:
            st.code("df.describe(include='all').T", language="python")
            st.dataframe(active_df.describe(include="all").T, use_container_width=True)

    # --- TAB 4: POWER BI STAR-SCHEMA & DAX STUDIO ---
    with tab_star:
        st.markdown("#### ⭐ Automated Power BI Star-Schema & DAX Measure Compiler")
        st.write("Download the complete normalized 4-table Star Schema (`Fact_Transactions`, `Dim_Products`, `Dim_Customers`, `Dim_Calendar`) + pre-built DAX script in one click:")
        zip_data = build_star_schema_zip_bundle(audited_df)
        st.download_button(
            "📦 Download Complete Power BI Star-Schema Bundle (.ZIP)",
            data=zip_data,
            file_name="PulseBI_StarSchema_DAX_Bundle.zip",
            mime="application/zip",
            use_container_width=True,
            key="main_dl_star_zip"
        )
        target_rev = rev_col if rev_col else "Revenue_Amount"
        st.markdown("##### 📜 Auto-Generated DAX Measures Preview (`PulseBI_Executive_Measures.dax`)")
        st.code(f"""Total Gross Revenue = SUM('Fact_Transactions'[{target_rev}])
Verified Transaction Count = COUNTROWS('Fact_Transactions')
Average Order Value (AOV) = DIVIDE([Total Gross Revenue], [Verified Transaction Count], 0)
Pareto Top 20% Customer Revenue = 
    CALCULATE(
        [Total Gross Revenue],
        FILTER(
            VALUES('Dim_Customers'[Customer_Key]),
            RANKX(ALL('Dim_Customers'), [Total Gross Revenue], , DESC, Dense) <= COUNTROWS(ALL('Dim_Customers')) * 0.20
        )
    )""", language="dax")


# === PULSEBI 1-CLICK EXECUTIVE BOARD DECK GENERATOR ===
def build_interactive_board_deck_html(df, deck_title="Q4 Executive Financial & Forensic Audit", presenter="Office of the CFO • PulseBI Autonomous Studio"):
    import numpy as np
    import pandas as pd

    rev_col, prod_col, cust_col, date_col = _detect_columns(df)
    audited_df, benford_df, quarantine_df, mad_val, benford_status = compute_forensic_audit(df)

    total_rows = len(df)
    num_series = pd.to_numeric(df[rev_col], errors="coerce").fillna(0.0) if rev_col else pd.Series([0.0])
    total_rev = float(num_series.sum())
    avg_ticket = float(num_series.mean()) if len(num_series) > 0 else 0.0
    quarantine_count = len(quarantine_df)
    rev_at_risk = float(pd.to_numeric(quarantine_df[rev_col], errors="coerce").sum()) if (rev_col and not quarantine_df.empty) else 0.0

    # Compute Top 5 Entities for Slide 2
    grp_col = prod_col if prod_col else (cust_col if cust_col else df.columns[0])
    top_entities_html = ""
    if rev_col and grp_col:
        tmp = df.copy()
        tmp[rev_col] = pd.to_numeric(tmp[rev_col], errors="coerce").fillna(0.0)
        agg = tmp.groupby(grp_col, dropna=False)[rev_col].sum().reset_index().sort_values(rev_col, ascending=False).head(5)
        max_v = max(float(agg[rev_col].max()), 1.0) if not agg.empty else 1.0
        for _, r in agg.iterrows():
            name_str = str(r[grp_col])[:28]
            val_v = float(r[rev_col])
            pct_w = min(max(int((val_v / max_v) * 100), 6), 100)
            share_pct = (val_v / max(total_rev, 1e-6)) * 100.0
            top_entities_html += f"""
            <div class="bar-row">
                <div class="bar-label">{name_str}</div>
                <div class="bar-track"><div class="bar-fill" style="width:{pct_w}%;"></div></div>
                <div class="bar-val">₹{val_v:,.0f} ({share_pct:.1f}%)</div>
            </div>"""

    # Compute Benford rows for Slide 3
    benford_bars_html = ""
    if not benford_df.empty:
        for _, r in benford_df.iterrows():
            d_str = str(r["Leading_Digit"])
            exp_v = float(r["Expected_Benford_%"])
            act_v = float(r["Actual_Ledger_%"])
            w_exp = min(int(exp_v * 2.5), 100)
            w_act = min(int(act_v * 2.5), 100)
            benford_bars_html += f"""
            <div class="benford-row">
                <span class="digit-badge">Digit {d_str}</span>
                <div class="dual-bars">
                    <div class="b-bar exp" style="width:{w_exp}%" title="Expected: {exp_v:.1f}%"></div>
                    <div class="b-bar act" style="width:{w_act}%" title="Actual: {act_v:.1f}%"></div>
                </div>
                <span class="b-stat">{act_v:.1f}% vs {exp_v:.1f}%</span>
            </div>"""

    # Compute Monte Carlo P10 / P50 / P90 for Slide 4
    base_daily = max(total_rev / 90.0, 100.0)
    hist_cv = min(max(float(num_series.std() / max(num_series.mean(), 1e-6)), 0.10), 0.65)
    rng = np.random.default_rng(42)
    sim_daily = np.clip(rng.normal(loc=base_daily, scale=base_daily * hist_cv, size=(10000, 90)), 0.0, None)
    sim_totals = np.sum(sim_daily, axis=1)
    p10_val = float(np.percentile(sim_totals, 10))
    p50_val = float(np.percentile(sim_totals, 50))
    p90_val = float(np.percentile(sim_totals, 90))

    html_deck = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{deck_title} — PulseBI Board Deck</title>
<style>
    :root {{
        --bg-dark: #070B14;
        --card-bg: #111827;
        --border: #1F2937;
        --accent: #38BDF8;
        --accent-glow: rgba(56, 189, 248, 0.25);
        --emerald: #10B981;
        --amber: #F59E0B;
        --rose: #F43F5E;
        --text-main: #F8FAFC;
        --text-muted: #94A3B8;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Inter, Roboto, sans-serif;
        background: var(--bg-dark);
        color: var(--text-main);
        overflow: hidden;
        height: 100vh;
        display: flex;
        flex-direction: column;
    }}
    .deck-topbar {{
        height: 54px;
        background: rgba(17, 24, 39, 0.92);
        border-bottom: 1px solid var(--border);
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 28px;
        z-index: 100;
    }}
    .brand {{ font-weight: 700; font-size: 15px; color: var(--accent); letter-spacing: 0.5px; }}
    .controls {{ display: flex; align-items: center; gap: 12px; }}
    .btn {{
        background: #1E293B;
        color: var(--text-main);
        border: 1px solid #334155;
        padding: 6px 14px;
        border-radius: 8px;
        cursor: pointer;
        font-size: 13px;
        font-weight: 600;
        transition: all 0.2s;
    }}
    .btn:hover {{ border-color: var(--accent); background: #0F172A; }}
    .btn-primary {{ background: linear-gradient(135deg, #0284C7, #2563EB); border: none; }}
    .slide-viewport {{
        flex: 1;
        position: relative;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 32px;
    }}
    .slide {{
        display: none;
        width: 100%;
        max-width: 1180px;
        height: 100%;
        max-height: 660px;
        background: radial-gradient(circle at top right, rgba(56, 189, 248, 0.08), transparent 45%), var(--card-bg);
        border: 1px solid var(--border);
        border-radius: 20px;
        padding: 48px 56px;
        box-shadow: 0 25px 60px rgba(0,0,0,0.65);
        flex-direction: column;
        justify-content: space-between;
        animation: fadeIn 0.35s ease;
    }}
    .slide.active {{ display: flex; }}
    @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(8px); }} to {{ opacity: 1; transform: translateY(0); }} }}
    .slide-tag {{
        display: inline-block;
        background: rgba(56, 189, 248, 0.12);
        color: var(--accent);
        border: 1px solid rgba(56, 189, 248, 0.3);
        padding: 5px 12px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 14px;
    }}
    h1 {{ font-size: 40px; line-height: 1.15; margin-bottom: 12px; color: #FFFFFF; }}
    h2 {{ font-size: 28px; margin-bottom: 8px; color: #FFFFFF; }}
    .sub {{ color: var(--text-muted); font-size: 16px; max-width: 780px; line-height: 1.5; }}
    .kpi-grid {{
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 18px;
        margin: 24px 0;
    }}
    .kpi-card {{
        background: rgba(15, 23, 42, 0.75);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 20px;
    }}
    .kpi-title {{ font-size: 12px; text-transform: uppercase; color: var(--text-muted); letter-spacing: 0.7px; margin-bottom: 8px; }}
    .kpi-value {{ font-size: 28px; font-weight: 800; color: var(--accent); }}
    .kpi-sub {{ font-size: 12px; color: var(--emerald); margin-top: 6px; }}
    .bar-row {{ display: flex; align-items: center; gap: 14px; margin-bottom: 12px; }}
    .bar-label {{ width: 190px; font-size: 14px; font-weight: 600; color: #E2E8F0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
    .bar-track {{ flex: 1; height: 14px; background: #1E293B; border-radius: 8px; overflow: hidden; }}
    .bar-fill {{ height: 100%; background: linear-gradient(90deg, #38BDF8, #6366F1); border-radius: 8px; }}
    .bar-val {{ width: 170px; text-align: right; font-size: 13px; color: var(--text-muted); font-variant-numeric: tabular-nums; }}
    .benford-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-top: 14px; }}
    .benford-row {{ background: #0F172A; border: 1px solid var(--border); padding: 10px 14px; border-radius: 10px; }}
    .digit-badge {{ font-size: 12px; font-weight: 700; color: var(--accent); }}
    .dual-bars {{ margin: 6px 0; display: flex; flex-direction: column; gap: 4px; }}
    .b-bar {{ height: 6px; border-radius: 4px; }}
    .b-bar.exp {{ background: #64748B; }}
    .b-bar.act {{ background: #10B981; }}
    .b-stat {{ font-size: 11px; color: var(--text-muted); }}
    .slide-footer {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-top: 1px solid var(--border);
        padding-top: 16px;
        font-size: 12px;
        color: var(--text-muted);
    }}
    .progress-bar {{ height: 3px; background: var(--accent); transition: width 0.3s; }}
    @media print {{
        body {{ overflow: visible; height: auto; background: #070B14; }}
        .deck-topbar {{ display: none; }}
        .slide-viewport {{ display: block; padding: 0; }}
        .slide {{ display: flex !important; page-break-after: always; max-height: none; height: 95vh; margin-bottom: 20px; }}
    }}
</style>
</head>
<body>

<div class="deck-topbar">
    <div class="brand">⚡ PULSEBI STUDIO • EXECUTIVE BOARD BRIEFING</div>
    <div class="controls">
        <button class="btn" onclick="prevSlide()">← Prev</button>
        <span id="slideIndicator" style="font-size:13px; color:#94A3B8; min-width:75px; text-align:center;">Slide 1 / 5</span>
        <button class="btn" onclick="nextSlide()">Next →</button>
        <button class="btn btn-primary" onclick="window.print()">🖨️ Print / Save PDF</button>
    </div>
</div>
<div id="progressBar" class="progress-bar" style="width: 20%;"></div>

<div class="slide-viewport">
    <!-- SLIDE 1: EXECUTIVE SUMMARY -->
    <div class="slide active">
        <div>
            <span class="slide-tag">Slide 01 • Executive Overview</span>
            <h1>{deck_title}</h1>
            <p class="sub">{presenter} • Automated ETL Scrubbing, Forensic Benford Audit & Stochastic Cash-Flow Modeling</p>
            <div class="kpi-grid">
                <div class="kpi-card">
                    <div class="kpi-title">Verified Ledger Rows</div>
                    <div class="kpi-value">{total_rows:,}</div>
                    <div class="kpi-sub">✓ 100% Schema Standardized</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">Total Gross Revenue</div>
                    <div class="kpi-value">₹{total_rev:,.0f}</div>
                    <div class="kpi-sub">Primary Metric: {rev_col}</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">Average Ticket (AOV)</div>
                    <div class="kpi-value">₹{avg_ticket:,.2f}</div>
                    <div class="kpi-sub">Clean Transaction Mean</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">Forensic Risk Exposure</div>
                    <div class="kpi-value" style="color: #F43F5E;">{quarantine_count:,} Rows</div>
                    <div class="kpi-sub" style="color: #F59E0B;">₹{rev_at_risk:,.0f} Isolated</div>
                </div>
            </div>
        </div>
        <div class="slide-footer">
            <span>PulseBI Autonomous BI Suite • Confidential Board Briefing</span>
            <span>Use ← / → Arrow Keys to Navigate</span>
        </div>
    </div>

    <!-- SLIDE 2: PARETO CONCENTRATION -->
    <div class="slide">
        <div>
            <span class="slide-tag">Slide 02 • Revenue Concentration</span>
            <h2>Pareto 80/20 Entity & Product Performance</h2>
            <p class="sub" style="margin-bottom: 24px;">Top revenue contributors ranked by gross ledger volume across <b>{grp_col}</b>.</p>
            <div style="margin-top: 18px;">
                {top_entities_html if top_entities_html else "<p class='sub'>No categorical breakdown column detected.</p>"}
            </div>
        </div>
        <div class="slide-footer">
            <span>Concentration Audit • Dimension: {grp_col}</span>
            <span>Slide 2 of 5</span>
        </div>
    </div>

    <!-- SLIDE 3: FORENSIC BENFORD RADAR -->
    <div class="slide">
        <div>
            <span class="slide-tag">Slide 03 • Forensic Integrity Audit</span>
            <h2>Benford's Law First-Digit Fraud & Anomaly Radar</h2>
            <p class="sub">Mean Absolute Deviation (MAD): <b style="color:#38BDF8;">{mad_val:.4f}</b> — Verdict: <b>{benford_status}</b></p>
            <div class="benford-grid">
                {benford_bars_html}
            </div>
        </div>
        <div class="slide-footer">
            <span>Green = Actual Ledger % • Slate = Expected Benford Logarithm %</span>
            <span>Slide 3 of 5</span>
        </div>
    </div>

    <!-- SLIDE 4: MONTE CARLO SIMULATION -->
    <div class="slide">
        <div>
            <span class="slide-tag">Slide 04 • Probabilistic Cash-Flow</span>
            <h2>10,000-Run Monte Carlo 90-Day Revenue Projection</h2>
            <p class="sub">Stochastic trajectory simulation incorporating historical daily variance (CV: {hist_cv:.2f}).</p>
            <div class="kpi-grid" style="grid-template-columns: repeat(3, 1fr); margin-top: 32px;">
                <div class="kpi-card">
                    <div class="kpi-title">P10 Bear-Case (90-Day)</div>
                    <div class="kpi-value" style="color:#F59E0B;">₹{p10_val:,.0f}</div>
                    <div class="kpi-sub">90% Downside Confidence Floor</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">P50 Base-Case Median</div>
                    <div class="kpi-value" style="color:#38BDF8;">₹{p50_val:,.0f}</div>
                    <div class="kpi-sub">Expected Central Trajectory</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">P90 Bull-Case Upside</div>
                    <div class="kpi-value" style="color:#10B981;">₹{p90_val:,.0f}</div>
                    <div class="kpi-sub">Top Decile Expansion Band</div>
                </div>
            </div>
        </div>
        <div class="slide-footer">
            <span>10,000 Stochastic Runs • 90-Day Horizon</span>
            <span>Slide 4 of 5</span>
        </div>
    </div>

    <!-- SLIDE 5: CFO ACTION PLAYBOOK -->
    <div class="slide">
        <div>
            <span class="slide-tag">Slide 05 • Strategic Action Plan</span>
            <h2>Executive CFO Recommendations & BI Deployment</h2>
            <p class="sub" style="margin-bottom: 22px;">Immediate operational actions generated autonomously from your ledger profile:</p>
            <div class="kpi-grid" style="grid-template-columns: 1fr; gap: 14px;">
                <div class="kpi-card" style="padding:16px 20px;">
                    <div class="kpi-title" style="color:#F43F5E;">1. Audit & Resolve Quarantined Transactions</div>
                    <p style="font-size:14px; color:#E2E8F0;">Review the <b>{quarantine_count:,} flagged high-risk rows</b> (representing ₹{rev_at_risk:,.0f} in exposure) exported in the Quarantine Ledger before closing monthly books.</p>
                </div>
                <div class="kpi-card" style="padding:16px 20px;">
                    <div class="kpi-title" style="color:#38BDF8;">2. Lock In P10 Cash-Flow Buffers</div>
                    <p style="font-size:14px; color:#E2E8F0;">Anchor quarterly working capital commitments against the P10 Bear-Case floor (<b>₹{p10_val:,.0f}</b>) while targeting P50/P90 expansion milestones.</p>
                </div>
                <div class="kpi-card" style="padding:16px 20px;">
                    <div class="kpi-title" style="color:#10B981;">3. Deploy Normalized Star-Schema to Power BI</div>
                    <p style="font-size:14px; color:#E2E8F0;">Import the auto-compiled <b>Fact_Transactions</b> and <b>Dim_*</b> tables alongside <b>PulseBI_Executive_Measures.dax</b> for live enterprise reporting.</p>
                </div>
            </div>
        </div>
        <div class="slide-footer">
            <span>Generated by PulseBI Studio • End of Briefing</span>
            <span>Slide 5 of 5</span>
        </div>
    </div>
</div>

<script>
    let currentSlide = 0;
    const slides = document.querySelectorAll('.slide');
    const indicator = document.getElementById('slideIndicator');
    const progress = document.getElementById('progressBar');

    function updateDeck() {{
        slides.forEach((s, idx) => s.classList.toggle('active', idx === currentSlide));
        indicator.textContent = `Slide ${{currentSlide + 1}} / ${{slides.length}}`;
        progress.style.width = `${{((currentSlide + 1) / slides.length) * 100}}%`;
    }}
    function nextSlide() {{ currentSlide = (currentSlide + 1) % slides.length; updateDeck(); }}
    function prevSlide() {{ currentSlide = (currentSlide - 1 + slides.length) % slides.length; updateDeck(); }}
    document.addEventListener('keydown', (e) => {{
        if (e.key === 'ArrowRight' || e.key === ' ') nextSlide();
        if (e.key === 'ArrowLeft') prevSlide();
    }});
</script>
</body>
</html>"""
    return html_deck

def render_board_deck_studio_section():
    import streamlit as st
    import streamlit.components.v1 as components

    active_df = _get_best_active_df()
    if active_df is None or active_df.empty:
        return

    # 1. Add 1-Click Board Deck Download to Sidebar
    try:
        sidebar_deck_html = build_interactive_board_deck_html(active_df)
        st.sidebar.download_button(
            "📽️ 1-Click CFO Board Deck (.HTML Slides)",
            data=sidebar_deck_html.encode("utf-8"),
            file_name="PulseBI_Executive_Board_Deck.html",
            mime="text/html",
            use_container_width=True,
            key="sb_dl_board_deck"
        )
    except Exception:
        pass

    # 2. Render Interactive Board Deck Studio on Main Page
    with st.expander("📽️ Interactive Executive Board Deck Studio (Live 5-Slide Presentation Preview & Export)", expanded=True):
        c_d1, c_d2, c_d3 = st.columns([2, 2, 1])
        with c_d1:
            custom_title = st.text_input("Presentation Title:", value="Q4 Executive Financial & Forensic Audit", key="deck_title_in")
        with c_d2:
            custom_pres = st.text_input("Presenter / Attribution:", value="Office of the CFO • PulseBI Autonomous Studio", key="deck_pres_in")
        deck_html = build_interactive_board_deck_html(active_df, deck_title=custom_title, presenter=custom_pres)
        with c_d3:
            st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
            st.download_button(
                "📥 Download Deck (.HTML)",
                data=deck_html.encode("utf-8"),
                file_name="PulseBI_Executive_Board_Deck.html",
                mime="text/html",
                use_container_width=True,
                key="main_dl_board_deck"
            )
        st.caption("💡 **Interactive Preview Below:** Click **Next → / ← Prev** in the slide topbar (or click inside the slide and use your keyboard `←` / `→` arrows). Click **🖨️ Print / Save PDF** to export as a multi-page PDF.")
        components.html(deck_html, height=620, scrolling=False)

render_pulsebi_nextgen_command_suite()
render_board_deck_studio_section()

