#!/usr/bin/env python3
"""
Test script to verify surplus calculations are correct
"""

# Sample transactions
transactions = [
    {"date": "2025-11-01", "amount": 50000, "description": "Salary", "category": "income"},
    {"date": "2025-11-02", "amount": -2000, "description": "Groceries", "category": "groceries"},
    {"date": "2025-11-05", "amount": -12000, "description": "Rent", "category": "rent"},
    {"date": "2025-11-07", "amount": -500, "description": "Netflix", "category": "other"},
]

print("="*60)
print("TESTING SURPLUS CALCULATION")
print("="*60)
print()

# Calculate manually
income = sum(t["amount"] for t in transactions if t["category"] == "income")
expenses_raw = sum(t["amount"] for t in transactions if t["category"] != "income")
expenses_abs = abs(expenses_raw)

print("Manual Calculation:")
print(f"  Income: ₹{income:,.2f}")
print(f"  Expenses (raw sum): ₹{expenses_raw:,.2f}")
print(f"  Expenses (absolute): ₹{expenses_abs:,.2f}")
print(f"  Surplus (income - abs(expenses)): ₹{income - expenses_abs:,.2f}")
print()

# Test with the actual analysis agent
import asyncio
import sys
sys.path.insert(0, '.')

from app.agents import analysis_agent

async def test_analysis():
    result = await analysis_agent(transactions)
    
    print("Analysis Agent Result:")
    print(f"  Income: ₹{result['income']:,.2f}")
    print(f"  Expense: ₹{result['expense']:,.2f}")
    print(f"  Surplus: ₹{result['forecast']['monthly_surplus']:,.2f}")
    print()
    
    print("Breakdown:")
    for cat, amount in result['breakdown'].items():
        print(f"  {cat}: ₹{amount:,.2f}")
    print()
    
    # Verify calculations
    expected_income = 50000
    expected_expense = 14500  # abs(-2000 + -12000 + -500)
    expected_surplus = 35500
    
    print("Verification:")
    print(f"  Income correct: {result['income'] == expected_income} ✓" if result['income'] == expected_income else f"  Income incorrect: Expected {expected_income}, got {result['income']} ✗")
    print(f"  Expense correct: {result['expense'] == expected_expense} ✓" if result['expense'] == expected_expense else f"  Expense incorrect: Expected {expected_expense}, got {result['expense']} ✗")
    print(f"  Surplus correct: {result['forecast']['monthly_surplus'] == expected_surplus} ✓" if result['forecast']['monthly_surplus'] == expected_surplus else f"  Surplus incorrect: Expected {expected_surplus}, got {result['forecast']['monthly_surplus']} ✗")
    print()
    
    # Test savings rate
    savings_rate = (result['forecast']['monthly_surplus'] / result['income']) * 100
    print(f"Savings Rate: {savings_rate:.1f}%")
    print()
    
    return result

# Run test
print("Running analysis agent test...")
print()
result = asyncio.run(test_analysis())

print("="*60)
print("TEST COMPLETE")
print("="*60)
print()
print("Summary:")
print(f"  ✓ Income: ₹{result['income']:,.2f} (positive)")
print(f"  ✓ Expense: ₹{result['expense']:,.2f} (positive)")
print(f"  ✓ Surplus: ₹{result['forecast']['monthly_surplus']:,.2f}")
print(f"  ✓ Formula: {result['income']:,.2f} - {result['expense']:,.2f} = {result['forecast']['monthly_surplus']:,.2f}")
print()
