"""
Pillar 1 UI: Automated ETL Audit View & Fuzzy Deduplication Inspector (PulseScrub)
"""

from typing import Dict, Optional
import pandas as pd
import streamlit as st

from core.data_scrubber import ScrubAuditReport


def render_etl_audit_view(
    raw_df: pd.DataFrame,
    clean_df: pd.DataFrame,
    schema_map: Dict[str, Optional[str]],
    report: ScrubAuditReport,
) -> None:
    """Renders the Pillar 1 ETL Audit dashboard, Fuzzy Merge Log, and Clean CSV exporter."""
    st.subheader("🧹 Pillar 1: Automated Dirty Excel/CSV Scrubber (`PulseScrub`)")

    # 1. Top-Level Audit KPI Cards
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric(
        "Raw -> Clean Rows",
        f"{report.final_row_count:,}",
        f"-{report.initial_row_count - report.final_row_count} junk rows stripped",
    )
    c2.metric(
        "Subtotals & Blanks Stripped",
        f"{report.empty_rows_removed + report.junk_subtotal_rows_removed}",
        f"{report.junk_subtotal_rows_removed} subtotals | {report.empty_rows_removed} blanks",
    )
    c3.metric(
        "Currency Cells Scrubbed",
        f"{report.currency_cells_cleaned:,}",
        "₹ / INR / Commas normalized",
    )
    c4.metric(
        "Missing Qty Imputed",
        f"{report.missing_quantities_imputed:,}",
        "Via Product Median Unit Price",
    )
    c5.metric(
        "Canonical Entities (RapidFuzz)",
        f"{report.unique_entities_after}",
        f"From {report.unique_entities_before} dirty variations ({report.fuzzy_replacements_count} cells fixed)",
    )

    # 2. Schema Mapping & RapidFuzz Merge Inspector
    col_left, col_right = st.columns([1, 1.3])

    with col_left:
        st.markdown("#### 🧭 Universal Schema Auto-Mapper")
        schema_rows = [
            {"Canonical BI Role": role.upper(), "Detected Raw Column": col or "⚠️ Not Detected"}
            for role, col in schema_map.items()
        ]
        st.dataframe(
            pd.DataFrame(schema_rows),
            use_container_width=True,
            hide_index=True,
        )

    with col_right:
        st.markdown("#### 🔗 RapidFuzz Entity Deduplication Audit Log")
        if report.fuzzy_merge_map:
            merge_df = pd.DataFrame(
                [
                    {"Dirty Raw Spelling": dirty, "Canonical Master Entity": canon}
                    for dirty, canon in report.fuzzy_merge_map.items()
                ]
            ).sort_values("Canonical Master Entity")
            st.dataframe(merge_df, use_container_width=True, height=210, hide_index=True)
        else:
            st.info("No misspelled entity variations detected at current threshold.")

    # 3. Side-by-Side Before & After Data Preview + Download
    with st.expander("🔍 Inspect Before vs. After Scrubbed Dataset (Sample 50 Rows)", expanded=False):
        b_col, a_col = st.columns(2)
        with b_col:
            st.caption("**Raw Dirty Input (incl. mixed dates, ₹ strings, typos & subtotals)**")
            st.dataframe(raw_df.head(50), use_container_width=True, height=260)
        with a_col:
            st.caption("**Scrubbed Canonical Output**")
            preview_cols = ["_date", "_customer", "_customer_raw", "_product", "_quantity", "_revenue"]
            avail_preview = [c for c in preview_cols if c in clean_df.columns]
            st.dataframe(clean_df[avail_preview].head(50), use_container_width=True, height=260)

    csv_bytes = clean_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download Scrubbed & Deduplicated Dataset (.CSV)",
        data=csv_bytes,
        file_name="PulseBI_Scrubbed_Transactions.csv",
        mime="text/csv",
    )