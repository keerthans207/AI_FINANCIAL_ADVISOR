"""
Production-Ready Local RAG System for Financial Advisory
Optimized for 4GB RAM, CPU-only, no GPU
Uses Phi-2 (2.7B) GGUF Q4_K_M + FAISS + sentence-transformers
"""

import os
import json
import gc
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import numpy as np
from structlog import get_logger

log = get_logger()

# Global instances (loaded once at startup)
_embedding_model = None
_llm_model = None
_faiss_index = None
_document_store = []
_initialized = False

# Model paths
MODELS_DIR = Path("models")
PHI2_MODEL_PATH = MODELS_DIR / "phi-2.Q4_K_M.gguf"

# System constraints for 4GB RAM
LLM_CONFIG = {
    "n_ctx": 1024,          # Context window
    "n_threads": 2,         # CPU threads
    "n_gpu_layers": 0,      # CPU only
    "n_batch": 128,         # Batch size
    "max_tokens": 300,      # Max generation tokens
    "temperature": 0.7,
    "top_p": 0.9,
    "repeat_penalty": 1.1,
}

# Fallback config for memory pressure
FALLBACK_CONFIG = {
    "n_ctx": 512,
    "max_tokens": 150,
}


def initialize_rag_system():
    """
    Initialize RAG system components globally.
    Called once at FastAPI startup.
    """
    global _embedding_model, _llm_model, _faiss_index, _initialized
    
    if _initialized:
        log.info("rag_already_initialized")
        return
    
    try:
        log.info("initializing_rag_system", ram_limit="4GB", mode="CPU-only")
        
        # 1. Initialize embedding model
        _embedding_model = _load_embedding_model()
        
        # 2. Initialize FAISS index
        _faiss_index = _initialize_faiss_index()
        
        # 3. Initialize LLM (Phi-2)
        _llm_model = _load_llm_model()
        
        _initialized = True
        log.info("rag_system_initialized", 
                 embedding_dim=384, 
                 llm="phi-2-q4",
                 vector_store="faiss-cpu")
        
    except Exception as e:
        log.error("rag_initialization_failed", error=str(e))
        raise


def _load_embedding_model():
    """Load sentence-transformers embedding model"""
    try:
        from sentence_transformers import SentenceTransformer
        
        log.info("loading_embedding_model", model="all-MiniLM-L6-v2")
        model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        
        # Test embedding
        test_emb = model.encode("test", show_progress_bar=False)
        log.info("embedding_model_loaded", dimension=len(test_emb))
        
        return model
        
    except Exception as e:
        log.error("embedding_model_load_failed", error=str(e))
        raise


def _initialize_faiss_index():
    """Initialize FAISS CPU index"""
    try:
        import faiss
        
        log.info("initializing_faiss_index", dimension=384, type="IndexFlatL2")
        
        # Create CPU-only L2 index
        index = faiss.IndexFlatL2(384)  # all-MiniLM-L6-v2 dimension
        
        log.info("faiss_index_initialized")
        return index
        
    except Exception as e:
        log.error("faiss_initialization_failed", error=str(e))
        raise


def _load_llm_model():
    """Load Phi-2 GGUF model with llama-cpp-python"""
    try:
        from llama_cpp import Llama
        
        # Check if model exists
        if not PHI2_MODEL_PATH.exists():
            log.warning("phi2_model_not_found", 
                       path=str(PHI2_MODEL_PATH),
                       message="Download from: https://huggingface.co/TheBloke/phi-2-GGUF")
            return None
        
        log.info("loading_phi2_model", 
                 path=str(PHI2_MODEL_PATH),
                 config=LLM_CONFIG)
        
        model = Llama(
            model_path=str(PHI2_MODEL_PATH),
            n_ctx=LLM_CONFIG["n_ctx"],
            n_threads=LLM_CONFIG["n_threads"],
            n_gpu_layers=LLM_CONFIG["n_gpu_layers"],
            n_batch=LLM_CONFIG["n_batch"],
            verbose=False,
        )
        
        log.info("phi2_model_loaded", ram_usage="~800MB")
        return model
        
    except Exception as e:
        log.error("llm_load_failed", error=str(e))
        return None


