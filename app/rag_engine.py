# app/rag_engine.py
"""
RAG Engine for Financial Advice
Provides context-aware financial insights using vector embeddings
"""
import os
from typing import List, Dict, Optional
import json
from datetime import datetime
from collections import defaultdict
import numpy as np
from structlog import get_logger

log = get_logger()

# Simple embedding using TF-IDF-like approach (can be replaced with sentence-transformers)
class SimpleEmbedder:
    """Lightweight embedding for financial text without external dependencies"""
    
    def __init__(self):
        self.vocab = {}
        self.idf = {}
        
    def fit(self, documents: List[str]):
        """Build vocabulary and IDF scores"""
        doc_freq = defaultdict(int)
        for doc in documents:
            words = set(doc.lower().split())
            for word in words:
                doc_freq[word] += 1
                if word not in self.vocab:
                    self.vocab[word] = len(self.vocab)
        
        # Calculate IDF
        n_docs = len(documents)
        for word, freq in doc_freq.items():
            self.idf[word] = np.log(n_docs / (1 + freq))
    
    def embed(self, text: str) -> List[float]:
        """Convert text to embedding vector"""
        words = text.lower().split()
        vector = np.zeros(max(len(self.vocab), 100))
        
        for word in words:
            if word in self.vocab:
                idx = self.vocab[word]
                vector[idx] = self.idf.get(word, 1.0)
        
        # Normalize
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
        
        return vector.tolist()


