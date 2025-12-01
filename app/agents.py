# app/agents.py
import asyncio
from typing import List, Dict
from .tools import get_market_quote
from structlog import get_logger

log = get_logger()

async def ingest_agent(rows: List[Dict]) -> List[Dict]:
    """
    Normalize rows -> transactions. Rule-based categorizer + simple heuristics.
    """
    normalized = []
    for r in rows:
        # robust extraction with defaults
        date = r.get("date") or r.get("Date") or r.get("transaction_date") or ""
        amount_raw = r.get("amount") or r.get("Amount") or r.get("amt") or "0"
        try:
            amount = float(amount_raw)
        except:
            # try removing commas, currency symbols
            cleaned = "".join(ch for ch in amount_raw if ch.isdigit() or ch in ".-")
            try:
                amount = float(cleaned)
            except:
                amount = 0.0
        desc = (r.get("description") or r.get("Description") or r.get("desc") or "").strip()
        # simple rules
        desc_l = desc.lower()
        if "salary" in desc_l or "payroll" in desc_l or "salary" in desc_l:
            cat = "income"
        elif "grocery" in desc_l or "supermarket" in desc_l or "groceries" in desc_l:
            cat = "groceries"
        elif "rent" in desc_l or "apartment" in desc_l:
            cat = "rent"
        elif "uber" in desc_l or "ola" in desc_l or "taxi" in desc_l:
            cat = "transport"
        else:
            cat = "other"
        t = {
            "date": date,
            "amount": amount,
            "description": desc,
            "category": cat,
            "raw": r
        }
        normalized.append(t)
    await asyncio.sleep(0)
    log.info("ingest_done", count=len(normalized))
    return normalized

async def analysis_agent(transactions: List[Dict]) -> Dict:
    """
    Compute summary metrics and a simple forecast.
    """
    total_income = sum(t["amount"] for t in transactions if t["category"] == "income")
    total_expense = sum(t["amount"] for t in transactions if t["category"] != "income")
    # naive monthly estimate using all transactions as single-month demo
    monthly_surplus = total_income - total_expense
    # category breakdown
    breakdown = {}
    for t in transactions:
        breakdown.setdefault(t["category"], 0.0)
        breakdown[t["category"]] += t["amount"]
    # forecast: keep it simple for demonstration
    forecast = {"monthly_surplus": monthly_surplus}
    await asyncio.sleep(0)
    result = {"income": total_income, "expense": total_expense, "breakdown": breakdown, "forecast": forecast}
    log.info("analysis_done", **{"income": total_income, "expense": total_expense})
    return result

async def advisor_agent(analysis: Dict, user_profile: Dict) -> Dict:
    """
    Generate advice. This is where you'd call an LLM; currently placeholder logic.
    """
    advice = []
    ms = analysis["forecast"]["monthly_surplus"]
    if ms is None:
        advice.append("No income records detected. Please ensure you uploaded salary / income transactions.")
    elif ms < 0:
        advice.append(f"You are running a monthly deficit of {ms:.2f}. Recommend reducing discretionary spending and reviewing subscriptions.")
    else:
        advice.append(f"Monthly surplus: {ms:.2f}. Aim to allocate at least 20% of surplus to emergency savings.")
    # risk profile customization
    risk = user_profile.get("risk_profile", "medium")
    if risk == "low":
        advice.append("Risk profile: Low — favor safety: savings accounts, fixed deposits, debt paydown.")
    elif risk == "high":
        advice.append("Risk profile: High — consider higher equity allocation for long-term goals.")
    else:
        advice.append("Risk profile: Medium — balanced approach advised.")
    # optionally call mock market tool to recommend a safe option
    quote = get_market_quote("govt_bond")
    advice.append(f"Example 1-yr yield proxy: {quote['price']} (mock).")
    await asyncio.sleep(0)
    log.info("advisor_done")
    return {"advice_lines": advice, "metadata": {"risk_profile": risk}}