def add_documents(texts: List[str], metadata: Optional[List[Dict]] = None):
    """
    Add documents to FAISS vector store.
    
    Args:
        texts: List of text documents to embed and store
        metadata: Optional metadata for each document
    """
    global _document_store
    
    if not _initialized:
        raise RuntimeError("RAG system not initialized. Call initialize_rag_system() first.")
    
    try:
        log.info("adding_documents", count=len(texts))
        
        # Generate embeddings
        embeddings = _embedding_model.encode(
            texts, 
            show_progress_bar=False,
            convert_to_numpy=True
        )
        
        # Add to FAISS index
        _faiss_index.add(embeddings.astype('float32'))
        
        # Store documents with metadata
        for i, text in enumerate(texts):
            doc_meta = metadata[i] if metadata and i < len(metadata) else {}
            _document_store.append({
                "text": text,
                "metadata": doc_meta,
                "index": len(_document_store)
            })
        
        log.info("documents_added", 
                 total_docs=len(_document_store),
                 index_size=_faiss_index.ntotal)
        
    except Exception as e:
        log.error("add_documents_failed", error=str(e))
        raise


def retrieve(query: str, k: int = 2) -> List[Dict]:
    """
    Retrieve top-k most relevant documents for query.
    
    Args:
        query: Search query
        k: Number of documents to retrieve
        
    Returns:
        List of retrieved documents with scores
    """
    if not _initialized:
        raise RuntimeError("RAG system not initialized.")
    
    if _faiss_index.ntotal == 0:
        log.warning("retrieve_empty_index")
        return []
    
    try:
        # Embed query
        query_embedding = _embedding_model.encode(
            [query],
            show_progress_bar=False,
            convert_to_numpy=True
        )
        
        # Search FAISS
        k = min(k, _faiss_index.ntotal)  # Don't exceed available docs
        distances, indices = _faiss_index.search(
            query_embedding.astype('float32'), 
            k
        )
        
        # Retrieve documents
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(_document_store):
                doc = _document_store[idx].copy()
                doc['score'] = float(distances[0][i])
                results.append(doc)
        
        log.info("documents_retrieved", query_len=len(query), results=len(results))
        return results
        
    except Exception as e:
        log.error("retrieve_failed", error=str(e))
        return []


def generate_financial_advice(
    context: str,
    financial_data: Dict,
    risk_profile: str = "medium"
) -> Dict:
    """
    Generate financial advice using Phi-2 LLM with retrieved context.
    
    Args:
        context: Retrieved context from vector store
        financial_data: Structured financial analysis
        risk_profile: User's risk profile (low/medium/high)
        
    Returns:
        Structured financial advice as JSON
    """
    if not _initialized:
        raise RuntimeError("RAG system not initialized.")
    
    if _llm_model is None:
        log.warning("llm_not_available", fallback="rule_based_advice")
        return _generate_fallback_advice(financial_data, risk_profile)
    
    try:
        # Build structured prompt
        prompt = _build_financial_prompt(context, financial_data, risk_profile)
        
        log.info("generating_advice", 
                 prompt_len=len(prompt),
                 max_tokens=LLM_CONFIG["max_tokens"])
        
        # Generate with Phi-2
        response = _llm_model(
            prompt,
            max_tokens=LLM_CONFIG["max_tokens"],
            temperature=LLM_CONFIG["temperature"],
            top_p=LLM_CONFIG["top_p"],
            repeat_penalty=LLM_CONFIG["repeat_penalty"],
            stop=["</s>", "USER:", "ASSISTANT:"],
        )
        
        # Extract generated text
        generated_text = response['choices'][0]['text'].strip()
        
        log.info("advice_generated", length=len(generated_text))
        
        # Parse into structured format
        advice = _parse_llm_response(generated_text, financial_data)
        
        # Force garbage collection
        gc.collect()
        
        return advice
        
    except Exception as e:
        log.error("advice_generation_failed", error=str(e))
        return _generate_fallback_advice(financial_data, risk_profile)


