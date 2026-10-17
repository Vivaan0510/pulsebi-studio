"""
Pillar 4: Power BI Star-Schema & DAX/M Compiler (PulseStar)
- Splits flat cleaned data into normalized Kimball Star-Schema tables:
  Fact_Transactions, Dim_Customers, Dim_Products, Dim_Calendar (with Indian Apr-Mar FY)
- Dynamically generates copy-pasteable Power BI DAX Measures and Power Query (M) scripts
- Packages the entire Star Schema + DAX + M scripts into an in-memory ZIP or multi-sheet XLSX
"""

from dataclasses import dataclass
import io
from typing import Dict, Optional
import zipfile
import numpy as np
import pandas as pd

from config.settings import INDIAN_FY_START_MONTH


@dataclass
class StarSchemaBundle:
    """Holds normalized Star-Schema tables and generated BI code artifacts."""
    fact_transactions: pd.DataFrame
    dim_customers: pd.DataFrame
    dim_products: pd.DataFrame
    dim_calendar: pd.DataFrame
    dax_measures_code: str
    power_query_m_code: str


def _build_indian_fy_calendar(min_date: pd.Timestamp, max_date: pd.Timestamp) -> pd.DataFrame:
    """
    Generates a continuous Kimball Dim_Calendar table supporting both
    Standard Calendar (Jan-Dec) and Indian Financial Year (Apr-Mar).
    """
    start_dt = pd.Timestamp(year=min_date.year, month=1, day=1)
    end_dt = pd.Timestamp(year=max_date.year + 1, month=3, day=31)
    dates = pd.date_range(start=start_dt, end=end_dt, freq="D")

    cal = pd.DataFrame({"Date": dates})
    cal["Date_Key"] = cal["Date"].dt.strftime("%Y%m%d").astype(int)
    cal["Calendar_Year"] = cal["Date"].dt.year
    cal["Month_Number"] = cal["Date"].dt.month
    cal["Month_Name"] = cal["Date"].dt.strftime("%b")
    cal["Year_Month"] = cal["Date"].dt.strftime("%Y-%m")
    cal["Day_Of_Week"] = cal["Date"].dt.strftime("%a")
    cal["Is_Weekend"] = cal["Date"].dt.dayofweek.isin([5, 6])

    # Indian Financial Year (April 1 to March 31)
    fy_start_year = np.where(
        cal["Month_Number"] >= INDIAN_FY_START_MONTH,
        cal["Calendar_Year"],
        cal["Calendar_Year"] - 1,
    )
    fy_end_short = (fy_start_year + 1) % 100
    cal["Indian_FY"] = [
        f"FY {sy}-{ey:02d}" for sy, ey in zip(fy_start_year, fy_end_short)
    ]

    # Indian Fiscal Quarter (FQ1 = Apr-Jun, FQ2 = Jul-Sep, FQ3 = Oct-Dec, FQ4 = Jan-Mar)
    cal["Indian_Fiscal_Quarter"] = np.select(
        [
            cal["Month_Number"].isin([4, 5, 6]),
            cal["Month_Number"].isin([7, 8, 9]),
            cal["Month_Number"].isin([10, 11, 12]),
        ],
        ["FQ1 (Apr-Jun)", "FQ2 (Jul-Sep)", "FQ3 (Oct-Dec)"],
        default="FQ4 (Jan-Mar)",
    )

    # Fiscal Month Order (April = 1 ... March = 12) for proper sorting in Power BI
    cal["Indian_FY_Month_Sort"] = np.where(
        cal["Month_Number"] >= 4,
        cal["Month_Number"] - 3,
        cal["Month_Number"] + 9,
    )

    return cal


