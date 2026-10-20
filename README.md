<div align="center">

# ⚡ PulseBI Studio
### Autonomous BI, CFO Intelligence & Star-Schema Compiler

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%25+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red.svg)](https://streamlit.io/)
[![Gemini API](https://img.shields.io/badge/Gemini_2.5_Flash-Cognitive_Engine-cyan.svg)](https://ai.google.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/mit)

*A minimalist, zero-clutter autonomous business intelligence platform designed to outperform legacy ETL and BI tools through a Command Center aesthetic, 1-click playbooks, and state-of-the-art generative AI.*

</div>

---

## 🚀 Overview

Modern BI tools (like Julius.ai, Alteryx, and DataRobot) often suffer from **Blank-Box Paralysis** (forcing users to stare at empty chat prompts) or **Dashboard Overload** (bombarding users with 20 raw tables and metrics instantly).

**PulseBI Studio** solves this by establishing a **Two-State Autonomous Command Center**:
1. **The Minimalist Landing Gate:** Zero clutter, zero tables on launch. Users see a crisp hero title, an AI Command Bar, file dropzone, and **1-Click Role Playbooks** (*CFO Board Brief*, *Churn Radar*, *Scrub Ledger*, *Power BI Model*).
2. **The Executive Story View:** Upon upload or playbook launch, it immediately distills raw ledgers into **3 High-Impact Executive Cards** (Revenue Health, Churn Retention Radar, and Star-Schema Readiness) with 1-click exports—keeping deep-dive analyst views neatly tucked behind a progressive disclosure toggle.

---

## 🏛️ Core Architecture & 4-Pillar Pipeline

PulseBI Studio processes dirty transactional data through an instantaneous 4-stage pipeline:
* **Pillar 1 (`PulseScrub`):** Automatically strips trailing whitespaces, fixes negative/zero sales anomalies, imputes missing quantities using product medians, and applies **RapidFuzz** string similarity matching to consolidate messy merchant/customer name typos into canonical master entities.
* **Pillar 2 & 3 (`Predictive BI`):** Executes behavioral **RFM (Recency, Frequency, Monetary) scoring** and Random Forest/decision-tree classification to isolate high-risk accounts, paired with 90-day linear regression revenue forecasting.
* **Pillar 4 (`PulseStar`):** Normalizes flat transactional ledgers into a complete Kimball Star-Schema (`Fact_Transactions`, `Dim_Customers`, `Dim_Products`, `Dim_Calendar` with Indian Financial Year April–March support) and auto-compiles ready-to-paste **DAX Measures** and **Power Query (M)** scripts.

---

## ✨ Key Features & Capabilities

* **Linear/Vercel-Grade Dark Glassmorphic UI:** Built with custom CSS, Inter font typography, JetBrains Mono code styling, ambient radial gradients, and electric cyan/indigo branding.
* **Gemini 2.5 Flash Cognitive Engine:** Optional API key integration that unlocks autonomous executive board memos, anomaly detection, and natural-language data interrogation.
* **1-Click Executive Exports:**
  * Clean CSV Ledger (`PulseBI_Clean_Ledger.csv`)
  * Multi-sheet Star-Schema Excel Workbook (`PulseBI_StarSchema_Workbook.xlsx`)
  * DAX Measures File (`PulseBI_Measures.dax`)

---

## 🛠️ Quickstart & Local Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/your-username/pulsebi-studio.git](https://github.com/your-username/pulsebi-studio.git)
   cd pulsebi-studio