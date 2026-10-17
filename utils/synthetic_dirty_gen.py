"""
Synthetic Dirty Business Dataset Generator for PulseBI testing and demos.
Generates realistic B2B/Wholesale transaction records with intentional anomalies:
- Misspelled customer names (for RapidFuzz testing)
- Mixed Indian & ISO date formats
- Currency symbols & comma-formatted numbers
- Embedded 'Subtotal' and empty divider rows
- Realistic RFM & Churn patterns + seasonal upward trend
"""

import os
import random
from datetime import datetime, timedelta
import numpy as np
import pandas as pd


CUSTOMER_CLUSTERS = [
    # (Canonical Name, [Dirty Variations], Churn Probability, Base Order Value)
    ("Apex Electronics Pvt Ltd", ["Apex Electronics Pvt Ltd", "Apex Electronic Pvt. Ltd.", "Apax Electronics", "Apex Electronics"], 0.10, 45000),
    ("Zenith Industrial Supplies", ["Zenith Industrial Supplies", "Zenith Industrials", "Zenith Ind. Supplies", "Zentih Industrial Supplies"], 0.15, 62000),
    ("Bharat Hardware & Tools", ["Bharat Hardware & Tools", "Bharat Hardwares", "Bharath Hardware & Tools", "Bharat Hardware"], 0.75, 18000), # High churn risk
    ("Vanguard Retail Group", ["Vanguard Retail Group", "Vanguard Retails", "Vangaurd Retail Group", "Vanguard Retail Grp"], 0.08, 85000),
    ("Kurla Logistics & Packaging", ["Kurla Logistics & Packaging", "Kurla Logistics", "Kurla Logisitcs & Pkg", "Kurla Packaging"], 0.80, 14000), # High churn risk
    ("Deccan Polymers India", ["Deccan Polymers India", "Deccan Polymer India", "Decan Polymers", "Deccan Polymers Ind."], 0.20, 51000),
    ("Metro Office Solutions", ["Metro Office Solutions", "Metro Office Solution", "Metro Offc Solutions", "Metro Solutions"], 0.65, 22000), # High churn risk
    ("Sahyadri Agro Traders", ["Sahyadri Agro Traders", "Sahyadri Agro", "Sahyadari Agro Traders", "Sahyadri Traders"], 0.12, 39000),
    ("Western Coast Distributors", ["Western Coast Distributors", "Western Coast Dist.", "Westrn Coast Distributors", "Western Distributors"], 0.18, 73000),
    ("Pinnacle MedTech Corp", ["Pinnacle MedTech Corp", "Pinnacle Medtech", "Pinacle MedTech Corp.", "Pinnacle MedTech"], 0.05, 95000),
    ("Shree Ganesh Enterprises", ["Shree Ganesh Enterprises", "Shri Ganesh Enterprises", "Shree Ganesh Ent.", "Shree Ganesh Entp"], 0.70, 15500), # High churn risk
    ("Omega Auto Components", ["Omega Auto Components", "Omega Auto Comp.", "Omga Auto Components", "Omega Auto"], 0.25, 48000),
]

PRODUCTS = [
    ("Industrial Sensor Kit v2", 4500),
    ("Heavy-Duty Packaging Roll", 1200),
    ("Smart Power Relay Module", 3200),
    ("Precision Bearing Assembly", 2800),
    ("Thermal Label Printer Pro", 8500),
    ("High-Tensile Fastener Box", 950),
]


def _format_dirty_date(dt: datetime) -> str:
    """Randomly formats a datetime object into mixed string representations."""
    fmt_choice = random.random()
    if fmt_choice < 0.55:
        return dt.strftime("%Y-%m-%d")          # ISO: 2026-08-14
    elif fmt_choice < 0.80:
        return dt.strftime("%d/%m/%Y")          # Indian slash: 14/08/2026
    elif fmt_choice < 0.95:
        return dt.strftime("%d-%b-%Y")          # Abbrev month: 14-Aug-2026
    else:
        return dt.strftime("%Y/%m/%d %H:%M")    # Timestamp style


