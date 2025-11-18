"""
Create test data for backend testing.
This creates sample fund data with rating = 5 for testing purposes.
"""

import json
import os
from datetime import datetime

# Create data directory
os.makedirs("data", exist_ok=True)

# Test data for ICICI Prudential Large Cap Fund
test_fund = {
    "fund_id": "test_large_cap_001",
    "fund_name": "ICICI Prudential Large Cap Fund Direct Growth",
    "source_url": "https://groww.in/mutual-funds/icici-prudential-large-cap-fund-direct-growth",
    "scraped_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    "last_updated": datetime.now().isoformat(),
    "expense_ratio": {
        "value": 0.85,
        "unit": "%",
        "display": "0.85%"
    },
    "exit_load": {
        "value": 1.0,
        "unit": "%",
        "period": "1",
        "display": "1% if redeemed within 1 year"
    },
    "minimum_sip": {
        "value": 100,
        "unit": "INR",
        "display": "₹100"
    },
    "lock_in": None,
    "rating": {
        "value": 5,
        "display": "5",
        "max_rating": 5
    },
    "riskometer": {
        "value": "very high",
        "display": "Very High"
    },
    "benchmark": {
        "value": "NIFTY 100 Total Return Index",
        "display": "NIFTY 100 Total Return Index"
    },
    "statement_download": {
        "available": True,
        "instructions": ["Statements can be downloaded from ICICI Prudential AMC website or registrar portal (CAMS/Karvy)"],
        "display": "Available - Check ICICI Prudential AMC website or registrar portal"
    }
}

# Save to funds_data.json
funds_data = [test_fund]
with open("data/funds_data.json", "w", encoding="utf-8") as f:
    json.dump(funds_data, f, indent=2, ensure_ascii=False)

print("[OK] Created test data: data/funds_data.json")

# Export RAG data
from data_storage import DataStorage
storage = DataStorage()
rag_file = storage.export_for_rag()
print(f"[OK] Exported RAG data: {rag_file}")

print("\n[OK] Test data created successfully!")
print("You can now run: python setup_backend.py")


