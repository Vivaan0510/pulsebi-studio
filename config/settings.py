"""
Global configuration, heuristic schema dictionaries, and Indian FY settings for PulseBI.
"""

APP_TITLE = "PulseBI — Auto-Prep, Predictive BI & Executive Studio"
APP_VERSION = "1.0.0"

# Heuristic keyword banks for Universal Schema Auto-Mapper
SCHEMA_KEYWORDS = {
    "date": [
        "date", "txn_date", "transaction_date", "invoice_date", "bill_date",
        "order_date", "created_at", "timestamp", "posting_date", "vch_date"
    ],
    "customer": [
        "customer", "client", "party", "party_name", "buyer", "account",
        "vendor", "entity", "customer_name", "billed_to", "consignee", "ledger"
    ],
    "product": [
        "product", "item", "sku", "category", "service", "description",
        "particulars", "material", "stock_item", "brand", "sub_category"
    ],
    "quantity": [
        "qty", "quantity", "units", "volume", "pcs", "nos", "count",
        "billed_qty", "shipped_qty"
    ],
    "revenue": [
        "revenue", "amount", "sales", "total", "net_amount", "gross_amount",
        "invoice_value", "turnover", "value", "price", "line_total", "inr"
    ],
}

# Keywords indicating summary/junk rows in messy Excel sheets
JUNK_ROW_PATTERNS = [
    r"^total\b",
    r"^sub\s*total\b",
    r"^grand\s*total\b",
    r"^carried\s*forward\b",
    r"^brought\s*forward\b",
    r"^page\s*\d+",
    r"^generated\s*on",
]

# Default Fuzzy Deduplication Threshold (0-100)
DEFAULT_FUZZY_THRESHOLD = 75

# Indian Financial Year Start Month (April = 4)
INDIAN_FY_START_MONTH = 4