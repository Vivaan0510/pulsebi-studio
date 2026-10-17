"""
Sidebar Navigation, Universal File Loader (Multi-Encoding CSV & Multi-Sheet Excel),
and Hyperparameter Controls for PulseBI Studio.
"""

from dataclasses import dataclass
import io
from typing import Optional
import pandas as pd
import streamlit as st

from config.settings import DEFAULT_FUZZY_THRESHOLD
from utils.synthetic_dirty_gen import generate_dirty_dataset


@dataclass
class SidebarConfig:
    """Holds user-selected settings and uploaded/generated raw DataFrame."""
    raw_df: Optional[pd.DataFrame]
    dataset_name: str
    fuzzy_threshold: int
    ml_model_choice: str
    inactivity_days: int
    forecast_horizon: int
    enable_exec_dashboard: bool
    enable_star_compiler: bool
    gemini_api_key: str


def _universal_read_csv(file_bytes: bytes) -> pd.DataFrame:
    """Tries UTF-8, UTF-8-SIG, CP1252, and Latin-1 with automatic delimiter sniffing."""
    for encoding in ["utf-8", "utf-8-sig", "cp1252", "latin1", "utf-16"]:
        try:
            return pd.read_csv(
                io.BytesIO(file_bytes),
                encoding=encoding,
                sep=None,
                engine="python",
                on_bad_lines="skip",
            )
        except Exception:
            try:
                return pd.read_csv(
                    io.BytesIO(file_bytes),
                    encoding=encoding,
                    low_memory=False,
                    on_bad_lines="skip",
                )
            except Exception:
                continue
    raise ValueError("Unable to decode CSV file with standard encodings.")


def render_sidebar() -> SidebarConfig:
    """Renders the PulseBI control sidebar and returns active configuration."""
    with st.sidebar:
        st.markdown("## ⚡ **PulseBI Studio**")
        st.caption("Zero-Code ETL • Predictive ML • Star-Schema Compiler")
        st.divider()

        # 1. Data Source Selection
        st.markdown("### 📂 1. Data Source")
        source_mode = st.radio(
            "Select Input Mode:",
            options=["🧪 Built-in Dirty B2B Demo Data", "📤 Upload Custom CSV / Excel"],
            index=0,
        )

        raw_df: Optional[pd.DataFrame] = None
        dataset_name = "dirty_b2b_sales_dump.csv"

        if source_mode == "🧪 Built-in Dirty B2B Demo Data":
            col1, col2 = st.columns(2)
            with col1:
                demo_rows = st.number_input("Base Rows", 50, 50000, 900, step=250)
            with col2:
                demo_seed = st.number_input("Random Seed", 1, 999, 42, step=1)

            raw_df = generate_dirty_dataset(num_rows=int(demo_rows), seed=int(demo_seed))
            dataset_name = f"Synthetic_Dirty_B2B_{demo_rows}rows.csv"
            st.success(f"Loaded {len(raw_df):,} dirty rows (incl. subtotals & typos)")
        else:
            uploaded_file = st.file_uploader(
                "Upload Any Clean or Dirty CSV / Excel",
                type=["csv", "xlsx", "xls", "tsv"],
            )
            if uploaded_file is not None:
                dataset_name = uploaded_file.name
                raw_bytes = uploaded_file.getvalue()
                try:
                    if dataset_name.lower().endswith((".csv", ".tsv")):
                        raw_df = _universal_read_csv(raw_bytes)
                    else:
                        xls = pd.ExcelFile(io.BytesIO(raw_bytes))
                        if len(xls.sheet_names) > 1:
                            selected_sheet = st.selectbox(
                                "📑 Select Excel Worksheet:", options=xls.sheet_names
                            )
                        else:
                            selected_sheet = xls.sheet_names[0]
                        raw_df = pd.read_excel(io.BytesIO(raw_bytes), sheet_name=selected_sheet)
                    st.success(f"Loaded '{dataset_name}' ({len(raw_df):,} rows × {len(raw_df.columns)} cols)")
                except Exception as exc:
                    st.error(f"Error reading file: {exc}")

        st.divider()

        # 2. Pillar Module Toggles
        st.markdown("### 🎛️ 2. Active Suite Pillars")
        enable_exec_dashboard = st.toggle(
            "📊 Pillar 3: Instant Executive Dashboard & What-If Simulator",
            value=True,
        )
        enable_star_compiler = st.toggle(
            "⭐ Pillar 4: Power BI Star-Schema & DAX Compiler",
            value=True,
        )

        st.divider()

        # 3. ETL & ML Hyperparameters
        st.markdown("### ⚙️ 3. ETL & ML Controls")
        fuzzy_threshold = st.slider(
            "RapidFuzz Entity Match Threshold",
            min_value=60,
            max_value=100,
            value=DEFAULT_FUZZY_THRESHOLD,
            step=1,
            help="Set to 75 for aggressive B2B typo merging, or 100 to disable fuzzy deduplication on already-clean IDs.",
        )

        ml_model_choice = st.selectbox(
            "Churn Classifier Architecture",
            options=["RandomForest", "DecisionTree"],
            index=0,
        )

        inactivity_days = st.slider(
            "Churn Inactivity Cutoff (Days)",
            min_value=15,
            max_value=180,
            value=45,
            step=5,
        )

        forecast_horizon = st.select_slider(
            "Revenue Forecast Horizon (Days)",
            options=[30, 60, 90],
            value=90,
        )

        with st.expander("🔑 Optional: Gemini AI Schema Assist"):
            gemini_api_key = st.text_input(
                "Gemini API Key (Tier-2 Header Fallback)",
                type="password",
                placeholder="Paste AI Studio Key (Optional)",
            )

        return SidebarConfig(
            raw_df=raw_df,
            dataset_name=dataset_name,
            fuzzy_threshold=fuzzy_threshold,
            ml_model_choice=ml_model_choice,
            inactivity_days=inactivity_days,
            forecast_horizon=forecast_horizon,
            enable_exec_dashboard=enable_exec_dashboard,
            enable_star_compiler=enable_star_compiler,
            gemini_api_key=gemini_api_key,
        )