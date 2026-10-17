# ⚡ PulseBI Studio — Auto-Prep ETL, Predictive BI & Star-Schema Suite

[![Python 3.14+](https://img.shields.io/badge/Python-3.14%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Scikit-Learn](https://img.shields.io/badge/ML-Scikit--Learn-F7931E?logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![RapidFuzz](https://img.shields.io/badge/Fuzzy_ETL-RapidFuzz_C%2B%2B-00C7B7)](https://github.com/maxbachmann/RapidFuzz)
[![Power BI Ready](https://img.shields.io/badge/BI_Compiler-Star_Schema_%26_DAX-F2C811)](https://powerbi.microsoft.com/)

**PulseBI Studio** is an end-to-end **Automated Data Preparation (ETL), Explainable Predictive Business Modelling, Interactive What-If Simulation, and Power BI Star-Schema Compiler** built for B2B enterprises, analysts, and finance teams.

> 🔗 **Ecosystem Companion (Part 1):** Pair PulseBI with [**VaultSheet Air-Gap (`vaultsheet-airgap`)**](https://github.com/Vivaan0510/vaultsheet-airgap) for 100% offline PDF financial statement extraction and automated accounting audit checks.

---

## 🚀 The 4 Core Pillars of PulseBI Studio

### 🧹 Pillar 1: Universal "Dirty Excel/CSV" Scrubber (`PulseScrub`)
* **Universal Schema Auto-Mapper:** Automatically maps arbitrary ERP/Tally/SAP column headers (`Vch_Booking_Date`, `Party_Ledger_Name`, `Gross_Invoice_INR`, or even anonymous `Col_1`, `Col_2` headers) to canonical BI roles (`DATE`, `CUSTOMER`, `PRODUCT`, `QUANTITY`, `REVENUE`) using hybrid token heuristics, statistical data-type profiling, and optional **Google Gemini 2.5 Flash** assist.
* **Interactive Manual Schema Override:** Allows 1-click remapping of any column directly from the UI.
* **Automated Row & Cell Hygiene:**
  * Auto-detects buried header rows in messy corporate Excel exports.
  * Strips blank divider rows and embedded `"Subtotal / Grand Total / Carried Forward"` summary lines.
  * Standardizes mixed Indian (`DD/MM/YYYY`, `DD-MMM-YYYY`), ISO (`YYYY-MM-DD`), and Excel serial dates (`45900`).
  * Cleans multi-currency strings (`₹`, `$`, `€`, `£`, `INR`, `Rs.`, commas, and accounting parentheses `(1,200.00)`).
  * Vectorized imputation of missing quantities using product-level median unit pricing.
* **High-Speed Entity Deduplication (`RapidFuzz`):** Clusters and merges misspelled customer/vendor names (e.g., `"Pinacle MedTech Corp."` $\rightarrow$ `"Pinnacle MedTech Corp"`) using frequency-weighted canonical selection and prefix-blocking to scale seamlessly from 10 rows to **1,000,000+ rows**.

---

### 🧠 Pillar 2: Built-In Explainable Predictive BI (`PulsePredict`)
* **RFM Segmentation & Behavioral Velocity:** Computes Recency, Frequency, Monetary (RFM) scores alongside **Average Inter-Purchase Interval (IPI)** and **Overdue Ratio** to segment accounts into *Champions, Loyal Accounts, Promising, Need Attention,* and *At-Risk (High Value)*.
* **Explainable Churn ML (`Scikit-Learn`):** Trains a Random Forest or Decision Tree Classifier to score customer churn probability (`0–100%`), calculate **Revenue at Risk (₹)**, and generate human-readable **Explainable Risk Reasons** per account (e.g., *"Inactive for 82 days + 23.8x past normal reorder cycle"*).
* **Seasonal Revenue Forecasting (30 / 60 / 90 Days):** Engineers Fourier seasonal harmonics, Indian festive/FY-end spikes, and rolling structural trends to project daily revenue run-rates with **90% confidence intervals** via Ridge Regression.

---

### 📊 Pillar 3: Instant Executive Dashboard & What-If Profit Simulator (`PulseBoard`)
* **Executive Plotly Visuals:** Interactive 90-Day Forecast Curve, **Pareto 80/20 Customer Concentration Chart**, RFM Risk Bar Matrix, and Top Product Breakdown.
* **Interactive "What-If" Margin & Retention Simulator:** Real-time sensitivity sliders for **Price Change (%)**, **At-Risk Churn Saved (%)**, **Baseline Gross Margin (%)**, and **Price Elasticity** with a live **Executive Revenue Bridge Waterfall Chart**.
* **1-Click Standalone Offline HTML Exporter:** Compiles all KPI cards, interactive Plotly charts, and the Top-100 Churn Watchlist into a single self-contained `.html` file shareable offline with clients and executives.

---

### ⭐ Pillar 4: Power BI Star-Schema & DAX / Power Query Compiler (`PulseStar`)
* **Automated Kimball Star-Schema Splitter:** Transforms flat tables into 4 normalized tables linked via surrogate keys:
  1. `Fact_Transactions`
  2. `Dim_Customers` (enriched with RFM & Churn ML predictions)
  3. `Dim_Products` (with unit prices & revenue share %)
  4. `Dim_Calendar` (built-in **Indian Financial Year Apr–Mar** `FY 2025-26` & `FQ1–FQ4` support)
* **Dynamic Code Generation:** Auto-generates copy-pasteable **Power BI DAX Measures (`.dax`)** and **Power Query (`M` / `.pq`)** scripts tailored to the uploaded dataset's exact raw column names.
* **1-Click Exports:** Download as a complete `.ZIP` bundle (4 CSVs + `.dax` + `.pq`) or a multi-sheet `.XLSX` workbook.

---

## 🛠️ Quickstart & Installation

```bash
# 1. Clone the repository
git clone [https://github.com/Vivaan0510/pulsebi-studio.git](https://github.com/Vivaan0510/pulsebi-studio.git)
cd pulsebi-studio

# 2. Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\activate   # Windows PowerShell
# source .venv/bin/activate # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. (Optional) Generate synthetic dirty B2B test dataset
python utils/synthetic_dirty_gen.py

# 5. Launch PulseBI Studio
streamlit run app.py