def _build_financial_prompt(
    context: str,
    financial_data: Dict,
    risk_profile: str
) -> str:
    """Build SEBI-compliant financial advisor prompt"""
    
    income = financial_data.get('income', 0)
    expense = financial_data.get('expense', 0)
    surplus = income - expense
    savings_rate = (surplus / income * 100) if income > 0 else 0
    breakdown = financial_data.get('breakdown', {})
    
    # Build structured data section
    data_section = f"""
FINANCIAL PROFILE:
- Monthly Income: ₹{income:,.0f}
- Monthly Expenses: ₹{expense:,.0f}
- Net Surplus: ₹{surplus:,.0f}
- Savings Rate: {savings_rate:.1f}%
- Risk Profile: {risk_profile.upper()}

EXPENSE BREAKDOWN:
"""
    
    for category, amount in breakdown.items():
        if category != 'income':
            percentage = (amount / expense * 100) if expense > 0 else 0
            data_section += f"- {category.title()}: ₹{amount:,.0f} ({percentage:.1f}%)\n"
    
    if context:
        data_section += f"\nRELEVANT CONTEXT:\n{context}\n"
    
    # Master prompt template
    prompt = f"""You are a SEBI-compliant certified financial planner for Indian middle-class clients.
Analyze the following structured financial data carefully.

{data_section}

Your responsibilities:
1. Interpret monthly income and expenses
2. Identify overspending categories
3. Calculate and evaluate savings rate
4. Assess financial health
5. Suggest optimized budget allocation using 50-30-20 rule
6. Recommend emergency fund target (in months of expenses)
7. Suggest investment allocation based on risk profile:
   - Conservative (low risk): 60% debt, 30% balanced, 10% equity
   - Moderate (medium risk): 50% equity, 30% debt, 20% gold/international
   - Aggressive (high risk): 60% equity, 20% mid-cap, 20% debt
8. Provide clear actionable next steps

Rules:
- Use numbers explicitly from the data above
- Be precise and realistic
- Avoid generic textbook advice
- Keep response under 300 words
- Maintain professional tone
- Focus on Indian financial context (PPF, EPF, NPS, mutual funds, etc.)

Generate advice in this format:
SUMMARY: [2-3 sentences on overall financial health]
RISK ASSESSMENT: [Identify key risks and concerns]
BUDGET RECOMMENDATION: [Specific allocation suggestions]
INVESTMENT SUGGESTION: [Risk-appropriate investment strategy]
EMERGENCY FUND: [Target amount and timeline]
ACTION STEPS: [3-5 specific next steps]

Begin your analysis:"""
    
    return prompt


def _parse_llm_response(generated_text: str, financial_data: Dict) -> Dict:
    """Parse LLM response into structured JSON format"""
    
    try:
        # Extract sections using keywords
        sections = {
            "summary": "",
            "risk_assessment": "",
            "budget_recommendation": "",
            "investment_suggestion": "",
            "emergency_fund_strategy": "",
            "action_steps": []
        }
        
        lines = generated_text.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect section headers
            line_upper = line.upper()
            if 'SUMMARY' in line_upper:
                current_section = 'summary'
                continue
            elif 'RISK' in line_upper:
                current_section = 'risk_assessment'
                continue
            elif 'BUDGET' in line_upper:
                current_section = 'budget_recommendation'
                continue
            elif 'INVESTMENT' in line_upper:
                current_section = 'investment_suggestion'
                continue
            elif 'EMERGENCY' in line_upper or 'FUND' in line_upper:
                current_section = 'emergency_fund_strategy'
                continue
            elif 'ACTION' in line_upper or 'STEPS' in line_upper:
                current_section = 'action_steps'
                continue
            
            # Add content to current section
            if current_section:
                if current_section == 'action_steps':
                    # Extract action items
                    if line.startswith(('-', '•', '*', '1', '2', '3', '4', '5')):
                        clean_line = line.lstrip('-•*123456789. ')
                        if clean_line:
                            sections['action_steps'].append(clean_line)
                else:
                    sections[current_section] += line + " "
        
        # Clean up sections
        for key in sections:
            if isinstance(sections[key], str):
                sections[key] = sections[key].strip()
        
        # Ensure we have action steps
        if not sections['action_steps']:
            sections['action_steps'] = _generate_default_actions(financial_data)
        
        return sections
        
    except Exception as e:
        log.error("parse_llm_response_failed", error=str(e))
        return _generate_fallback_advice(financial_data, "medium")