def _generate_dax_script(schema_map: Dict[str, Optional[str]]) -> str:
    """Generates executive-ready Power BI DAX measures mapped to the Star Schema."""
    raw_rev = schema_map.get("revenue") or "Revenue"
    raw_cust = schema_map.get("customer") or "Customer"

    return f"""// =========================================================================
// PulseBI Studio — Auto-Generated Power BI DAX Measures
// Source Mapping: Revenue [{raw_rev}] | Entity [{raw_cust}]
// Model Relationships:
//   1. Dim_Calendar[Date]        (1) ---> (*) Fact_Transactions[Transaction_Date]
//   2. Dim_Customers[Customer_Key] (1) ---> (*) Fact_Transactions[Customer_Key]
//   3. Dim_Products[Product_Key]   (1) ---> (*) Fact_Transactions[Product_Key]
// =========================================================================

// --- 1. CORE KPI MEASURES ---
Total Revenue (INR) = 
    SUM ( Fact_Transactions[Revenue_INR] )

Total Billed Quantity = 
    SUM ( Fact_Transactions[Quantity] )

Total Transactions = 
    COUNTROWS ( Fact_Transactions )

Active Customers = 
    DISTINCTCOUNT ( Fact_Transactions[Customer_Key] )

Average Order Value (AOV) = 
    DIVIDE ( [Total Revenue (INR)], [Total Transactions], 0 )


// --- 2. INDIAN FINANCIAL YEAR (APR-MAR) TIME INTELLIGENCE ---
Revenue YTD (Indian FY Apr-Mar) = 
    TOTALYTD (
        [Total Revenue (INR)],
        Dim_Calendar[Date],
        "31/03"
    )

Revenue Prior Year (Same Period) = 
    CALCULATE (
        [Total Revenue (INR)],
        SAMEPERIODLASTYEAR ( Dim_Calendar[Date] )
    )

YoY Revenue Growth % = 
    VAR CurrentRev = [Total Revenue (INR)]
    VAR PriorRev = [Revenue Prior Year (Same Period)]
    RETURN
        DIVIDE ( CurrentRev - PriorRev, PriorRev, 0 )

Moving Average 30D Revenue = 
    AVERAGEX (
        DATESINPERIOD (
            Dim_Calendar[Date],
            LASTDATE ( Dim_Calendar[Date] ),
            -30,
            DAY
        ),
        [Total Revenue (INR)]
    )


// --- 3. CHURN & PARETO 80/20 EXECUTIVE INTELLIGENCE ---
Revenue at Risk (High Churn Accounts) = 
    CALCULATE (
        [Total Revenue (INR)],
        Dim_Customers[Risk_Level] = "High Risk (At-Risk)"
    )

At-Risk Customer Count = 
    CALCULATE (
        COUNTROWS ( Dim_Customers ),
        Dim_Customers[Risk_Level] = "High Risk (At-Risk)"
    )

Customer Revenue Share % = 
    DIVIDE (
        [Total Revenue (INR)],
        CALCULATE ( [Total Revenue (INR)], ALLSELECTED ( Dim_Customers ) ),
        0
    )
"""


