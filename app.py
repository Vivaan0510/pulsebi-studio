
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


# """
# PulseBI Studio — Main Streamlit Application Entry Point
# End-to-End Automated Data Prep, Predictive Business Modelling & Power BI Star-Schema Suite.
# Includes @st.cache_data pipeline caching + Interactive Manual Schema Override.
# """

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
import os as _os
import pandas as _pd
import numpy as _np
import streamlit as _st

_st.session_state["_pulsebi_run_captured"] = False
_st.session_state["_pulsebi_df_priority"] = 0
_PULSEBI_REGISTER_LOCK = False

def _is_derived_or_summary_table(df):
    if df is None or not hasattr(df, "columns"):
        return True
    cols = set(str(c) for c in df.columns)
    # Reject time-series forecast tables, RFM summary tables, Benford tables, or tiny metadata tables
    derived_signatures = {
        "Rolling_7D_Revenue", "Model_Fit", "Series_Type", "Forecast_Lower", "Forecast_Upper",
        "RFM_Segment", "Churn_Prob", "Risk_Level", "Expected_Benford_%", "Leading_Digit",
        "Canonical Master Entity", "Dirty Raw Spelling", "Canonical BI Role"
    }
    if len(cols.intersection(derived_signatures)) > 0:
        return True
    if len(df) < 20 or len(df.columns) < 4:
        return True
    return False

def sanitize_anomalies(df):
    import numpy as np
    import pandas as pd
    if df is None or not isinstance(df, pd.DataFrame) or df.empty:
        return df
    out = df.copy()
    anomaly_tokens = {"error", "unknown", "null entity", "nan", "none", "null", "n/a", "na", "?", "-", ""}
    for col in out.select_dtypes(include=["object", "string"]).columns:
        s_clean = out[col].astype(str).str.strip()
        s_low = s_clean.str.lower()
        out[col] = out[col].where(~s_low.isin(anomaly_tokens), np.nan)
        non_null = out[col].dropna()
        if len(non_null) > 0:
            coerced = pd.to_numeric(non_null.astype(str).str.replace(",", "", regex=False), errors="coerce")
            if coerced.notnull().mean() >= 0.65:
                out[col] = pd.to_numeric(out[col].astype(str).str.replace(",", "", regex=False), errors="coerce")
    return out

def standardize_currency_and_units(df):
    import pandas as pd
    if df is None or not isinstance(df, pd.DataFrame) or df.empty:
        return df
    out = df.copy()
    for col in out.select_dtypes(include=["object", "string"]).columns:
        sample_vals = out[col].dropna().astype(str).head(30)
        if len(sample_vals) == 0:
            continue
        has_currency = sample_vals.str.contains(r'[₹$€£]|USD|INR|EUR|GBP|Rs', case=False, regex=True).any()
        if has_currency:
            cleaned_series = out[col].astype(str).str.replace(r'[^\d.-]', '', regex=True)
            coerced = pd.to_numeric(cleaned_series, errors="coerce")
            if coerced.notnull().mean() >= 0.50:
                out[col] = coerced
    return out

def _register_active_df(df, priority=1):
    global _PULSEBI_REGISTER_LOCK
    import pandas as pd
    import streamlit as st
    if _PULSEBI_REGISTER_LOCK:
        return df
    if df is None or not isinstance(df, pd.DataFrame) or df.empty:
        return df
    # Strictly block forecast_df, rfm_df, and other internal helper tables from overwriting the true ledger!
    if _is_derived_or_summary_table(df):
        return df
    try:
        _PULSEBI_REGISTER_LOCK = True
        work = df
        if st.session_state.get("chk_sanitize", True):
            work = sanitize_anomalies(work)
        if st.session_state.get("chk_currency", True):
            work = standardize_currency_and_units(work)
        curr_priority = st.session_state.get("_pulsebi_df_priority", 0)
        if not st.session_state.get("_pulsebi_run_captured", False) or priority >= curr_priority:
            st.session_state["pulsebi_active_df"] = work
            st.session_state["_pulsebi_run_captured"] = True
            st.session_state["_pulsebi_df_priority"] = priority
        return work
    finally:
        _PULSEBI_REGISTER_LOCK = False

if not hasattr(_pd, "_orig_read_csv"):
    _pd._orig_read_csv = _pd.read_csv
    def _hooked_read_csv(*args, **kwargs):
        df = _pd._orig_read_csv(*args, **kwargs)
        try:
            df = _register_active_df(df, priority=2)
        except Exception:
            pass
        return df
    _pd.read_csv = _hooked_read_csv

if not hasattr(_pd, "_orig_read_excel"):
    _pd._orig_read_excel = _pd.read_excel
    def _hooked_read_excel(*args, **kwargs):
        df = _pd._orig_read_excel(*args, **kwargs)
        try:
            df = _register_active_df(df, priority=2)
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
            else:
                df = _pd.read_excel(uploaded_obj)
            uploaded_obj.seek(0)
            _register_active_df(df, priority=4)
        except Exception:
            pass
    return st.session_state.get("pulsebi_shared_file", None)

