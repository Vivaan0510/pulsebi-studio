"""
Pillar 1A: Universal Schema Auto-Mapper (PulseScrub Enterprise Edition)
Maps arbitrary raw CSV/Excel column headers to canonical BI roles:
['date', 'customer', 'product', 'quantity', 'revenue']
Combines:
  1. Keyword & RapidFuzz Header Matching
  2. Statistical Data-Content & Cardinality Profiling (works even on 'Column1', 'Column2')
  3. Optional Gemini AI Tier-2 Assist
"""

import json
import re
from typing import Dict, Optional
import numpy as np
import pandas as pd
from rapidfuzz import fuzz

from config.settings import SCHEMA_KEYWORDS


def _clean_header(col_name: str) -> str:
    """Normalizes column header string for token matching."""
    return re.sub(r"[^a-z0-9]+", "_", str(col_name).strip().lower()).strip("_")


def auto_map_schema(df: pd.DataFrame) -> Dict[str, Optional[str]]:
    """
    Universal heuristic + statistical data-profiling column matcher.
    Works on both named corporate schemas and anonymous headers.
    """
    mapping: Dict[str, Optional[str]] = {
        "date": None,
        "customer": None,
        "product": None,
        "quantity": None,
        "revenue": None,
    }

    if df is None or df.empty:
        return mapping

    available_cols = list(df.columns)
    used_cols = set()

    # Pre-sample up to 200 non-null rows for ultra-fast profiling even on 1M+ row datasets
    sample_df = df.dropna(how="all").head(200)

    # Pass 1: Hybrid Header + Content Scoring
    for role, keywords in SCHEMA_KEYWORDS.items():
        best_col = None
        best_score = 0.0

        for col in available_cols:
            if col in used_cols:
                continue

            clean_col = _clean_header(col)
            col_tokens = set(clean_col.split("_"))

            # 1. Header Token Score
            token_score = 0.0
            for kw in keywords:
                if kw == clean_col:
                    token_score = max(token_score, 100.0)
                elif kw in col_tokens:
                    token_score = max(token_score, 90.0)
                else:
                    ratio = fuzz.partial_ratio(kw, clean_col)
                    if ratio >= 82:
                        token_score = max(token_score, ratio * 0.85)

            # 2. Statistical Data Content Boost
            s = sample_df[col].dropna().astype(str).str.strip()
            content_boost = 0.0

            if len(s) > 0:
                if role == "date":
                    date_like = s.str.contains(
                        r"(?:\d{1,4}[-/\.]\w{1,3}[-/\.]\d{1,4}|\b20\d{2}\b)", regex=True
                    ).mean()
                    if date_like > 0.5:
                        content_boost = 45.0
                elif role == "revenue":
                    curr_like = s.str.contains(
                        r"(?:₹|\$|€|£|inr|usd|rs\.?|\d+,\d{2,3}|\d+\.\d{2})",
                        flags=re.IGNORECASE,
                        regex=True,
                    ).mean()
                    if curr_like > 0.4:
                        content_boost = 35.0
                elif role == "quantity":
                    num_clean = pd.to_numeric(
                        s.str.replace(r"[,₹$]", "", regex=True), errors="coerce"
                    )
                    valid_ratio = num_clean.notna().mean()
                    if valid_ratio > 0.7:
                        median_val = num_clean.median()
                        if 0 < median_val < 1000:
                            content_boost = 25.0

            total_score = token_score + content_boost
            if total_score > best_score and total_score >= 45.0:
                best_score = total_score
                best_col = col

        if best_col:
            mapping[role] = best_col
            used_cols.add(best_col)

    # Pass 2: Pure Statistical Fallback for any unmapped critical roles (e.g. anonymous headers)
    rem_cols = [c for c in available_cols if c not in used_cols]

    # Fallback for Revenue: pick remaining numeric column with largest sum/mean
    if mapping["revenue"] is None and rem_cols:
        best_rev_col, max_mean = None, -1.0
        for col in rem_cols:
            s_num = pd.to_numeric(
                sample_df[col]
                .astype(str)
                .str.replace(r"[^0-9.-]", "", regex=True),
                errors="coerce",
            )
            if s_num.notna().mean() > 0.6 and s_num.mean() > max_mean:
                max_mean = float(s_num.mean())
                best_rev_col = col
        if best_rev_col:
            mapping["revenue"] = best_rev_col
            used_cols.add(best_rev_col)
            rem_cols.remove(best_rev_col)

    # Fallback for Customer & Product: pick categorical text columns by cardinality
    text_cols = []
    for col in rem_cols:
        s = sample_df[col].dropna().astype(str)
        if len(s) > 0:
            is_num = pd.to_numeric(s, errors="coerce").notna().mean()
            if is_num < 0.3:  # Primarily text
                text_cols.append((col, s.nunique()))

    text_cols.sort(key=lambda x: x[1], reverse=True)
    if mapping["customer"] is None and text_cols:
        mapping["customer"] = text_cols[0][0]
        used_cols.add(text_cols[0][0])
        text_cols.pop(0)
    if mapping["product"] is None and text_cols:
        mapping["product"] = text_cols[0][0]
        used_cols.add(text_cols[0][0])

    return mapping


def gemini_assist_schema_map(
    df: pd.DataFrame, api_key: str
) -> Dict[str, Optional[str]]:
    """Optional Tier-2 Fallback using Gemini 2.5 Flash."""
    base_map = auto_map_schema(df)
    if not api_key or df is None or df.empty:
        return base_map

    try:
        from google import genai

        client = genai.Client(api_key=api_key)
        sample_payload = df.dropna(how="all").head(3).to_dict(orient="records")
        prompt = (
            "You are a BI Schema Mapper. Map the following dataset columns to these exact 5 canonical keys: "
            '["date", "customer", "product", "quantity", "revenue"]. '
            "Return ONLY valid JSON mapping each canonical key to the exact column name from the list, or null if absent.\n\n"
            f"Columns: {list(df.columns)}\n"
            f"Sample Rows: {json.dumps(sample_payload, default=str)}"
        )
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        raw_text = response.text.strip().strip("```json").strip("```").strip()
        ai_map = json.loads(raw_text)

        valid_cols = set(df.columns)
        for role in base_map:
            candidate = ai_map.get(role)
            if candidate in valid_cols:
                base_map[role] = candidate
        return base_map
    except Exception:
        return base_map