def _generate_power_query_m_script(schema_map: Dict[str, Optional[str]]) -> str:
    """Generates a Power Query (M) script tailored to the user's exact raw column headers."""
    c_date = schema_map.get("date") or "Date"
    c_cust = schema_map.get("customer") or "Customer"
    c_prod = schema_map.get("product") or "Product"
    c_qty = schema_map.get("quantity") or "Quantity"
    c_rev = schema_map.get("revenue") or "Revenue"

    return f"""// =========================================================================
// PulseBI Studio — Auto-Generated Power Query (M) Transformation Script
// Paste into Power BI Desktop -> Home -> Transform Data -> Advanced Editor
// =========================================================================
let
    // 1. Load Raw CSV / Excel Source
    Source = Csv.Document(
        File.Contents("C:\\path\\to\\your_raw_data.csv"),
        [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.None]
    ),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),

    // 2. Remove Blank & Embedded 'Subtotal / Total' Summary Rows
    RemovedBlankRows = Table.SelectRows(
        PromotedHeaders,
        each not List.IsEmpty(List.RemoveMatchingItems(Record.FieldValues(_), {{"", null}}))
    ),
    RemovedSubtotals = Table.SelectRows(
        RemovedBlankRows,
        each not Text.Contains(Text.Lower(Text.From(_[{c_date}] ?? "")), "total")
         and not Text.Contains(Text.Lower(Text.From(_[{c_cust}] ?? "")), "subtotal")
    ),

    // 3. Clean Currency Symbols (₹, INR, Rs., Commas) on [{c_rev}]
    CleanedCurrencyText = Table.TransformColumns(
        RemovedSubtotals,
        {{
            "{c_rev}",
            each Text.Trim(
                Text.Replace(
                    Text.Replace(
                        Text.Replace(
                            Text.Replace(Text.From(_ ?? "0"), "₹", ""),
                        "INR", ""),
                    "Rs.", ""),
                ",", "")
            ),
            type text
        }}
    ),

    // 4. Trim & Normalize Entity Names on [{c_cust}]
    TrimmedEntities = Table.TransformColumns(
        CleanedCurrencyText,
        {{"{c_cust}", each Text.Clean(Text.Trim(Text.From(_ ?? "Unknown Entity"))), type text}}
    ),

    // 5. Enforce Canonical BI Data Types
    TypedTable = Table.TransformColumnTypes(
        TrimmedEntities,
        {{
            {{"{c_date}", type date}},
            {{"{c_cust}", type text}},
            {{"{c_prod}", type text}},
            {{"{c_qty}", Int64.Type}},
            {{"{c_rev}", Currency.Type}}
        }},
        "en-IN"
    ),

    // 6. Rename to PulseBI Canonical Schema
    RenamedColumns = Table.RenameColumns(
        TypedTable,
        {{
            {{"{c_date}", "Transaction_Date"}},
            {{"{c_cust}", "Customer_Name"}},
            {{"{c_prod}", "Product_Name"}},
            {{"{c_qty}", "Quantity"}},
            {{"{c_rev}", "Revenue_INR"}}
        }}
    )
in
    RenamedColumns
"""


