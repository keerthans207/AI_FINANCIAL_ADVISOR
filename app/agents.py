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
        except ValueError:
            # try removing commas, currency symbols
            cleaned = "".join(ch for ch in str(amount_raw) if ch.isdigit() or ch in ".-")
            try:
                amount = float(cleaned) if cleaned and cleaned not in ['.', '-', '-.'] else 0.0
            except ValueError:
                amount = 0.0
        desc = (r.get("description") or r.get("Description") or r.get("desc") or "").strip()
        # simple rules - fixed duplicate "salary" check
        desc_l = desc.lower()
        if "salary" in desc_l or "payroll" in desc_l or "wage" in desc_l:
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
    # Expenses are negative, so we take absolute value for clarity
    total_expense = abs(sum(t["amount"] for t in transactions if t["category"] != "income"))
    # Calculate surplus: income minus absolute expense value
    monthly_surplus = total_income - total_expense
    # category breakdown
    breakdown = {}
    for t in transactions:
        cat = t["category"]
        amount = t["amount"]
        # Store expenses as positive values in breakdown for clarity
        if cat != "income":
            amount = abs(amount)
        breakdown.setdefault(cat, 0.0)
        breakdown[cat] += amount
    # forecast: keep it simple for demonstration
    forecast = {"monthly_surplus": monthly_surplus}
    await asyncio.sleep(0)
    result = {"income": total_income, "expense": total_expense, "breakdown": breakdown, "forecast": forecast}
    log.info("analysis_done", income=total_income, expense=total_expense, surplus=monthly_surplus)
    return result

async def advisor_agent(analysis: Dict, user_profile: Dict, transactions: List[Dict] = None) -> Dict:
    """
    Generate advice using LLM RAG system for context-aware recommendations.
    Falls back to rule-based if LLM unavailable.
    """
    from .llm_rag_engine import (
        add_documents, 
        retrieve, 
        generate_financial_advice,
        get_system_status
    )
    
    try:
        # Check if RAG system is available
        status = get_system_status()
        
        if not status['initialized']:
            log.warning("rag_not_initialized", fallback="simple_advice")
            return _generate_simple_advice(analysis, user_profile)
        
        if transactions:
            # Build structured financial summary for RAG
            financial_summary = _build_financial_summary(analysis, transactions, user_profile)
            
            # Add to vector store
            add_documents(
                texts=[financial_summary],
                metadata=[{"type": "financial_analysis", "user_profile": user_profile}]
            )
            
            # Retrieve relevant context
            query = f"financial advice for income {analysis.get('income')} expense {analysis.get('expense')} risk {user_profile.get('risk_profile', 'medium')}"
            retrieved_docs = retrieve(query, k=2)
            
            # Build context from retrieved documents
            context = "\n".join([doc['text'] for doc in retrieved_docs])
            
            # Generate advice using LLM
            advice = generate_financial_advice(
                context=context,
                financial_data=analysis,
                risk_profile=user_profile.get('risk_profile', 'medium')
            )
            
            await asyncio.sleep(0)
            log.info("advisor_done_with_llm_rag", 
                     has_summary=bool(advice.get('summary')),
                     action_steps=len(advice.get('action_steps', [])))
            
            return advice
        else:
            # Fallback to simple advice
            return _generate_simple_advice(analysis, user_profile)
            
    except Exception as e:
        log.error("advisor_agent_error", error=str(e))
        return _generate_simple_advice(analysis, user_profile)


def _build_financial_summary(analysis: Dict, transactions: List[Dict], user_profile: Dict) -> str:
    """Build structured financial summary for vector store"""
    
    income = analysis.get('income', 0)
    expense = analysis.get('expense', 0)
    surplus = income - expense
    savings_rate = (surplus / income * 100) if income > 0 else 0
    breakdown = analysis.get('breakdown', {})
    
    summary = f"""Financial Analysis Summary:
Monthly Income: ₹{income:,.0f}
Monthly Expenses: ₹{expense:,.0f}
Net Surplus: ₹{surplus:,.0f}
Savings Rate: {savings_rate:.1f}%
Risk Profile: {user_profile.get('risk_profile', 'medium')}

Expense Breakdown:
"""
    
    for category, amount in breakdown.items():
        if category != 'income':
            percentage = (amount / expense * 100) if expense > 0 else 0
            summary += f"- {category.title()}: ₹{amount:,.0f} ({percentage:.1f}%)\n"
    
    # Add transaction insights
    summary += f"\nTotal Transactions: {len(transactions)}\n"
    
    # Identify top spending categories
    expense_cats = {k: v for k, v in breakdown.items() if k != 'income'}
    if expense_cats:
        top_cat = max(expense_cats.items(), key=lambda x: x[1])
        summary += f"Highest Expense Category: {top_cat[0].title()} (₹{top_cat[1]:,.0f})\n"
    
    return summary


def _generate_simple_advice(analysis: Dict, user_profile: Dict) -> Dict:
    """Generate simple rule-based advice (fallback)"""
    
    income = analysis.get('income', 0)
    expense = analysis.get('expense', 0)
    surplus = income - expense
    savings_rate = (surplus / income * 100) if income > 0 else 0
    risk = user_profile.get('risk_profile', 'medium')
    
    advice = {
        "summary": f"Monthly surplus: ₹{surplus:,.0f}. Savings rate: {savings_rate:.1f}%.",
        
        "risk_assessment": "Spending exceeds income - immediate action needed." if surplus < 0 else "Financial position is stable.",
        
        "budget_recommendation": f"Apply 50-30-20 rule: ₹{income*0.5:,.0f} needs, ₹{income*0.3:,.0f} wants, ₹{income*0.2:,.0f} savings.",
        
        "investment_suggestion": _get_simple_investment_advice(surplus, risk),
        
        "emergency_fund_strategy": f"Target: ₹{expense*6:,.0f} (6 months). Timeline: {(expense*6/surplus):.1f} months." if surplus > 0 else "Focus on positive cash flow first.",
        
        "action_steps": [
            "Track all expenses for 30 days",
            "Set up automatic savings transfer",
            "Review and optimize subscriptions",
            "Build emergency fund",
            "Consider tax-saving investments"
        ]
    }
    
    return advice


def _get_simple_investment_advice(surplus: float, risk_profile: str) -> str:
    """Simple investment allocation advice"""
    
    if surplus <= 0:
        return "Focus on expense reduction before investing."
    
    if risk_profile == "low":
        return "Conservative: 60% debt funds, 30% balanced funds, 10% equity"
    elif risk_profile == "high":
        return "Aggressive: 60% equity, 20% mid-cap, 20% debt"
    else:
        return "Moderate: 50% equity, 30% debt, 20% gold/international"