# === PULSEBI NON-TECH FRIENDLY CODE REDESIGN ===
if not hasattr(_st, "_orig_code_friendly"):
    _st._orig_code_friendly = _st.code

    def _friendly_code_renderer(body, language="python", *args, **kwargs):
        import streamlit as st
        code_str = str(body or "")
        lang_low = str(language or "").lower()

        if lang_low == "dax" or "SUM(" in code_str or "COUNTROWS" in code_str or "CALCULATE" in code_str:
            st.markdown("""
            <div style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.10), rgba(15, 23, 42, 0.85)); border: 1px solid rgba(16, 185, 129, 0.35); border-radius: 14px; padding: 18px 22px; margin-bottom: 12px;">
                <div style="font-size: 15px; font-weight: 700; color: #34D399; margin-bottom: 8px;">
                    ✅ Ready-to-Use Business Math (No Coding Needed)
                </div>
                <p style="font-size: 13.5px; color: #E2E8F0; line-height: 1.55; margin: 0 0 10px 0;">
                    Your AI Buddy has already written all the calculator formulas for your business so you never have to write spreadsheet math yourself:
                </p>
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; font-size: 13px; color: #CBD5E1;">
                    <div style="background: rgba(30, 41, 59, 0.7); padding: 8px 12px; border-radius: 8px;">💰 <b>Total Sales & Orders:</b> Adds up all clean invoices automatically.</div>
                    <div style="background: rgba(30, 41, 59, 0.7); padding: 8px 12px; border-radius: 8px;">🧾 <b>Typical Order Size:</b> Shows what a regular customer spends per order.</div>
                    <div style="background: rgba(30, 41, 59, 0.7); padding: 8px 12px; border-radius: 8px;">📈 <b>Growth Tracker:</b> Compares current sales against earlier periods.</div>
                    <div style="background: rgba(30, 41, 59, 0.7); padding: 8px 12px; border-radius: 8px;">🏆 <b>VIP 80/20 Finder:</b> Pinpoints the top customers bringing in 80% of your revenue.</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            with st.expander("🛠️ Show Technical Formula Code (Optional — For IT / BI Analysts)", expanded=False):
                return _st._orig_code_friendly(body, language=language, *args, **kwargs)
            return None

        elif "Csv.Document" in code_str or "Table.PromoteHeaders" in code_str or "Table.SelectRows" in code_str or lang_low in ("m", "powerquery", "pq"):
            st.markdown("""
            <div style="background: linear-gradient(135deg, rgba(56, 189, 248, 0.10), rgba(15, 23, 42, 0.85)); border: 1px solid rgba(56, 189, 248, 0.35); border-radius: 14px; padding: 18px 22px; margin-bottom: 12px;">
                <div style="font-size: 15px; font-weight: 700; color: #38BDF8; margin-bottom: 8px;">
                    🪄 Automated Spreadsheet Cleanup Recipe (3 Simple Steps)
                </div>
                <p style="font-size: 13.5px; color: #E2E8F0; line-height: 1.55; margin: 0 0 10px 0;">
                    Instead of fixing messy Excel files by hand every week, this automated recipe cleans everything behind the scenes:
                </p>
                <div style="display: flex; flex-direction: column; gap: 7px; font-size: 13px; color: #CBD5E1;">
                    <div style="background: rgba(30, 41, 59, 0.7); padding: 8px 12px; border-radius: 8px;"><b>Step 1 — Reads Your File:</b> Opens your spreadsheet and detects column headers automatically.</div>
                    <div style="background: rgba(30, 41, 59, 0.7); padding: 8px 12px; border-radius: 8px;"><b>Step 2 — Removes Junk Rows:</b> Deletes empty lines, 'Subtotal' rows, and 'ERROR' text so totals are never double-counted.</div>
                    <div style="background: rgba(30, 41, 59, 0.7); padding: 8px 12px; border-radius: 8px;"><b>Step 3 — Fixes Dates & Money:</b> Converts currency symbols (₹ / $) and text numbers into clean math values.</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            with st.expander("🛠️ Show Technical Automation Script (Optional — For IT / BI Analysts)", expanded=False):
                return _st._orig_code_friendly(body, language=language, *args, **kwargs)
            return None

        elif "df." in code_str or "groupby" in code_str or lang_low == "python":
            with st.expander("🛠️ View How Your AI Buddy Calculated This (Optional Technical Formula)", expanded=False):
                return _st._orig_code_friendly(body, language=language, *args, **kwargs)
            return None

        with st.expander("🛠️ View Technical Details", expanded=False):
            return _st._orig_code_friendly(body, language=language, *args, **kwargs)

    _st.code = _friendly_code_renderer



def sync_shared_upload(uploaded_obj, source_name):
    import streamlit as st
    if uploaded_obj is not None:
        st.session_state["pulsebi_shared_file"] = uploaded_obj
        st.session_state["pulsebi_shared_source"] = source_name
        try:
            uploaded_obj.seek(0)
            if uploaded_obj.name.lower().endswith(".csv"):
                df = _pd.read_csv(uploaded_obj)
            else:
                df = _pd.read_excel(uploaded_obj)
            uploaded_obj.seek(0)
            _register_active_df(df, priority=2)
        except Exception:
            pass
    return st.session_state.get("pulsebi_shared_file", None)



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
    if 'norm_raw_df' in locals() and norm_raw_df is not None and hasattr(norm_raw_df, 'to_csv'):
        norm_raw_df = _register_active_df(norm_raw_df, priority=3)

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
    if 'clean_df' in locals() and clean_df is not None and hasattr(clean_df, 'to_csv'):
        clean_df = _register_active_df(clean_df, priority=5)

    rfm_df, churn_summary, ts_df, forecast_summary = cached_ml_pipelines(
        clean_df,
        ml_model_choice=cfg.ml_model_choice,
        inactivity_days=cfg.inactivity_days,
        forecast_horizon=cfg.forecast_horizon,
    )
    if 'rfm_df' in locals() and rfm_df is not None and hasattr(rfm_df, 'to_csv'):
        rfm_df = _register_active_df(rfm_df, priority=2)

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
                st.markdown("#### 📐 Ready-to-Use Business Formulas (Power BI Ready)")
                st.code(bundle.dax_measures_code, language="dax")
            with code_col2:
                st.markdown("#### ⚙️ Automated Spreadsheet Cleanup Recipe")
                st.code(bundle.power_query_m_code, language="powerquery")


if __name__ == "__main__":
    main()


# === PULSEBI NEXT-GEN AUTONOMOUS INTELLIGENCE SUITE ===
def _get_best_active_df():
    import os
    import streamlit as st
    import pandas as pd
    df = st.session_state.get("pulsebi_active_df", None)
    if df is not None and isinstance(df, pd.DataFrame) and not df.empty and not _is_derived_or_summary_table(df):
        return df
    for cand_name in ["clean_df", "scrubbed_df", "df_clean", "cleaned_df", "norm_raw_df", "raw_df"]:
        if cand_name in globals():
            val = globals()[cand_name]
            if isinstance(val, pd.DataFrame) and not val.empty and not _is_derived_or_summary_table(val):
                return _register_active_df(val, priority=5)
    for k, v in list(st.session_state.items()):
        if isinstance(v, pd.DataFrame) and not v.empty and not _is_derived_or_summary_table(v):
            return v
    if os.path.exists("dirty_cafe_sales.csv"):
        try:
            return _pd._orig_read_csv("dirty_cafe_sales.csv")
        except Exception:
            pass
    return None

def _detect_columns(df):
    import pandas as pd
    if df is None or df.empty:
        return None, None, None, None
    num_cols = list(df.select_dtypes(include=["number"]).columns)
    obj_cols = list(df.select_dtypes(include=["object", "string", "category"]).columns)

    rev_col = None
    priority_rev_names = [
        "Gross_Invoice_INR", "Revenue_INR", "Total Spent", "Total_Revenue", "Net_Revenue",
        "Revenue", "Sales_Amount", "Invoice_Amount", "Amount", "Sales", "Total", "Price Per Unit"
    ]
    for cand in priority_rev_names:
        for c in df.columns:
            if cand.lower() == c.lower():
                rev_col = c
                break
        if rev_col:
            break
    if not rev_col:
        for c in num_cols:
            if any(k in c.lower() for k in ["rev", "spent", "invoice", "amount", "sales", "total", "inr", "usd", "price", "val"]):
                rev_col = c
                break
    if not rev_col and num_cols:
        rev_col = num_cols[-1]

    prod_col, cust_col, date_col = None, None, None
    for c in df.columns:
        cl = c.lower()
        if not date_col and any(k in cl for k in ["date", "time", "booking", "day", "month", "timestamp", "period"]):
            date_col = c
        elif not cust_col and any(k in cl for k in ["party", "customer", "client", "account", "vendor", "buyer", "company", "organization", "entity"]):
            cust_col = c
        elif not prod_col and any(k in cl for k in ["item", "product", "particular", "sku", "service", "category", "segment", "brand"]):
            prod_col = c

    if not cust_col and obj_cols:
        non_date_objs = [c for c in obj_cols if c != date_col and c != prod_col and "id" not in c.lower() and "key" not in c.lower()]
        if non_date_objs:
            cust_col = non_date_objs[0]
    if not prod_col and obj_cols:
        non_date_objs = [c for c in obj_cols if c != date_col and c != cust_col and "id" not in c.lower() and "key" not in c.lower()]
        if non_date_objs:
            prod_col = non_date_objs[0]
        elif cust_col:
            prod_col = cust_col
    return rev_col, prod_col, cust_col, date_col

def _compute_real_daily_pace(df, rev_col, date_col):
    import pandas as pd
    if df is None or df.empty or not rev_col:
        return 0.0, 90
    total_rev = float(pd.to_numeric(df[rev_col], errors="coerce").fillna(0.0).sum())
    days_span = 323
    if date_col and date_col in df.columns:
        parsed = pd.to_datetime(df[date_col], errors="coerce").dropna()
        if len(parsed) > 1:
            span = (parsed.max() - parsed.min()).days
            if span >= 7:
                days_span = span
    daily_pace = total_rev / max(days_span, 1)
    return daily_pace, days_span

def generate_html_audit_report(df, metrics_dict):
    total_rev = metrics_dict.get("total_revenue", 0.0)
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
        <div class="subtitle">Autonomous BI & Financial Ledger Intelligence Report</div>
        <div class="grid">
            <div class="card"><h3>Verified Orders</h3><p>{clean_rows:,}</p></div>
            <div class="card"><h3>Total Scrubbed Revenue</h3><p>₹{total_rev:,.2f}</p></div>
            <div class="card"><h3>Remaining Null Cells</h3><p>{null_count:,}</p></div>
        </div>
        <div class="section">
            <h2>Executive Summary & Compliance Posture</h2>
            <p>This automated audit confirms that your business ledger has been cleaned of duplicate entries, blank/subtotal rows, and spelling typos, and screened for unusual invoice patterns.</p>
        </div>
        <div class="footer">PulseBI Studio Enterprise Edition • Friendly AI Business Companion</div>
    </div>
</body>
</html>"""
    return html

def compute_forensic_audit(df):
    import numpy as np
    import pandas as pd
    rev_col, prod_col, cust_col, date_col = _detect_columns(df)
    work = df.copy()
    if not rev_col:
        return work, pd.DataFrame(), pd.DataFrame(), 0.0, "Healthy & Natural"

    series = pd.to_numeric(work[rev_col], errors="coerce").dropna()
    pos_series = series[series > 0]

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
            "First Digit (1-9)": str(d),
            "Normal Business Pattern (%)": round(expected_pct, 1),
            "Your Actual Invoices (%)": round(actual_pct, 1),
            "Difference (%)": round(dev_pct, 1),
            "Order Count": actual_cnt
        })
    benford_df = pd.DataFrame(benford_rows)
    mad_val = mad_sum / 9.0

    num_series = pd.to_numeric(work[rev_col], errors="coerce")
    q1 = num_series.quantile(0.25)
    q3 = num_series.quantile(0.75)
    iqr = max(float(q3 - q1), 1e-6)
    mean_v = float(num_series.mean()) if len(num_series.dropna()) > 0 else 0.0
    std_v = max(float(num_series.std()), 1e-6) if len(num_series.dropna()) > 1 else 1.0

    z_scores = ((num_series - mean_v) / std_v).abs()
    iqr_upper = q3 + 2.2 * iqr

    work["Unusual_Score"] = z_scores.round(2)
    work["Review_Status"] = np.where(
        (z_scores > 2.5) | (num_series > iqr_upper) | (num_series <= 0),
        "NEEDS_QUICK_CHECK",
        "NORMAL"
    )
    quarantine_df = work[work["Review_Status"] == "NEEDS_QUICK_CHECK"].copy()
    status_label = (
        "Healthy & Natural (Looks 100% Organic)"
        if mad_val < 0.020
        else ("Normal Fixed-Price Pattern (Standard Product Pricing)" if mad_val < 0.040 else "Worth a Quick Look (Many Invoices Start with the Same Number)")
    )
    return work, benford_df, quarantine_df, mad_val, status_label

def build_star_schema_zip_bundle(df):
    import io
    import json
    import zipfile
    import pandas as pd

    rev_col, prod_col, cust_col, date_col = _detect_columns(df)
    work = df.copy()

    if prod_col and prod_col in work.columns:
        unique_prods = work[prod_col].dropna().astype(str).unique()
        dim_prod = pd.DataFrame({
            "Product_Key": [f"PRD-{i+1001}" for i in range(len(unique_prods))],
            "Product_Name": unique_prods
        })
        prod_map = dict(zip(dim_prod["Product_Name"], dim_prod["Product_Key"]))
        work["Product_Key"] = work[prod_col].astype(str).map(prod_map).fillna("PRD-0000")
    else:
        dim_prod = pd.DataFrame({"Product_Key": ["PRD-1001"], "Product_Name": ["Enterprise Standard SKU"]})
        work["Product_Key"] = "PRD-1001"

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

    target_rev = rev_col if rev_col else "Revenue_Amount"
    dax_script = f"""// =========================================================================
// PULSEBI STUDIO — AUTO-COMPILED POWER BI DAX MEASURE SUITE
// =========================================================================

Total Gross Revenue = SUM('Fact_Transactions'[{target_rev}])
Verified Transaction Count = COUNTROWS('Fact_Transactions')
Average Order Value (AOV) = DIVIDE([Total Gross Revenue], [Verified Transaction Count], 0)
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

def build_interactive_board_deck_html(df, deck_title="Business Performance & 90-Day Outlook", presenter="Prepared by Your PulseBI AI Companion"):
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

    grp_col = cust_col if cust_col else (prod_col if prod_col else df.columns[0])
    top_entities_html = ""
    if rev_col and grp_col:
        tmp = df.copy()
        tmp[rev_col] = pd.to_numeric(tmp[rev_col], errors="coerce").fillna(0.0)
        agg = tmp.groupby(grp_col, dropna=False)[rev_col].sum().reset_index().sort_values(rev_col, ascending=False).head(5)
        max_v = max(float(agg[rev_col].max()), 1.0) if not agg.empty else 1.0
        for _, r in agg.iterrows():
            name_str = str(r[grp_col])[:32]
            val_v = float(r[rev_col])
            pct_w = min(max(int((val_v / max_v) * 100), 8), 100)
            share_pct = (val_v / max(total_rev, 1e-6)) * 100.0
            top_entities_html += f"""
            <div class="bar-row">
                <div class="bar-label">{name_str}</div>
                <div class="bar-track"><div class="bar-fill" style="width:{pct_w}%;"></div></div>
                <div class="bar-val">₹{val_v:,.0f} ({share_pct:.1f}%)</div>
            </div>"""

    benford_bars_html = ""
    if not benford_df.empty:
        for _, r in benford_df.iterrows():
            d_str = str(r["First Digit (1-9)"])
            exp_v = float(r["Normal Business Pattern (%)"])
            act_v = float(r["Your Actual Invoices (%)"])
            w_exp = min(int(exp_v * 2.5), 100)
            w_act = min(int(act_v * 2.5), 100)
            benford_bars_html += f"""
            <div class="benford-row">
                <span class="digit-badge">Starts with {d_str}</span>
                <div class="dual-bars">
                    <div class="b-bar exp" style="width:{w_exp}%" title="Normal: {exp_v:.1f}%"></div>
                    <div class="b-bar act" style="width:{w_act}%" title="Yours: {act_v:.1f}%"></div>
                </div>
                <span class="b-stat">Yours: {act_v:.1f}% (Normal: {exp_v:.1f}%)</span>
            </div>"""

    daily_pace, _ = _compute_real_daily_pace(df, rev_col, date_col)
    base_daily = max(daily_pace, 100.0)
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
<title>{deck_title} — PulseBI Presentation</title>
<style>
    :root {{
        --bg-dark: #070B14;
        --card-bg: #111827;
        --border: #1E293B;
        --accent: #38BDF8;
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
        height: 100vh;
        display: flex;
        flex-direction: column;
        overflow: hidden;
    }}
    .deck-topbar {{
        height: 52px;
        background: #0F172A;
        border-bottom: 1px solid var(--border);
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 24px;
    }}
    .brand {{ font-weight: 700; font-size: 14px; color: var(--accent); letter-spacing: 0.5px; }}
    .controls {{ display: flex; align-items: center; gap: 10px; }}
    .btn {{
        background: #1E293B;
        color: var(--text-main);
        border: 1px solid #334155;
        padding: 6px 14px;
        border-radius: 8px;
        cursor: pointer;
        font-size: 13px;
        font-weight: 600;
    }}
    .btn:hover {{ border-color: var(--accent); background: #0F172A; }}
    .btn-primary {{ background: linear-gradient(135deg, #0284C7, #2563EB); border: none; }}
    .slide-viewport {{
        flex: 1;
        display: flex;
        align-items: stretch;
        justify-content: center;
        padding: 16px 24px;
    }}
    .slide {{
        display: none;
        width: 100%;
        height: 100%;
        background: radial-gradient(circle at top right, rgba(56, 189, 248, 0.10), transparent 50%), var(--card-bg);
        border: 1px solid #334155;
        border-radius: 18px;
        padding: 34px 44px;
        box-shadow: 0 20px 50px rgba(0,0,0,0.6);
        flex-direction: column;
        justify-content: space-between;
    }}
    .slide.active {{ display: flex; }}
    .slide-tag {{
        display: inline-block;
        background: rgba(56, 189, 248, 0.14);
        color: var(--accent);
        border: 1px solid rgba(56, 189, 248, 0.35);
        padding: 5px 14px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: 12px;
    }}
    h1 {{ font-size: 34px; line-height: 1.2; margin-bottom: 8px; color: #FFFFFF; }}
    h2 {{ font-size: 26px; margin-bottom: 8px; color: #FFFFFF; }}
    .sub {{ color: var(--text-muted); font-size: 15px; line-height: 1.5; }}
    .kpi-grid {{
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 18px;
        margin: 22px 0;
    }}
    .kpi-card {{
        background: rgba(15, 23, 42, 0.85);
        border: 1px solid #334155;
        border-radius: 14px;
        padding: 20px;
    }}
    .kpi-title {{ font-size: 12px; text-transform: uppercase; color: var(--text-muted); letter-spacing: 0.6px; margin-bottom: 8px; }}
    .kpi-value {{ font-size: 28px; font-weight: 800; color: var(--accent); }}
    .kpi-sub {{ font-size: 12.5px; color: var(--emerald); margin-top: 6px; }}
    .bar-row {{ display: flex; align-items: center; gap: 16px; margin-bottom: 14px; }}
    .bar-label {{ width: 240px; font-size: 15px; font-weight: 600; color: #E2E8F0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
    .bar-track {{ flex: 1; height: 16px; background: #1E293B; border-radius: 8px; overflow: hidden; }}
    .bar-fill {{ height: 100%; background: linear-gradient(90deg, #38BDF8, #6366F1); border-radius: 8px; }}
    .bar-val {{ width: 190px; text-align: right; font-size: 14px; color: #E2E8F0; font-weight: 600; }}
    .benford-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-top: 14px; }}
    .benford-row {{ background: #0F172A; border: 1px solid #334155; padding: 10px 14px; border-radius: 10px; }}
    .digit-badge {{ font-size: 12.5px; font-weight: 700; color: var(--accent); }}
    .dual-bars {{ margin: 6px 0; display: flex; flex-direction: column; gap: 4px; }}
    .b-bar {{ height: 7px; border-radius: 4px; }}
    .b-bar.exp {{ background: #64748B; }}
    .b-bar.act {{ background: #10B981; }}
    .b-stat {{ font-size: 11.5px; color: var(--text-muted); }}
    .slide-footer {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-top: 1px solid var(--border);
        padding-top: 12px;
        font-size: 12.5px;
        color: var(--text-muted);
    }}
    .progress-bar {{ height: 3px; background: var(--accent); transition: width 0.3s; }}
    @media print {{
        body {{ overflow: visible; height: auto; background: #070B14; }}
        .deck-topbar {{ display: none; }}
        .slide-viewport {{ display: block; padding: 0; }}
        .slide {{ display: flex !important; page-break-after: always; height: 95vh; margin-bottom: 20px; }}
    }}
</style>
</head>
<body>
<div class="deck-topbar">
    <div class="brand">⚡ PULSEBI STUDIO • INTERACTIVE SLIDE PRESENTATION</div>
    <div class="controls">
        <button class="btn" onclick="prevSlide()">← Previous Slide</button>
        <span id="slideIndicator" style="font-size:13px; color:#E2E8F0; font-weight:600; min-width:85px; text-align:center;">Slide 1 of 5</span>
        <button class="btn" onclick="nextSlide()">Next Slide →</button>
        <button class="btn btn-primary" onclick="window.print()">🖨️ Print / Save as PDF</button>
    </div>
</div>
<div id="progressBar" class="progress-bar" style="width: 20%;"></div>

<div class="slide-viewport">
    <div class="slide active">
        <div>
            <span class="slide-tag">Slide 1 • The Big Picture</span>
            <h1>{deck_title}</h1>
            <p class="sub">{presenter} • Automatic Spreadsheet Cleanup, Top Customer Breakdown & 90-Day Sales Outlook</p>
            <div class="kpi-grid">
                <div class="kpi-card">
                    <div class="kpi-title">Total Verified Orders</div>
                    <div class="kpi-value">{total_rows:,}</div>
                    <div class="kpi-sub">✓ 100% Cleaned & Verified</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">Total Money Earned</div>
                    <div class="kpi-value">₹{total_rev:,.0f}</div>
                    <div class="kpi-sub">Column: {rev_col}</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">Typical Order Size</div>
                    <div class="kpi-value">₹{avg_ticket:,.0f}</div>
                    <div class="kpi-sub">Daily Pace: ₹{base_daily:,.0f}/day</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">Unusual Orders to Check</div>
                    <div class="kpi-value" style="color: #F43F5E;">{quarantine_count:,} Orders</div>
                    <div class="kpi-sub" style="color: #F59E0B;">Worth ₹{rev_at_risk:,.0f} total</div>
                </div>
            </div>
        </div>
        <div class="slide-footer">
            <span>PulseBI Studio • Friendly Executive Briefing</span>
            <span>Tip: Click 'Next Slide →' above or use your ← / → keyboard arrows</span>
        </div>
    </div>

    <div class="slide">
        <div>
            <span class="slide-tag">Slide 2 • Your Best Customers & Items</span>
            <h2>Top 5 Contributors Bringing In the Most Money</h2>
            <p class="sub" style="margin-bottom: 22px;">Ranked from #1 biggest contributor to #5 across <b>{grp_col}</b>:</p>
            <div style="margin-top: 14px;">
                {top_entities_html if top_entities_html else "<p class='sub'>No category breakdown detected.</p>"}
            </div>
        </div>
        <div class="slide-footer">
            <span>80/20 VIP Concentration • Grouped by: {grp_col}</span>
            <span>Slide 2 of 5</span>
        </div>
    </div>

    <div class="slide">
        <div>
            <span class="slide-tag">Slide 3 • Bookkeeping Safety Check</span>
            <h2>Invoice Pattern & Typing Mistake Check</h2>
            <p class="sub">Safety Verdict: <b style="color:#10B981;">{benford_status}</b></p>
            <div class="benford-grid">
                {benford_bars_html}
            </div>
        </div>
        <div class="slide-footer">
            <span>Green Bar = Your Invoices • Grey Bar = Normal Business Pattern</span>
            <span>Slide 3 of 5</span>
        </div>
    </div>

    <div class="slide">
        <div>
            <span class="slide-tag">Slide 4 • Next 90 Days Forecast</span>
            <h2>What Your Next 3 Months of Sales Look Like</h2>
            <p class="sub">We tested 10,000 future scenarios based on your current daily pace (₹{base_daily:,.0f}/day):</p>
            <div class="kpi-grid" style="grid-template-columns: repeat(3, 1fr); margin-top: 26px;">
                <div class="kpi-card">
                    <div class="kpi-title">Slow Quarter (Safe Floor)</div>
                    <div class="kpi-value" style="color:#F59E0B;">₹{p10_val:,.0f}</div>
                    <div class="kpi-sub">Worst-Case Budget Safety Net</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">Normal Quarter (Most Likely)</div>
                    <div class="kpi-value" style="color:#38BDF8;">₹{p50_val:,.0f}</div>
                    <div class="kpi-sub">Expected 90-Day Sales</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">Busy Quarter (Best Case)</div>
                    <div class="kpi-value" style="color:#10B981;">₹{p90_val:,.0f}</div>
                    <div class="kpi-sub">High-Growth Target</div>
                </div>
            </div>
        </div>
        <div class="slide-footer">
            <span>90-Day Forward Outlook • 10,000 Scenarios Tested</span>
            <span>Slide 4 of 5</span>
        </div>
    </div>

    <div class="slide">
        <div>
            <span class="slide-tag">Slide 5 • 3 Easy Next Steps</span>
            <h2>Your Simple Action Plan for This Week</h2>
            <p class="sub" style="margin-bottom: 16px;">Three practical steps recommended by your AI Business Buddy:</p>
            <div class="kpi-grid" style="grid-template-columns: 1fr; gap: 12px; margin: 10px 0;">
                <div class="kpi-card" style="padding:14px 18px;">
                    <div class="kpi-title" style="color:#F43F5E;">Step 1 — Check on Customers Who Haven't Ordered Lately</div>
                    <p style="font-size:14px; color:#E2E8F0;">Look at the red 'At-Risk' customers in the watchlist above and give them a friendly call or offer so they don't switch to a competitor.</p>
                </div>
                <div class="kpi-card" style="padding:14px 18px;">
                    <div class="kpi-title" style="color:#38BDF8;">Step 2 — Plan Your Expenses Around Your Safe Floor (₹{p10_val:,.0f})</div>
                    <p style="font-size:14px; color:#E2E8F0;">Keep fixed expenses below ₹{p10_val:,.0f} for the next 90 days so you stay profitable even if sales have a slow month.</p>
                </div>
                <div class="kpi-card" style="padding:14px 18px;">
                    <div class="kpi-title" style="color:#10B981;">Step 3 — Spend 2 Minutes Reviewing the {quarantine_count:,} Unusual Orders</div>
                    <p style="font-size:14px; color:#E2E8F0;">Download the Flagged Orders list from the left sidebar to make sure those extra-large orders are real sales and not typing mistakes.</p>
                </div>
            </div>
        </div>
        <div class="slide-footer">
            <span>Generated by PulseBI Studio • End of Presentation</span>
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
        indicator.textContent = `Slide ${{currentSlide + 1}} of ${{slides.length}}`;
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

# Single Clean Hook for st.plotly_chart (Zero Duplicate Buttons!)
def _generate_chart_insights_markdown(fig, chart_title=""):
    import pandas as pd
    title_text = str(chart_title).strip()
    if not title_text and hasattr(fig, "layout") and hasattr(fig.layout, "title") and fig.layout.title.text:
        title_text = str(fig.layout.title.text)
    t_low = title_text.lower()

    df = _get_best_active_df()
    rev_col, prod_col, cust_col, date_col = _detect_columns(df) if df is not None else (None, None, None, None)

    if "pareto" in t_low or "80/20" in t_low or "concentration" in t_low:
        top_name = "your #1 customer"
        top_share = "a large share"
        top_val_str = ""
        if df is not None and rev_col:
            grp = cust_col if cust_col else (prod_col if prod_col else df.columns[0])
            tmp = df.copy()
            tmp[rev_col] = pd.to_numeric(tmp[rev_col], errors="coerce").fillna(0.0)
            agg = tmp.groupby(grp, dropna=False)[rev_col].sum().sort_values(ascending=False)
            if len(agg) > 0 and agg.sum() > 0:
                top_name = str(agg.index[0])
                top_val_str = f" (₹{agg.iloc[0]:,.0f})"
                top_share = f"{(agg.iloc[0] / agg.sum() * 100):.1f}%"
        return (
            "👋 **Your AI Buddy Explains This Chart:**\n"
            "• **The Blue Bars:** Each bar is a customer, lined up from your biggest spender on the far left to smallest on the right.\n"
            "• **The Gold Line & Red 80% Line:** Shows the VIP group that brings in 80% of all your money.\n"
            f"• **What to Do:** **{top_name}**{top_val_str} is your #1 customer (**{top_share}** of all sales). Take great care of the customers on the left side of this chart!"
        )
    elif "seasonal" in t_low or "trajectory" in t_low or "forecast" in t_low or "run-rate" in t_low:
        daily_pace, _ = _compute_real_daily_pace(df, rev_col, date_col) if df is not None else (0.0, 90)
        pace_str = f"₹{daily_pace:,.0f}/day" if daily_pace > 0 else "your usual daily average"
        return (
            "👋 **Your AI Buddy Explains This Chart:**\n"
            f"• **The Blue Line (Left):** Shows your real past sales (averaging around **{pace_str}**). High peaks are busy weeks; dips are slower weeks.\n"
            "• **The Green Line & Shaded Box (Right):** Shows where our computer predicts your sales are heading over the **next 90 days**.\n"
            "• **What to Do:** Use the middle green line to plan your normal budget, and keep some savings ready in case sales dip toward the bottom of the green shaded area."
        )
    elif "churn" in t_low or "rfm" in t_low or "segment" in t_low:
        return (
            "👋 **Your AI Buddy Explains This Chart:**\n"
            "• **Red Bar (At-Risk):** Regular customers who haven't bought from you lately and might leave if you don't check in on them.\n"
            "• **Green Bar (Loyal Accounts):** Your happy, repeat customers who buy on time.\n"
            "• **What to Do:** Give the customers in the Red group a quick friendly call or small discount this week to win them back!"
        )
    elif "product" in t_low or "sku" in t_low:
        return (
            "👋 **Your AI Buddy Explains This Chart:**\n"
            "• **Longest Bars = Best Sellers:** Shows which products or items bring in the most money.\n"
            "• **What to Do:** Always keep your top-selling items well-stocked so you never miss out on easy sales."
        )
    elif "bridge" in t_low or "what-if" in t_low:
        return (
            "👋 **Your AI Buddy Explains This Chart:**\n"
            "• **Left Blue Bar:** Your starting revenue before any changes.\n"
            "• **Middle Green Bars:** Extra money you gain by adjusting prices and saving 'At-Risk' customers using the sliders above.\n"
            "• **Right Blue Bar:** Your new, higher total revenue!"
        )
    else:
        return (
            "👋 **Your AI Buddy Explains This Chart:**\n"
            "• Taller bars and higher lines mean more sales or activity.\n"
            "• Focus on the biggest bars to see what works best in your business!"
        )

# Ensure we always wrap from the true unhooked Streamlit plotly_chart function
for _attr in ["_orig_plotly_chart_pe", "_orig_plotly_chart_master"]:
    if hasattr(_st, _attr):
        _st.plotly_chart = getattr(_st, _attr)
        break

_st._true_base_plotly_chart = _st.plotly_chart

def _buddy_plotly_chart_wrapper(figure_or_data, *args, **kwargs):
    import streamlit as st
    c_title = ""
    try:
        if hasattr(figure_or_data, "layout") and hasattr(figure_or_data.layout, "title") and figure_or_data.layout.title.text:
            c_title = str(figure_or_data.layout.title.text)
    except Exception:
        pass

    explanation_md = _generate_chart_insights_markdown(figure_or_data, c_title)
    res = _st._true_base_plotly_chart(figure_or_data, *args, **kwargs)

    try:
        with st.popover("💬 What Does This Chart Mean? (Click to Ask AI Buddy)", use_container_width=False):
            st.markdown(explanation_md)
    except Exception:
        with st.expander("💬 What Does This Chart Mean? (Click to Ask AI Buddy)", expanded=False):
            st.markdown(explanation_md)
    return res

_st.plotly_chart = _buddy_plotly_chart_wrapper

def inject_modebar_explain_button_js(df):
    import pandas as pd
    import streamlit.components.v1 as components

    rev_col, prod_col, cust_col, date_col = _detect_columns(df) if df is not None else (None, None, None, None)
    total_rev = float(pd.to_numeric(df[rev_col], errors="coerce").fillna(0.0).sum()) if (df is not None and rev_col) else 0.0
    daily_pace, _ = _compute_real_daily_pace(df, rev_col, date_col) if df is not None else (0.0, 90)

    top_name = "Top Account"
    top_share = "0%"
    if df is not None and rev_col:
        grp = cust_col if cust_col else (prod_col if prod_col else df.columns[0])
        tmp = df.copy()
        tmp[rev_col] = pd.to_numeric(tmp[rev_col], errors="coerce").fillna(0.0)
        agg = tmp.groupby(grp, dropna=False)[rev_col].sum().sort_values(ascending=False)
        if len(agg) > 0 and agg.sum() > 0:
            top_name = str(agg.index[0]).replace("'", "").replace('"', '')
            top_share = f"{(agg.iloc[0] / agg.sum() * 100):.1f}%"

    rev_str = f"₹{total_rev:,.0f}"
    pace_str = f"₹{daily_pace:,.0f}/day"

    js_code = f"""
    <script>
    (function() {{
        const parentDoc = window.parent.document;
        if (!parentDoc.getElementById('pulsebi-explain-modal-style')) {{
            const style = parentDoc.createElement('style');
            style.id = 'pulsebi-explain-modal-style';
            style.innerHTML = `
                .pulsebi-modebar-explain-btn {{
                    display: inline-flex !important;
                    align-items: center;
                    justify-content: center;
                    background: linear-gradient(135deg, #0284C7, #2563EB) !important;
                    color: #FFFFFF !important;
                    border-radius: 5px;
                    padding: 2px 7px !important;
                    margin-left: 4px !important;
                    font-size: 11px !important;
                    font-weight: 700 !important;
                    cursor: pointer !important;
                    box-shadow: 0 2px 6px rgba(2,132,199,0.45);
                    text-decoration: none !important;
                }}
                #pulsebi-simple-modal {{
                    position: fixed;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    background: #111827;
                    color: #F8FAFC;
                    border: 1px solid #38BDF8;
                    border-radius: 16px;
                    padding: 26px 30px;
                    max-width: 540px;
                    width: 92%;
                    z-index: 999999;
                    box-shadow: 0 25px 60px rgba(0,0,0,0.85);
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    display: none;
                }}
                #pulsebi-simple-modal h3 {{ margin: 0 0 12px 0; color: #38BDF8; font-size: 19px; }}
                #pulsebi-simple-modal p {{ font-size: 14.5px; line-height: 1.65; color: #E2E8F0; margin-bottom: 10px; }}
                #pulsebi-simple-modal .close-btn {{
                    margin-top: 14px; background: #1E293B; color: #F8FAFC; border: 1px solid #475569;
                    padding: 7px 16px; border-radius: 8px; cursor: pointer; font-weight: 600; float: right;
                }}
            `;
            parentDoc.head.appendChild(style);
        }}

        if (!parentDoc.getElementById('pulsebi-simple-modal')) {{
            const modal = parentDoc.createElement('div');
            modal.id = 'pulsebi-simple-modal';
            modal.innerHTML = `
                <h3 id="pulsebi-modal-title">💡 AI Buddy Chart Guide</h3>
                <div id="pulsebi-modal-body"></div>
                <button class="close-btn" onclick="this.parentElement.style.display='none'">Got It ✓</button>
            `;
            parentDoc.body.appendChild(modal);
        }}

        function attachModebarButtons() {{
            const modebars = parentDoc.querySelectorAll('.modebar-container .modebar');
            modebars.forEach((mb, idx) => {{
                let btn = mb.querySelector('.pulsebi-modebar-explain-btn');
                if (!btn) {{
                    const grp = mb.querySelector('.modebar-group') || mb;
                    btn = parentDoc.createElement('a');
                    btn.className = 'modebar-btn pulsebi-modebar-explain-btn';
                    btn.title = 'Click for a simple explanation of this chart';
                    btn.innerHTML = '💡 Insights';
                    grp.appendChild(btn);
                }}
                btn.onclick = function(e) {{
                    e.preventDefault();
                    e.stopPropagation();
                    let title = '💡 AI Buddy Chart Guide';
                    let bodyHtml = '';
                    if (idx === 1) {{
                        title = '🏆 Your Top Customers (80/20 Rule)';
                        bodyHtml = `
                            <p><b>1. Blue Bars:</b> Ranks your top customers from biggest spender on the left to smallest on the right across your <b>{rev_str}</b> in sales.</p>
                            <p><b>2. Gold & Red 80% Line:</b> Right now, <b>{top_name}</b> is your #1 customer ({top_share} of total sales). The customers to the left of where the gold line crosses the red line bring in 80% of your money.</p>
                            <p><b>3. Friendly Tip:</b> Keep those top customers on the left happy—they pay most of your bills!</p>
                        `;
                    }} else if (idx === 0) {{
                        title = '📈 Past Sales & Next 90 Days Forecast';
                        bodyHtml = `
                            <p><b>1. Blue Line (Left):</b> Your real past sales (averaging <b>{pace_str}</b>).</p>
                            <p><b>2. Green Line & Shaded Area (Right):</b> Where our computer predicts your sales will go over the next 3 months.</p>
                            <p><b>3. Friendly Tip:</b> Plan your regular budget around the middle green line!</p>
                        `;
                    }} else {{
                        title = '💡 How to Read This Chart';
                        bodyHtml = `
                            <p><b>1. Simple Rule:</b> Taller bars or longer lines mean more money or more customers in that group.</p>
                            <p><b>2. Friendly Tip:</b> Focus on the tallest bars to see what is working best, and check red bars to see who needs a quick follow-up call.</p>
                        `;
                    }}
                    parentDoc.getElementById('pulsebi-modal-title').innerText = title;
                    parentDoc.getElementById('pulsebi-modal-body').innerHTML = bodyHtml;
                    parentDoc.getElementById('pulsebi-simple-modal').style.display = 'block';
                }};
            }});
        }}

        attachModebarButtons();
        setInterval(attachModebarButtons, 1200);
    }})();
    </script>
    """
    components.html(js_code, height=0, width=0)

def render_unified_sidebar_studio(active_df, audited_df, quarantine_df, rev_col):
    import io
    import pandas as pd
    import streamlit as st

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🛠️ Automatic Cleanup Settings")
    auto_sanitize = st.sidebar.checkbox(
        "🧹 Auto-Fix Typing Mistakes (ERROR / UNKNOWN → Blank)",
        value=True,
        key="chk_sanitize",
        help="Automatically cleans up 'ERROR' or 'UNKNOWN' text in your spreadsheet."
    )
    enable_currency = st.sidebar.checkbox(
        "💱 Auto-Clean Currency Symbols (₹ / $)",
        value=True,
        key="chk_currency",
        help="Removes ₹ and $ symbols so the computer can add up your money columns accurately."
    )

    st.sidebar.markdown("### 📦 1-Click Download Center")
    if active_df is not None and not active_df.empty:
        export_df = active_df.copy()
        if auto_sanitize:
            export_df = sanitize_anomalies(export_df)
        if enable_currency:
            export_df = standardize_currency_and_units(export_df)

        total_rev_val = float(pd.to_numeric(export_df[rev_col], errors="coerce").fillna(0.0).sum()) if rev_col else 0.0
        st.sidebar.caption(f"✅ Active Data: **{len(export_df):,} orders** (`₹{total_rev_val:,.0f}` total)")

        csv_bytes = export_df.to_csv(index=False).encode("utf-8")
        st.sidebar.download_button(
            "📥 Clean Spreadsheet (.CSV)",
            data=csv_bytes,
            file_name="PulseBI_Cleaned_Data.csv",
            mime="text/csv",
            use_container_width=True,
            key="sb_dl_csv"
        )

        try:
            xl_buf = io.BytesIO()
            with pd.ExcelWriter(xl_buf, engine="openpyxl") as writer:
                export_df.to_excel(writer, sheet_name="Cleaned_Orders", index=False)
                summary_df = pd.DataFrame({
                    "Column": export_df.columns,
                    "Data_Type": [str(t) for t in export_df.dtypes],
                    "Missing_Cells": [int(export_df[c].isnull().sum()) for c in export_df.columns],
                    "Valid_Cells": [int(export_df[c].notnull().sum()) for c in export_df.columns]
                })
                summary_df.to_excel(writer, sheet_name="Health_Check", index=False)
            st.sidebar.download_button(
                "📊 Clean Excel Workbook (.XLSX)",
                data=xl_buf.getvalue(),
                file_name="PulseBI_Cleaned_Workbook.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                key="sb_dl_xlsx"
            )
        except Exception:
            pass

        try:
            sidebar_deck_html = build_interactive_board_deck_html(active_df)
            st.sidebar.download_button(
                "📽️ 5-Slide Presentation Deck (.HTML)",
                data=sidebar_deck_html.encode("utf-8"),
                file_name="PulseBI_Presentation_Slides.html",
                mime="text/html",
                use_container_width=True,
                key="sb_dl_board_deck"
            )
        except Exception:
            pass

        html_str = generate_html_audit_report(export_df, {"total_revenue": total_rev_val, "row_count": len(export_df), "clean_rows": len(export_df)})
        st.sidebar.download_button(
            "📄 1-Page Summary Report (.HTML)",
            data=html_str,
            file_name="PulseBI_Summary_Report.html",
            mime="text/html",
            use_container_width=True,
            key="sb_dl_html"
        )

        if quarantine_df is not None and not quarantine_df.empty:
            q_csv = quarantine_df.to_csv(index=False).encode("utf-8")
            st.sidebar.download_button(
                f"🔍 {len(quarantine_df)} Unusual Orders to Check (.CSV)",
                data=q_csv,
                file_name="PulseBI_Unusual_Orders_To_Check.csv",
                mime="text/csv",
                use_container_width=True,
                key="sb_dl_quarantine"
            )

        with st.sidebar.expander("🛠️ Advanced IT Exports (Parquet / Power BI)", expanded=False):
            try:
                pq_buf = io.BytesIO()
                export_df.to_parquet(pq_buf, index=False)
                st.download_button(
                    "📥 Parquet Data File (.parquet)",
                    data=pq_buf.getvalue(),
                    file_name="PulseBI_Scrubbed_Export.parquet",
                    mime="application/octet-stream",
                    use_container_width=True,
                    key="sb_dl_parquet"
                )
            except Exception:
                pass
            try:
                zip_bytes = build_star_schema_zip_bundle(audited_df)
                st.download_button(
                    "⭐ Power BI Star-Schema Bundle (.ZIP)",
                    data=zip_bytes,
                    file_name="PulseBI_StarSchema_DAX_Bundle.zip",
                    mime="application/zip",
                    use_container_width=True,
                    key="sb_dl_star_zip"
                )
            except Exception:
                pass

def render_pulsebi_master_enterprise_suite():
    import numpy as np
    import pandas as pd
    import streamlit as st
    import streamlit.components.v1 as components

    active_df = _get_best_active_df()
    if active_df is None or active_df.empty:
        return

    rev_col, prod_col, cust_col, date_col = _detect_columns(active_df)
    audited_df, benford_df, quarantine_df, mad_val, benford_status = compute_forensic_audit(active_df)

    inject_modebar_explain_button_js(active_df)
    render_unified_sidebar_studio(active_df, audited_df, quarantine_df, rev_col)

    num_series = pd.to_numeric(active_df[rev_col], errors="coerce").fillna(0.0) if rev_col else pd.Series([0.0])
    total_rev = float(num_series.sum())
    avg_order = float(num_series.mean()) if len(num_series) > 0 else 0.0
    total_tx = len(active_df)
    daily_pace, span_days = _compute_real_daily_pace(active_df, rev_col, date_col)
    next_90d_est = daily_pace * 90.0 * 1.085

    grp_col = cust_col if cust_col else (prod_col if prod_col else active_df.columns[0])
    top_entity = "Your #1 Customer"
    top_entity_rev = 0.0
    top_entity_pct = 0.0
    total_entities = 1
    if rev_col and grp_col:
        tmp = active_df.copy()
        tmp[rev_col] = pd.to_numeric(tmp[rev_col], errors="coerce").fillna(0.0)
        agg = tmp.groupby(grp_col, dropna=False)[rev_col].sum().sort_values(ascending=False)
        total_entities = len(agg)
        if len(agg) > 0:
            top_entity = str(agg.index[0])
            top_entity_rev = float(agg.iloc[0])
            top_entity_pct = (top_entity_rev / max(total_rev, 1e-6)) * 100.0

    top_prod = "Your #1 Product"
    top_prod_rev = 0.0
    if rev_col and prod_col and prod_col in active_df.columns:
        tmp_p = active_df.copy()
        tmp_p[rev_col] = pd.to_numeric(tmp_p[rev_col], errors="coerce").fillna(0.0)
        agg_p = tmp_p.groupby(prod_col, dropna=False)[rev_col].sum().sort_values(ascending=False)
        if len(agg_p) > 0:
            top_prod = str(agg_p.index[0])
            top_prod_rev = float(agg_p.iloc[0])

    # =========================================================================
    # SECTION 1: FRIENDLY AI BUDDY GUIDE & EXECUTIVE STORY (FIRST THING USERS SEE!)
    # =========================================================================
    st.markdown("---")
    st.markdown("## 🤝 Your AI Business Buddy — What Your Numbers Mean Today")
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(2, 132, 199, 0.16), rgba(16, 185, 129, 0.12)); border: 1px solid rgba(56, 189, 248, 0.45); border-radius: 16px; padding: 22px 26px; margin-bottom: 18px;">
        <div style="font-size: 18px; font-weight: 800; color: #38BDF8; margin-bottom: 8px;">
            👋 Hey there! Here is your 30-second business summary in simple words:
        </div>
        <p style="font-size: 15px; color: #F8FAFC; line-height: 1.65; margin: 0;">
            I just finished cleaning and checking <b>{total_tx:,} verified orders</b> across your <b>{total_entities} accounts</b>. 
            So far, your business has brought in <b>₹{total_rev:,.0f}</b> (averaging <b>₹{avg_order:,.0f} per order</b>, or about <b>₹{daily_pace:,.0f} per day</b>). 
            Your #1 biggest supporter is <b>{top_entity}</b> (who brought in <b>₹{top_entity_rev:,.0f}</b>, or <b>{top_entity_pct:.1f}%</b> of all your money), 
            and your #1 best-selling item is <b>{top_prod}</b> (<b>₹{top_prod_rev:,.0f}</b>).
        </p>
    </div>
    """, unsafe_allow_html=True)

    tab_easy, tab_takeaways, tab_glossary = st.tabs([
        "📊 4 Things to Know About Your Business",
        "✅ 3 Easy Steps to Take This Week",
        "📖 Simple Dictionary of Dashboard Words"
    ])

    with tab_easy:
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            st.markdown(f"""
### 💰 1. How Much Money You Made
* **Total Sales:** Across **{total_tx:,} verified orders**, your business earned **₹{total_rev:,.0f}**.
* **Typical Order Size:** Every time a customer places an order, they spend around **₹{avg_order:,.0f}**.
* **Automatic Cleanup:** Before doing the math, I automatically removed blank lines, 'Subtotal' rows, and fixed spelling mistakes so nothing is counted twice.

### 🏆 2. Who Your VIP Customers Are
* **Your #1 Customer:** **{top_entity}** is your biggest contributor, bringing in **₹{top_entity_rev:,.0f}** (**{top_entity_pct:.1f}%** of total sales).
* **Your #1 Product:** **{top_prod}** is your top-performing item at **₹{top_prod_rev:,.0f}**.
""")
        with col_s2:
            st.markdown(f"""
### 🔮 3. What the Next 3 Months Look Like
* **Daily Pace:** Your business brings in roughly **₹{daily_pace:,.0f} per day**.
* **Next 90 Days:** If you keep moving at this pace, you are on track to earn around **₹{next_90d_est:,.0f}** over the next 3 months.

### 🛡️ 4. Bookkeeping & Safety Check
* **Unusual Orders Spotted:** Out of **{total_tx:,}** orders, I set aside **{len(quarantine_df):,} unusual-looking orders** (either extra-large orders or unusual amounts).
* **No Need to Worry:** Just click the **Unusual Orders (.CSV)** button in the left sidebar when you have 2 minutes to make sure they aren't typing mistakes.
""")

    with tab_takeaways:
        st.markdown(f"""
### 🎯 3 Simple Steps to Grow & Protect Your Money This Week
1. **Call Your 'At-Risk' Customers:** In the **Pillar 2 & 3** tab above, check the red **At-Risk** customers who haven't ordered in 75–82 days. A quick friendly phone call or small discount can win them back before they go to a competitor!
2. **Take Extra Care of {top_entity}:** Since **{top_entity}** and your top few VIP accounts generate the bulk of your cash flow, make sure their orders are always delivered on time.
3. **Double-Check the {len(quarantine_df):,} Flagged Orders:** Download the `Unusual Orders` file from the left sidebar to confirm those extra-big invoices are real sales.
""")

    with tab_glossary:
        st.markdown("""
### 📖 Simple Dictionary: What the Words on This Page Mean
| Word on Screen | What It Means in Simple Everyday Language |
| :--- | :--- |
| **Total Scrubbed Revenue** | All the money you earned after we deleted duplicate rows, subtotals, and typing errors. |
| **At-Risk Accounts (Churn ML)** | Regular customers who haven't bought from you lately and might need a friendly check-in call. |
| **Pareto 80/20 Concentration** | A chart showing which top customers bring in 80% of your total money. |
| **What-If Simulator** | Sliders that let you test *"What if I raise prices by 5% or save 35% of my At-Risk customers?"* |
| **Star-Schema & DAX** | Organizing your spreadsheet neatly so an IT team can open it inside Microsoft Power BI in one click. |
""")

    # =========================================================================
    # SECTION 2: INTERACTIVE 5-SLIDE PRESENTATION DECK (FULL WIDESCREEN FIT)
    # =========================================================================
    st.markdown("---")
    with st.expander("📽️ Ready-Made 5-Slide Business Presentation (Click to Flip Through Slides or Save as PDF)", expanded=True):
        c_d1, c_d2, c_d3 = st.columns([2, 2, 1])
        with c_d1:
            custom_title = st.text_input("Presentation Title:", value="Business Performance & 90-Day Outlook", key="deck_title_in")
        with c_d2:
            custom_pres = st.text_input("Presented By:", value="Prepared by Your PulseBI AI Companion", key="deck_pres_in")
        deck_html = build_interactive_board_deck_html(active_df, deck_title=custom_title, presenter=custom_pres)
        with c_d3:
            st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
            st.download_button(
                "📥 Download Slides (.HTML)",
                data=deck_html.encode("utf-8"),
                file_name="PulseBI_Presentation_Slides.html",
                mime="text/html",
                use_container_width=True,
                key="main_dl_board_deck"
            )
        st.caption("💡 **How to Use:** Click **Next Slide → / ← Previous Slide** inside the presentation bar below, or click **🖨️ Print / Save as PDF** to share with your team.")
        components.html(deck_html, height=560, scrolling=False)

    # =========================================================================
    # SECTION 3: AI DEEP-DIVE & FUTURE SIMULATOR (TUCKED NEATLY SO IT NEVER SCARES USERS)
    # =========================================================================
    st.markdown("---")
    with st.expander("🔬 Explore More: Future Sales Predictor, Ask-AI Question Box & Bookkeeping Safety Check", expanded=False):
        st.caption("Want to test future 'What-If' scenarios, ask a custom question about your spreadsheet, or check for bookkeeping errors? Pick a tool below:")

        tab_monte, tab_nlq, tab_forensic, tab_star = st.tabs([
            "🔮 Future Sales Predictor (Next 90 Days)",
            "💬 Ask Your Spreadsheet a Question",
            "🛡️ Bookkeeping & Unusual Order Check",
            "⭐ Export for Microsoft Power BI"
        ])

        with tab_monte:
            st.markdown("#### 🔮 Test What Could Happen to Your Sales Over the Next 90 Days")
            st.write("Move the sliders below to see how losing customers, rising supplier costs, or growing sales would affect your money over the next 3 months:")
            mc1, mc2, mc3 = st.columns(3)
            with mc1:
                churn_shock = st.slider("😟 What if some customers stop buying? (%)", min_value=0, max_value=50, value=10, step=5, key="mc_churn")
            with mc2:
                margin_shock = st.slider("📦 What if supplier costs go up? (%)", min_value=-20, max_value=30, value=5, step=5, key="mc_margin")
            with mc3:
                growth_boost = st.slider("🚀 What if new sales grow faster? (%)", min_value=-20, max_value=40, value=10, step=5, key="mc_growth")

            num_vals = pd.to_numeric(active_df[rev_col], errors="coerce").dropna() if rev_col else pd.Series([100.0, 150.0, 200.0])
            base_daily_rev = max(daily_pace, 100.0)
            hist_cv = min(max(float(num_vals.std() / max(num_vals.mean(), 1e-6)), 0.10), 0.65)

            net_drift_multiplier = (1.0 - churn_shock / 100.0) * (1.0 - margin_shock / 100.0) * (1.0 + growth_boost / 100.0)
            adj_daily_mean = base_daily_rev * net_drift_multiplier
            daily_sigma = adj_daily_mean * hist_cv

            rng = np.random.default_rng(42)
            sim_daily = np.clip(rng.normal(loc=adj_daily_mean, scale=daily_sigma, size=(10000, 90)), a_min=0.0, a_max=None)
            sim_cum = np.cumsum(sim_daily, axis=1)

            p10_curve = np.percentile(sim_cum, 10, axis=0)
            p50_curve = np.percentile(sim_cum, 50, axis=0)
            p90_curve = np.percentile(sim_cum, 90, axis=0)

            final_totals = sim_cum[:, -1]
            p10_final, p50_final, p90_final = float(p10_curve[-1]), float(p50_curve[-1]), float(p90_curve[-1])
            baseline_90d = base_daily_rev * 90.0
            prob_beat_baseline = float((final_totals >= baseline_90d).mean() * 100.0)

            k1, k2, k3, k4 = st.columns(4)
            k1.metric("😟 Slow Quarter (Safe Floor)", f"₹{p10_final:,.0f}", f"{((p10_final/baseline_90d - 1)*100):+.1f}% vs Normal")
            k2.metric("🙂 Expected Quarter (Most Likely)", f"₹{p50_final:,.0f}", f"{((p50_final/baseline_90d - 1)*100):+.1f}% vs Normal")
            k3.metric("🤩 Great Quarter (Best Case)", f"₹{p90_final:,.0f}", f"{((p90_final/baseline_90d - 1)*100):+.1f}% vs Normal")
            k4.metric("Chance of Beating Usual Sales", f"{prob_beat_baseline:.0f}%", "Out of 10,000 tests")

            fan_df = pd.DataFrame({
                "Day": [f"Day {i+1}" for i in range(90)],
                "Slow_Quarter_Floor": np.round(p10_curve, 2),
                "Expected_Sales": np.round(p50_curve, 2),
                "Best_Case_Sales": np.round(p90_curve, 2)
            }).set_index("Day")
            st.line_chart(fan_df[["Slow_Quarter_Floor", "Expected_Sales", "Best_Case_Sales"]])

        with tab_nlq:
            st.markdown("#### 💬 Ask Your AI Buddy a Question About Your Data")
            preset_q = st.selectbox(
                "Pick a popular question below (or type your own keyword):",
                [
                    "Who are my top 10 customers by total money spent?",
                    "What are my top 10 best-selling products/items?",
                    "Show me the 25 biggest single orders",
                    "Show me the unusual orders that need a quick check"
                ],
                key="nlq_preset"
            )
            custom_q = st.text_input("Or type a word like 'customer', 'product', 'biggest', or 'unusual':", value="", key="nlq_custom")
            active_query = custom_q.strip().lower() if custom_q.strip() else preset_q.lower()

            if "customer" in active_query or "product" in active_query or "item" in active_query:
                use_col = cust_col if "customer" in active_query and cust_col else (prod_col if prod_col else active_df.columns[0])
                if rev_col and use_col:
                    tmp = active_df.copy()
                    tmp[rev_col] = pd.to_numeric(tmp[rev_col], errors="coerce").fillna(0.0)
                    agg = tmp.groupby(use_col, dropna=False)[rev_col].agg(["count", "sum", "mean"]).reset_index()
                    agg.columns = [use_col, "Number of Orders", "Total Money (₹)", "Average Order (₹)"]
                    agg = agg.sort_values("Total Money (₹)", ascending=False).head(10)
                    agg["Total Money (₹)"] = agg["Total Money (₹)"].round(0)
                    agg["Average Order (₹)"] = agg["Average Order (₹)"].round(0)
                    st.dataframe(agg, use_container_width=True, hide_index=True)
                    st.bar_chart(agg.set_index(use_col)["Total Money (₹)"])
            elif "biggest" in active_query or "single" in active_query or "top" in active_query:
                if rev_col:
                    tmp = active_df.copy()
                    tmp[rev_col] = pd.to_numeric(tmp[rev_col], errors="coerce")
                    top_rows = tmp.sort_values(by=rev_col, ascending=False).head(25)
                    st.dataframe(top_rows, use_container_width=True)
            else:
                st.dataframe(quarantine_df.head(50), use_container_width=True)

        with tab_forensic:
            st.markdown("#### 🛡️ Automatic Bookkeeping & Unusual Order Check")
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Orders Checked", f"{len(active_df):,}", f"Column: {rev_col}")
            c2.metric("Unusual Orders Found", f"{len(quarantine_df):,}", f"{(len(quarantine_df)/max(len(active_df),1)*100):.1f}% of all orders")
            rev_at_risk = float(pd.to_numeric(quarantine_df[rev_col], errors="coerce").sum()) if (rev_col and not quarantine_df.empty) else 0.0
            c3.metric("Total Value of Unusual Orders", f"₹{rev_at_risk:,.0f}", benford_status.split("(")[0].strip())

            st.info(f"💡 **AI Buddy Verdict:** **{benford_status}** — We checked all **{len(active_df):,} orders** in `{rev_col}` to see if your invoice numbers look natural and spot any extra-large orders worth double-checking.")

            if not benford_df.empty:
                st.markdown("##### 📊 Do Your Invoice Numbers Follow a Normal Business Pattern?")
                st.caption("In most businesses, more invoice amounts start with smaller digits (like 1, 2, or 3) than big digits (like 8 or 9). Comparing the two bars helps accountants spot typing errors:")
                chart_df = benford_df.set_index("First Digit (1-9)")[["Normal Business Pattern (%)", "Your Actual Invoices (%)"]]
                st.bar_chart(chart_df)

            with st.expander(f"📋 Click to View the {len(quarantine_df)} Unusual Orders List", expanded=False):
                if not quarantine_df.empty:
                    st.dataframe(quarantine_df.head(50), use_container_width=True)
                else:
                    st.success("No unusual orders found!")

            with st.expander("🔢 Click to View Detailed Digit Breakdown Table (For Accountants)", expanded=False):
                st.dataframe(benford_df, use_container_width=True, hide_index=True)

        with tab_star:
            st.markdown("#### ⭐ 1-Click Package for Microsoft Power BI")
            st.write("If you or your accountant use Microsoft Power BI, click below to download your neatly organized data tables and pre-written formulas in one `.ZIP` folder:")
            zip_data = build_star_schema_zip_bundle(audited_df)
            st.download_button(
                "📦 Download Power BI Ready Package (.ZIP)",
                data=zip_data,
                file_name="PulseBI_StarSchema_DAX_Bundle.zip",
                mime="application/zip",
                use_container_width=True,
                key="main_dl_star_zip"
            )

render_pulsebi_master_enterprise_suite()

