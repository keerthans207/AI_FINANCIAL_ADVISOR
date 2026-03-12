import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# CHANGE THIS TO YOUR SERVER IP IF NEEDED
API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="AI Financial Advisor",
    page_icon="💰",
    layout="wide",
)

# ---------- DARK MODE STYLE ----------
st.markdown(
    """
    <style>
    body {background-color:#0E1117;}
    .stMetric {
        background-color:#1f2937;
        padding:15px;
        border-radius:12px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------- SIDEBAR ----------
st.sidebar.title("💰 FinAI Dashboard")
page = st.sidebar.radio(
    "Navigation",
    ["Upload & Analysis", "Financial Charts", "AI Chat Advisor"]
)

# ---------- PAGE 1 ----------
if page == "Upload & Analysis":

    st.title("📊 Monthly Expense Analyzer")

    uploaded_file = st.file_uploader("Upload your expenses CSV", type=["csv"])

    if uploaded_file:

        files = {"file": uploaded_file}

        response = requests.post(
            f"{API_URL}/upload_csv",
            files=files
        )

        if response.status_code == 200:

            data = response.json()
            analysis = data.get("analysis", {})

            col1, col2, col3 = st.columns(3)

            col1.metric("Income", f"${analysis.get('income',0):,.2f}")
            col2.metric("Expenses", f"${analysis.get('expense',0):,.2f}")

            surplus = analysis.get("forecast", {}).get("monthly_surplus", 0)
            col3.metric("Surplus", f"${surplus:,.2f}")

            st.session_state["analysis_data"] = analysis

            # Handle advice safely
            advice_data = data.get("advice", [])

            if isinstance(advice_data, dict):
                st.session_state["advice"] = list(advice_data.values())
            elif isinstance(advice_data, list):
                st.session_state["advice"] = advice_data
            else:
                st.session_state["advice"] = [str(advice_data)]

        else:
            st.error("Backend error")

# ---------- PAGE 2 ----------
elif page == "Financial Charts":

    st.title("📈 Expense Breakdown")

    if "analysis_data" in st.session_state:

        analysis = st.session_state["analysis_data"]

        breakdown = analysis.get("breakdown", {})

        if breakdown:

            df = pd.DataFrame(
                list(breakdown.items()),
                columns=["Category", "Amount"]
            )

            col1, col2 = st.columns(2)

            with col1:
                fig = px.pie(
                    df,
                    names="Category",
                    values="Amount",
                    title="Expense Distribution"
                )
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                fig2 = px.bar(
                    df,
                    x="Category",
                    y="Amount",
                    title="Category Spending"
                )
                st.plotly_chart(fig2, use_container_width=True)

        else:
            st.info("No expense data available.")

    else:
        st.info("Upload a CSV first.")

# ---------- PAGE 3 ----------
elif page == "AI Chat Advisor":

    st.title("🤖 Financial AI Advisor")

    if "advice" in st.session_state:

        st.subheader("Generated Advice")

        for line in st.session_state["advice"]:
            st.write("•", line)

    st.divider()

    user_prompt = st.chat_input("Ask a financial question")

    if user_prompt:

        st.chat_message("user").write(user_prompt)

        try:

            response = requests.post(
                f"{API_URL}/ask",
                json={"question": user_prompt},
                timeout=60
            )

            if response.status_code == 200:
                answer = response.json().get("answer", "No response from AI")
            else:
                answer = "Backend returned an error."

        except Exception:
            answer = "Chat endpoint not available yet."

        st.chat_message("assistant").write(answer)
