#!/usr/bin/env python3
"""
Quick test script for RAG Financial Advisor System
Run this after starting the server to see the RAG system in action
"""

import requests
import json
import time

BASE_URL = "http://localhost:8010"

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")

def test_upload_csv():
    """Test uploading transactions and getting RAG advice"""
    print_section("1. UPLOADING ENHANCED TRANSACTIONS")
    
    # Upload the enhanced sample data
    with open("Sample data/enhanced_transactions.csv", "rb") as f:
        files = {"file": f}
        response = requests.post(f"{BASE_URL}/upload_csv?user_id=1", files=files)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Successfully uploaded {data['transactions_ingested']} transactions")
        print(f"📊 User ID: {data['user_id']}")
        
        # Display RAG advice if available
        if "advice" in data:
            advice = data["advice"]
            
            if "summary" in advice:
                print("\n" + "─"*60)
                print("FINANCIAL SUMMARY")
                print("─"*60)
                print(advice["summary"])
            
            if "spending_insights" in advice:
                print("\n" + "─"*60)
                print("SPENDING INSIGHTS")
                print("─"*60)
                for insight in advice["spending_insights"]:
                    print(f"  {insight}")
            
            if "financial_health" in advice:
                health = advice["financial_health"]
                print("\n" + "─"*60)
                print("FINANCIAL HEALTH SCORE")
                print("─"*60)
                print(f"  Score: {health['score']}/100 - {health['rating']}")
                print(f"\n  Factors:")
                for factor in health["factors"]:
                    print(f"    • {factor}")
        
        return data["user_id"]
    else:
        print(f"❌ Upload failed: {response.status_code}")
        print(response.text)
        return None

def test_get_insights(user_id, risk_profile="medium"):
    """Test getting detailed RAG insights"""
    print_section(f"2. GETTING DETAILED INSIGHTS (Risk: {risk_profile.upper()})")
    
    response = requests.get(f"{BASE_URL}/insights/{user_id}?risk_profile={risk_profile}")
    
    if response.status_code == 200:
        data = response.json()
        insights = data["insights"]
        
        print(f"📈 Analyzed {data['transaction_count']} transactions\n")
        
        # Summary
        if "summary" in insights:
            print("─"*60)
            print("EXECUTIVE SUMMARY")
            print("─"*60)
            print(insights["summary"])
        
        # Spending Insights
        if "spending_insights" in insights:
            print("\n" + "─"*60)
            print("SPENDING INSIGHTS")
            print("─"*60)
            for insight in insights["spending_insights"]:
                print(f"  {insight}")
        
        # Savings Recommendations
        if "savings_recommendations" in insights:
            print("\n" + "─"*60)
            print("SAVINGS RECOMMENDATIONS")
            print("─"*60)
            for rec in insights["savings_recommendations"][:5]:  # Show first 5
                print(f"  {rec}")
        
        # Investment Suggestions
        if "investment_suggestions" in insights:
            print("\n" + "─"*60)
            print("INVESTMENT SUGGESTIONS")
            print("─"*60)
            for sug in insights["investment_suggestions"][:7]:  # Show first 7
                print(f"  {sug}")
        
        # Action Items
        if "action_items" in insights:
            print("\n" + "─"*60)
            print("ACTION ITEMS")
            print("─"*60)
            for action in insights["action_items"]:
                print(f"  {action}")
        
        # Financial Health
        if "financial_health" in insights:
            health = insights["financial_health"]
            print("\n" + "─"*60)
            print("FINANCIAL HEALTH ASSESSMENT")
            print("─"*60)
            print(f"  Overall Score: {health['score']}/100")
            print(f"  Rating: {health['rating']}")
            print(f"\n  Contributing Factors:")
            for factor in health["factors"]:
                print(f"    • {factor}")
        
        # Relevant Tips
        if "relevant_tips" in insights:
            print("\n" + "─"*60)
            print("RELEVANT FINANCIAL WISDOM")
            print("─"*60)
            for i, tip in enumerate(insights["relevant_tips"][:3], 1):
                print(f"  {i}. {tip}")
        
        return True
    else:
        print(f"❌ Failed to get insights: {response.status_code}")
        print(response.text)
        return False

def test_different_risk_profiles(user_id):
    """Test advice generation with different risk profiles"""
    print_section("3. COMPARING RISK PROFILES")
    
    for risk in ["low", "medium", "high"]:
        print(f"\n{'─'*60}")
        print(f"Risk Profile: {risk.upper()}")
        print('─'*60)
        
        response = requests.get(f"{BASE_URL}/insights/{user_id}?risk_profile={risk}")
        
        if response.status_code == 200:
            data = response.json()
            insights = data["insights"]
            
            if "investment_suggestions" in insights:
                print("\nInvestment Allocation:")
                for sug in insights["investment_suggestions"][:5]:
                    if "•" in sug or "allocation" in sug.lower():
                        print(f"  {sug}")
        
        time.sleep(0.5)  # Small delay between requests

def test_health_check():
    """Test health endpoint"""
    print_section("0. HEALTH CHECK")
    
    response = requests.get(f"{BASE_URL}/health")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Service Status: {data['status']}")
        print(f"📦 Service: {data['service']}")
        return True
    else:
        print(f"❌ Health check failed: {response.status_code}")
        return False

def main():
    print("\n" + "="*60)
    print("  RAG FINANCIAL ADVISOR - SYSTEM TEST")
    print("="*60)
    print("\nThis script demonstrates the RAG-powered financial advice system")
    print("Make sure the server is running: docker-compose up OR uvicorn app.main:app")
    
    input("\nPress Enter to start testing...")
    
    # Health check
    if not test_health_check():
        print("\n❌ Server is not running. Please start it first.")
        return
    
    # Upload transactions
    user_id = test_upload_csv()
    
    if user_id:
        time.sleep(1)
        
        # Get detailed insights
        test_get_insights(user_id, risk_profile="medium")
        
        time.sleep(1)
        
        # Compare risk profiles
        test_different_risk_profiles(user_id)
    
    print("\n" + "="*60)
    print("  TEST COMPLETE!")
    print("="*60)
    print("\n💡 Try these commands:")
    print(f"  • Get insights: curl {BASE_URL}/insights/{user_id}")
    print(f"  • View advice history: curl {BASE_URL}/advices/{user_id}")
    print(f"  • Start monitoring: curl -X POST {BASE_URL}/start_monitor/{user_id}")
    print("\n📚 See RAG_SYSTEM_GUIDE.md for complete documentation\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except requests.exceptions.ConnectionError:
        print("\n\n❌ Cannot connect to server. Please ensure it's running on port 8000")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