def _generate_fallback_advice(financial_data: Dict, risk_profile: str) -> Dict:
    """Generate rule-based advice when LLM is unavailable"""
    
    income = financial_data.get('income', 0)
    expense = financial_data.get('expense', 0)
    surplus = income - expense
    savings_rate = (surplus / income * 100) if income > 0 else 0
    
    # Determine financial health
    if savings_rate >= 20:
        health = "excellent"
    elif savings_rate >= 10:
        health = "good"
    elif savings_rate > 0:
        health = "fair"
    else:
        health = "critical"
    
    advice = {
        "summary": f"Your current savings rate is {savings_rate:.1f}%. Financial health: {health}. Monthly surplus: ₹{surplus:,.0f}.",
        
        "risk_assessment": "Overspending detected in discretionary categories. " if surplus < income * 0.1 else "Spending is under control. ",
        
        "budget_recommendation": f"Apply 50-30-20 rule: ₹{income*0.5:,.0f} for needs, ₹{income*0.3:,.0f} for wants, ₹{income*0.2:,.0f} for savings.",
        
        "investment_suggestion": _get_investment_allocation(surplus, risk_profile),
        
        "emergency_fund_strategy": f"Target emergency fund: ₹{expense*6:,.0f} (6 months expenses). At current surplus, achievable in {(expense*6/surplus):.1f} months." if surplus > 0 else "Focus on creating positive cash flow first.",
        
        "action_steps": _generate_default_actions(financial_data)
    }
    
    return advice


def _get_investment_allocation(surplus: float, risk_profile: str) -> str:
    """Get investment allocation based on risk profile"""
    
    if surplus <= 0:
        return "Focus on expense reduction before investing."
    
    allocations = {
        "low": "Conservative: 60% debt funds/FD, 30% balanced funds, 10% equity index funds",
        "medium": "Moderate: 50% equity mutual funds, 30% debt funds, 20% gold/international funds",
        "high": "Aggressive: 60% equity mutual funds, 20% mid/small cap funds, 20% debt funds"
    }
    
    allocation = allocations.get(risk_profile, allocations["medium"])
    
    if surplus < 5000:
        return f"{allocation}. Start with ₹{surplus*0.5:,.0f}/month SIP in index funds."
    elif surplus < 15000:
        return f"{allocation}. Suggested SIP: ₹{surplus*0.6:,.0f}/month across diversified funds."
    else:
        return f"{allocation}. Suggested SIP: ₹{surplus*0.7:,.0f}/month with professional advisory."


def _generate_default_actions(financial_data: Dict) -> List[str]:
    """Generate default action steps"""
    
    surplus = financial_data.get('income', 0) - financial_data.get('expense', 0)
    
    actions = []
    
    if surplus <= 0:
        actions.extend([
            "Audit all subscriptions and cancel unused services",
            "Identify top 3 expense categories to reduce by 10%",
            "Set up expense tracking system",
            "Review and negotiate recurring bills"
        ])
    else:
        actions.extend([
            f"Set up automatic transfer of ₹{surplus*0.2:,.0f} to savings account",
            "Open high-yield savings account or liquid fund",
            f"Start SIP with ₹{min(surplus*0.3, 5000):,.0f} in index fund",
            "Build emergency fund to 3 months expenses",
            "Review and optimize insurance coverage"
        ])
    
    return actions[:5]  # Return top 5 actions


def get_system_status() -> Dict:
    """Get RAG system status for monitoring"""
    return {
        "initialized": _initialized,
        "embedding_model_loaded": _embedding_model is not None,
        "llm_model_loaded": _llm_model is not None,
        "faiss_index_size": _faiss_index.ntotal if _faiss_index else 0,
        "documents_stored": len(_document_store),
        "config": LLM_CONFIG
    }


def clear_vector_store():
    """Clear vector store (useful for testing)"""
    global _document_store, _faiss_index
    
    if _faiss_index:
        _faiss_index.reset()
    _document_store = []
    
    log.info("vector_store_cleared")
