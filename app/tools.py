# app/tools.py
import csv, io
from typing import List, Dict
import httpx
import os

def parse_csv_bytes(content: bytes) -> List[Dict]:
    text = content.decode("utf-8", errors="ignore")
    reader = csv.DictReader(io.StringIO(text))
    rows = [dict(row) for row in reader]
    return rows

# Mock market data tool - replace with real OpenAPI / httpx calls if desired
def get_market_quote(symbol: str) -> Dict:
    # Mock: returns a deterministic price for demo
    base = sum(ord(c) for c in symbol) % 1000
    price = round(10 + base / 10.0, 2)
    return {"symbol": symbol.upper(), "price": price}