def compile_star_schema(
    clean_df: pd.DataFrame,
    rfm_df: pd.DataFrame,
    schema_map: Dict[str, Optional[str]],
) -> StarSchemaBundle:
    """
    Splits the scrubbed dataset and RFM predictions into a normalized
    4-table Star Schema + DAX & Power Query (M) code bundle.
    """
    df = clean_df.copy()

    # 1. Build Dim_Customers (enriched with RFM & Churn ML outputs)
    cust_cols = [
        "_customer",
        "RFM_Segment",
        "RFM_Score",
        "Recency_Days",
        "Frequency",
        "Monetary",
        "Avg_Order_Value",
        "Churn_Probability",
        "Risk_Level",
        "Risk_Explanation",
    ]
    available_cust_cols = [c for c in cust_cols if c in rfm_df.columns]
    dim_cust = rfm_df[available_cust_cols].copy()
    dim_cust = dim_cust.rename(columns={"_customer": "Customer_Name"})
    dim_cust = dim_cust.sort_values("Customer_Name").reset_index(drop=True)
    dim_cust.insert(0, "Customer_Key", [f"CUST-{i+1001}" for i in range(len(dim_cust))])

    cust_key_map = dict(zip(dim_cust["Customer_Name"], dim_cust["Customer_Key"]))

    # 2. Build Dim_Products
    total_rev = max(1.0, float(df["_revenue"].sum()))
    prod_agg = (
        df.groupby("_product", as_index=False)
        .agg(
            Total_Units_Sold=("_quantity", "sum"),
            Total_Revenue_INR=("_revenue", "sum"),
            Transaction_Count=("_date", "count"),
        )
        .sort_values("Total_Revenue_INR", ascending=False)
        .reset_index(drop=True)
    )
    prod_agg = prod_agg.rename(columns={"_product": "Product_Name"})
    prod_agg.insert(0, "Product_Key", [f"PROD-{i+101}" for i in range(len(prod_agg))])
    prod_agg["Avg_Unit_Price_INR"] = (
        prod_agg["Total_Revenue_INR"] / np.maximum(1, prod_agg["Total_Units_Sold"])
    ).round(2)
    prod_agg["Revenue_Share_Pct"] = (
        (prod_agg["Total_Revenue_INR"] / total_rev) * 100.0
    ).round(2)

    prod_key_map = dict(zip(prod_agg["Product_Name"], prod_agg["Product_Key"]))

    # 3. Build Dim_Calendar (with Indian FY Apr-Mar columns)
    dim_cal = _build_indian_fy_calendar(df["_date"].min(), df["_date"].max())

    # 4. Build Fact_Transactions
    fact = pd.DataFrame()
    fact["Transaction_ID"] = [f"TXN-{i+10001}" for i in range(len(df))]
    fact["Date_Key"] = df["_date"].dt.strftime("%Y%m%d").astype(int)
    fact["Transaction_Date"] = df["_date"].dt.strftime("%Y-%m-%d")
    fact["Customer_Key"] = df["_customer"].map(cust_key_map).fillna("CUST-0000")
    fact["Product_Key"] = df["_product"].map(prod_key_map).fillna("PROD-000")
    fact["Quantity"] = df["_quantity"].astype(int)
    fact["Revenue_INR"] = df["_revenue"].round(2)

    # Preserve extra domain columns (e.g., Region_Zone) if present in raw dataset
    mapped_raw_cols = set(v for v in schema_map.values() if v)
    internal_cols = {"_date", "_customer", "_customer_raw", "_product", "_quantity", "_revenue"}
    extra_cols = [
        c for c in df.columns if c not in mapped_raw_cols and c not in internal_cols
    ]
    for col in extra_cols:
        fact[col] = df[col].values

    dax_code = _generate_dax_script(schema_map)
    m_code = _generate_power_query_m_script(schema_map)

    return StarSchemaBundle(
        fact_transactions=fact,
        dim_customers=dim_cust,
        dim_products=prod_agg,
        dim_calendar=dim_cal,
        dax_measures_code=dax_code,
        power_query_m_code=m_code,
    )


def export_star_schema_zip(bundle: StarSchemaBundle) -> bytes:
    """Packages all 4 Star-Schema CSVs + DAX + Power Query M into a downloadable ZIP archive."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(
            "Fact_Transactions.csv",
            bundle.fact_transactions.to_csv(index=False).encode("utf-8"),
        )
        zf.writestr(
            "Dim_Customers.csv",
            bundle.dim_customers.to_csv(index=False).encode("utf-8"),
        )
        zf.writestr(
            "Dim_Products.csv",
            bundle.dim_products.to_csv(index=False).encode("utf-8"),
        )
        zf.writestr(
            "Dim_Calendar_Indian_FY.csv",
            bundle.dim_calendar.to_csv(index=False).encode("utf-8"),
        )
        zf.writestr(
            "PulseBI_PowerBI_Measures.dax",
            bundle.dax_measures_code.encode("utf-8"),
        )
        zf.writestr(
            "PulseBI_PowerQuery_Cleanse.pq",
            bundle.power_query_m_code.encode("utf-8"),
        )
    buffer.seek(0)
    return buffer.getvalue()


def export_star_schema_excel(bundle: StarSchemaBundle) -> bytes:
    """Packages all 4 Star-Schema tables into a clean multi-sheet Excel (.xlsx) workbook."""
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        bundle.fact_transactions.to_excel(writer, sheet_name="Fact_Transactions", index=False)
        bundle.dim_customers.to_excel(writer, sheet_name="Dim_Customers", index=False)
        bundle.dim_products.to_excel(writer, sheet_name="Dim_Products", index=False)
        bundle.dim_calendar.to_excel(writer, sheet_name="Dim_Calendar_FY", index=False)
    buffer.seek(0)
    return buffer.getvalue()