def _format_dirty_currency(val: float) -> str:
    """Randomly wraps numeric revenue in messy currency strings."""
    choice = random.random()
    if choice < 0.65:
        return f"{val:.2f}"
    elif choice < 0.85:
        return f"₹ {val:,.2f}"
    elif choice < 0.95:
        return f"INR {val:,.0f}"
    else:
        return f"Rs. {val:.2f}"


def generate_dirty_dataset(num_rows: int = 850, seed: int = 42) -> pd.DataFrame:
    """
    Generates a synthetic messy dataset suitable for testing ETL, RFM Churn,
    and 90-day Revenue Forecasting.
    """
    random.seed(seed)
    np.random.seed(seed)

    end_date = datetime(2026, 10, 15)
    start_date = end_date - timedelta(days=365)

    records = []

    for i in range(num_rows):
        cluster = random.choice(CUSTOMER_CLUSTERS)
        canonical_name, variations, churn_prob, base_val = cluster

        # Simulate churn behavior: high-churn customers stop ordering in the last 65 days
        if churn_prob > 0.60:
            days_offset = random.randint(0, 290)  # Stops ~75 days before end_date
        else:
            days_offset = random.randint(0, 365)

        txn_date = start_date + timedelta(days=days_offset)

        # Pick a dirty customer name variation (weighted towards canonical)
        weights = [0.65] + [0.35 / (len(variations) - 1)] * (len(variations) - 1)
        dirty_customer = random.choices(variations, weights=weights, k=1)[0]

        # Occasionally inject leading/trailing whitespace
        if random.random() < 0.15:
            dirty_customer = f"  {dirty_customer} "

        product_name, unit_price = random.choice(PRODUCTS)

        # Seasonal growth factor + day-of-week bump
        month_factor = 1.0 + (days_offset / 365.0) * 0.28
        if txn_date.month in (10, 11, 3):  # Festive & FY-end spike
            month_factor *= 1.22

        qty = max(1, int(np.random.poisson(lam=(base_val / unit_price) * 0.35 * month_factor)))
        raw_revenue = qty * unit_price * np.random.uniform(0.95, 1.05)

        # Inject occasional missing quantity (5% of rows)
        qty_cell = np.nan if random.random() < 0.05 else qty

        records.append({
            "Vch_Booking_Date": _format_dirty_date(txn_date),
            "Party_Ledger_Name": dirty_customer,
            "Item_Particulars": product_name,
            "Billed_Qty": qty_cell,
            "Gross_Invoice_INR": _format_dirty_currency(raw_revenue),
            "Region_Zone": random.choice(["West-MH", "West-GJ", "South-KA", "North-DL"]),
        })

        # Every ~120 rows, inject a messy 'Subtotal' or blank divider row
        if (i + 1) % 120 == 0:
            records.append({
                "Vch_Booking_Date": "Subtotal",
                "Party_Ledger_Name": "--- Page Subtotal ---",
                "Item_Particulars": None,
                "Billed_Qty": None,
                "Gross_Invoice_INR": "₹ 9,99,999.00",
                "Region_Zone": None,
            })
            records.append({
                "Vch_Booking_Date": None,
                "Party_Ledger_Name": None,
                "Item_Particulars": None,
                "Billed_Qty": None,
                "Gross_Invoice_INR": None,
                "Region_Zone": None,
            })

    df = pd.DataFrame(records)
    return df


if __name__ == "__main__":
    os.makedirs("sample_data", exist_ok=True)
    sample_df = generate_dirty_dataset(num_rows=900)
    output_path = os.path.join("sample_data", "dirty_b2b_sales_dump.csv")
    sample_df.to_csv(output_path, index=False)
    print(f"[PulseBI] Generated {len(sample_df)} dirty rows -> {output_path}")