class FinancialRAG:
    """RAG system for financial advice generation"""
    
    def __init__(self):
        self.embedder = SimpleEmbedder()
        self.knowledge_base = []
        self.embeddings = []
        self._initialize_knowledge()
    
    def _initialize_knowledge(self):
        """Initialize with financial wisdom and best practices"""
        self.financial_knowledge = [
            {
                "topic": "emergency_fund",
                "content": "Maintain 3-6 months of expenses in emergency fund. This provides financial security during unexpected events.",
                "category": "savings"
            },
            {
                "topic": "50_30_20_rule",
                "content": "Budget using 50-30-20 rule: 50% needs, 30% wants, 20% savings and debt repayment.",
                "category": "budgeting"
            },
            {
                "topic": "high_interest_debt",
                "content": "Prioritize paying off high-interest debt (>10% APR) before investing. Debt reduction is guaranteed return.",
                "category": "debt"
            },
            {
                "topic": "diversification",
                "content": "Diversify investments across asset classes: stocks, bonds, real estate. Don't put all eggs in one basket.",
                "category": "investment"
            },
            {
                "topic": "retirement_savings",
                "content": "Start retirement savings early. Compound interest works best over long periods. Aim for 15% of income.",
                "category": "retirement"
            },
            {
                "topic": "expense_tracking",
                "content": "Track all expenses monthly. Small recurring costs add up significantly over time.",
                "category": "budgeting"
            },
            {
                "topic": "investment_horizon",
                "content": "Match investment risk to time horizon: short-term goals need safer assets, long-term can handle volatility.",
                "category": "investment"
            },
            {
                "topic": "lifestyle_inflation",
                "content": "Avoid lifestyle inflation. When income increases, increase savings proportionally before increasing spending.",
                "category": "savings"
            },
            {
                "topic": "tax_optimization",
                "content": "Utilize tax-advantaged accounts. Maximize contributions to retirement accounts and health savings accounts.",
                "category": "tax"
            },
            {
                "topic": "subscription_audit",
                "content": "Audit subscriptions quarterly. Cancel unused services. Average person wastes 20-30% on forgotten subscriptions.",
                "category": "expense_reduction"
            }
        ]
        
        # Build embeddings
        documents = [k["content"] for k in self.financial_knowledge]
        self.embedder.fit(documents)
        
        for knowledge in self.financial_knowledge:
            embedding = self.embedder.embed(knowledge["content"])
            self.knowledge_base.append(knowledge)
            self.embeddings.append(embedding)
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        v1 = np.array(vec1)
        v2 = np.array(vec2)
        return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-10)
    
    def retrieve_relevant_knowledge(self, query: str, top_k: int = 3) -> List[Dict]:
        """Retrieve most relevant financial knowledge for query"""
        query_embedding = self.embedder.embed(query)
        
        similarities = []
        for idx, emb in enumerate(self.embeddings):
            sim = self._cosine_similarity(query_embedding, emb)
            similarities.append((sim, idx))
        
        # Sort by similarity
        similarities.sort(reverse=True)
        
        results = []
        for sim, idx in similarities[:top_k]:
            results.append({
                **self.knowledge_base[idx],
                "relevance_score": float(sim)
            })
        
        return results
    
    def analyze_spending_patterns(self, transactions: List[Dict]) -> Dict:
        """Deep analysis of spending patterns"""
        # Group by category
        category_spending = defaultdict(float)
        category_count = defaultdict(int)
        monthly_data = defaultdict(lambda: defaultdict(float))
        
        for tx in transactions:
            cat = tx.get("category", "other")
            amount = tx.get("amount", 0)
            
            # Only process non-income transactions as expenses
            if cat != "income":
                # Convert negative amounts to positive for expense tracking
                expense_amount = abs(amount)
                category_spending[cat] += expense_amount
                category_count[cat] += 1
                
                # Extract month
                date_str = tx.get("date", "")
                try:
                    month = date_str[:7] if len(date_str) >= 7 else "unknown"
                    monthly_data[month][cat] += expense_amount
                except:
                    pass
        
        total_spending = sum(category_spending.values())
        
        # Calculate percentages
        category_percentages = {
            cat: (amount / total_spending * 100) if total_spending > 0 else 0
            for cat, amount in category_spending.items()
        }
        
        # Identify top spending categories
        top_categories = sorted(
            category_spending.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        return {
            "total_spending": total_spending,
            "category_breakdown": dict(category_spending),
            "category_percentages": category_percentages,
            "category_transaction_count": dict(category_count),
            "top_spending_categories": top_categories,
            "monthly_trends": dict(monthly_data)
        }
    
    def calculate_financial_health_score(self, analysis: Dict, transactions: List[Dict]) -> Dict:
        """Calculate financial health score (0-100)"""
        score = 50  # Base score
        factors = []
        
        income = analysis.get("income", 0)
        expense = analysis.get("expense", 0)  # Already positive from analysis_agent
        # Surplus = income - expense (both are positive values)
        surplus = income - expense
        
        # Factor 1: Savings rate
        if income > 0:
            savings_rate = (surplus / income) * 100
            if savings_rate >= 20:
                score += 20
                factors.append(f"Excellent savings rate: {savings_rate:.1f}%")
            elif savings_rate >= 10:
                score += 10
                factors.append(f"Good savings rate: {savings_rate:.1f}%")
            elif savings_rate > 0:
                score += 5
                factors.append(f"Positive savings: {savings_rate:.1f}%")
            else:
                score -= 20
                factors.append(f"Negative savings: {savings_rate:.1f}%")
        
        # Factor 2: Spending diversity (not too concentrated)
        breakdown = analysis.get("breakdown", {})
        if breakdown:
            # Remove income from breakdown for expense analysis
            expense_breakdown = {k: v for k, v in breakdown.items() if k != "income"}
            if expense_breakdown:
                total_expenses = sum(expense_breakdown.values())
                if total_expenses > 0:
                    max_category_pct = max(expense_breakdown.values()) / total_expenses * 100
                    if max_category_pct < 40:
                        score += 10
                        factors.append("Well-diversified spending")
                    elif max_category_pct > 60:
                        score -= 10
                        factors.append("Spending too concentrated in one category")
        
        # Factor 3: Transaction regularity
        if len(transactions) >= 5:
            score += 10
            factors.append("Good transaction tracking")
        
        # Factor 4: Income presence
        has_income = any(t.get("category") == "income" for t in transactions)
        if has_income:
            score += 10
            factors.append("Regular income detected")
        else:
            score -= 15
            factors.append("No income transactions found")
        
        # Clamp score
        score = max(0, min(100, score))
        
        # Rating
        if score >= 80:
            rating = "Excellent"
        elif score >= 60:
            rating = "Good"
        elif score >= 40:
            rating = "Fair"
        else:
            rating = "Needs Improvement"
        
        return {
            "score": score,
            "rating": rating,
            "factors": factors
        }
    
    def generate_personalized_advice(
        self,
        transactions: List[Dict],
        analysis: Dict,
        user_profile: Dict
    ) -> Dict:
        """Generate RAG-enhanced personalized financial advice"""
        
        # Analyze spending patterns
        spending_analysis = self.analyze_spending_patterns(transactions)
        
        # Calculate health score
        health_score = self.calculate_financial_health_score(analysis, transactions)
        
        # Build context query
        income = analysis.get("income", 0)
        expense = analysis.get("expense", 0)  # Already positive from analysis_agent
        # Surplus = income - expense (both positive values)
        surplus = income - expense
        
        context_query = f"monthly income {income} expense {expense} surplus {surplus} "
        context_query += " ".join(spending_analysis["category_breakdown"].keys())
        
        # Retrieve relevant knowledge
        relevant_knowledge = self.retrieve_relevant_knowledge(context_query, top_k=4)
        
        # Generate advice sections
        advice_sections = {
            "summary": self._generate_summary(income, expense, surplus, health_score),
            "spending_insights": self._generate_spending_insights(spending_analysis),
            "savings_recommendations": self._generate_savings_advice(surplus, income, relevant_knowledge),
            "investment_suggestions": self._generate_investment_advice(surplus, user_profile, relevant_knowledge),
            "action_items": self._generate_action_items(spending_analysis, surplus, income),
            "financial_health": health_score,
            "relevant_tips": [k["content"] for k in relevant_knowledge]
        }
        
        return advice_sections
    
    def _generate_summary(self, income: float, expense: float, surplus: float, health_score: Dict) -> str:
        """Generate executive summary"""
        if income == 0:
            return "⚠️ No income detected. Please ensure income transactions are uploaded for complete analysis."
        
        savings_rate = (surplus / income * 100) if income > 0 else 0
        
        summary = f"💰 Financial Health: {health_score['rating']} ({health_score['score']}/100)\n\n"
        summary += f"Monthly Income: ₹{income:,.2f}\n"
        summary += f"Monthly Expenses: ₹{expense:,.2f}\n"
        summary += f"Net Surplus: ₹{surplus:,.2f} ({savings_rate:.1f}% savings rate)\n\n"
        
        if surplus > 0:
            summary += f"✅ You're saving {savings_rate:.1f}% of your income. "
            if savings_rate >= 20:
                summary += "Excellent work!"
            elif savings_rate >= 10:
                summary += "Good progress, aim for 20%."
            else:
                summary += "Try to increase to 20%."
        else:
            summary += f"⚠️ You're spending more than you earn. Immediate action needed."
        
        return summary
    
    def _generate_spending_insights(self, spending_analysis: Dict) -> List[str]:
        """Generate insights about spending patterns"""
        insights = []
        
        top_categories = spending_analysis["top_spending_categories"]
        percentages = spending_analysis["category_percentages"]
        
        if top_categories:
            top_cat, top_amount = top_categories[0]
            top_pct = percentages.get(top_cat, 0)
            insights.append(f"🔍 Your highest expense is {top_cat}: ₹{top_amount:,.2f} ({top_pct:.1f}% of total)")
        
        # Check for concerning patterns
        if percentages.get("other", 0) > 30:
            insights.append("⚠️ Over 30% spending is uncategorized. Better categorization helps identify savings opportunities.")
        
        if "rent" in percentages and percentages["rent"] > 40:
            insights.append("🏠 Housing costs exceed 40% of expenses. Consider if this is sustainable long-term.")
        
        # Positive patterns
        if percentages.get("groceries", 0) < 15:
            insights.append("✅ Grocery spending is well-controlled.")
        
        return insights
    
    def _generate_savings_advice(self, surplus: float, income: float, knowledge: List[Dict]) -> List[str]:
        """Generate savings recommendations"""
        advice = []
        
        if surplus <= 0:
            advice.append("🚨 Priority: Create a positive cash flow by reducing expenses or increasing income.")
            advice.append("📊 Track every expense for 30 days to identify reduction opportunities.")
        else:
            emergency_fund_target = income * 3  # 3 months
            advice.append(f"🎯 Emergency Fund Goal: ₹{emergency_fund_target:,.2f} (3 months of income)")
            advice.append(f"💡 With current surplus, you can build this in {emergency_fund_target/surplus:.1f} months")
        
        # Add relevant knowledge
        for k in knowledge:
            if k["category"] in ["savings", "budgeting"]:
                advice.append(f"💡 {k['content']}")
        
        return advice
    
    def _generate_investment_advice(self, surplus: float, profile: Dict, knowledge: List[Dict]) -> List[str]:
        """Generate investment recommendations"""
        advice = []
        risk_profile = profile.get("risk_profile", "medium")
        
        if surplus <= 0:
            advice.append("⏸️ Focus on positive cash flow before investing.")
            return advice
        
        # Investment allocation based on surplus
        if surplus < 5000:
            advice.append(f"💰 Current surplus: ₹{surplus:,.2f}/month")
            advice.append("🏦 Start with: High-yield savings account or liquid funds")
            advice.append("📈 Target: Build ₹50,000 emergency fund first")
        elif surplus < 15000:
            advice.append(f"💰 Current surplus: ₹{surplus:,.2f}/month")
            advice.append("📊 Suggested allocation:")
            advice.append("  • 50% Emergency fund (liquid)")
            advice.append("  • 30% Debt mutual funds")
            advice.append("  • 20% Equity mutual funds (SIP)")
        else:
            advice.append(f"💰 Strong surplus: ₹{surplus:,.2f}/month")
            advice.append("📊 Diversified allocation:")
            
            if risk_profile == "low":
                advice.append("  • 60% Fixed deposits / Debt funds")
                advice.append("  • 30% Balanced funds")
                advice.append("  • 10% Equity funds")
            elif risk_profile == "high":
                advice.append("  • 60% Equity mutual funds")
                advice.append("  • 20% Mid/Small cap funds")
                advice.append("  • 20% Debt funds")
            else:  # medium
                advice.append("  • 50% Equity mutual funds")
                advice.append("  • 30% Debt funds")
                advice.append("  • 20% Gold/International funds")
        
        # Add relevant knowledge
        for k in knowledge:
            if k["category"] == "investment":
                advice.append(f"💡 {k['content']}")
        
        return advice
    
    def _generate_action_items(self, spending_analysis: Dict, surplus: float, income: float) -> List[str]:
        """Generate specific action items"""
        actions = []
        
        # Immediate actions
        if surplus <= 0:
            actions.append("🎯 Week 1: List all subscriptions and cancel unused ones")
            actions.append("🎯 Week 2: Identify top 3 expense categories to reduce by 10%")
            actions.append("🎯 Week 3: Set up expense tracking system")
        else:
            actions.append("🎯 This week: Set up automatic transfer of 20% income to savings")
            actions.append("🎯 This month: Open high-yield savings account if not already done")
            actions.append("🎯 Next month: Start SIP in index fund with ₹" + f"{min(surplus * 0.3, 5000):,.0f}")
        
        # Category-specific actions
        percentages = spending_analysis["category_percentages"]
        
        if percentages.get("transport", 0) > 10:
            actions.append("🚗 Review: Can you optimize transport costs with monthly passes or carpooling?")
        
        if "subscription" in spending_analysis["category_breakdown"]:
            actions.append("📱 Audit: Review all subscriptions - cancel unused services")
        
        return actions


# Global RAG instance
_rag_instance = None

def get_rag_engine() -> FinancialRAG:
    """Get or create RAG engine singleton"""
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = FinancialRAG()
        log.info("rag_engine_initialized")
    return _rag_instance
