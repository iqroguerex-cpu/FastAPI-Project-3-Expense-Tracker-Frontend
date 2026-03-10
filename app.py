import streamlit as st
import requests
import pandas as pd
import plotly.express as px

API_URL = "https://fastapi-project-3-expense-tracker-backend.onrender.com"

st.set_page_config(page_title="Expense Tracker", layout="wide")

st.title("💰 Expense Tracker Dashboard")

# ---------------------------
# API FUNCTIONS
# ---------------------------

def fetch_expenses():
    try:
        response = requests.get(f"{API_URL}/expenses", timeout=5)
        if response.status_code == 200:
            return response.json()
        return []
    except:
        st.error("Backend not reachable")
        return []

def create_expense(data):
    requests.post(f"{API_URL}/expenses/create_expense", json=data)

def delete_expense(expense_id):
    requests.delete(f"{API_URL}/expenses/delete_expense/{expense_id}")

# ---------------------------
# LOAD DATA
# ---------------------------

expenses = fetch_expenses()

df = pd.DataFrame(expenses)

if df.empty:
    st.warning("No expenses available.")
else:
    df["date"] = pd.to_datetime(df["date"])

# ---------------------------
# METRICS
# ---------------------------

if not df.empty:

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Expenses", len(df))

    with col2:
        st.metric("Total Spending", f"${df['amount'].sum():.2f}")

    with col3:
        st.metric("Average Expense", f"${df['amount'].mean():.2f}")

    st.divider()

# ---------------------------
# CHARTS
# ---------------------------

if not df.empty:

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("📊 Category Spending")

        category_data = df.groupby("category")["amount"].sum().reset_index()

        fig = px.pie(
            category_data,
            names="category",
            values="amount",
            title="Expenses by Category"
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:

        st.subheader("📈 Monthly Spending")

        monthly = df.groupby(df["date"].dt.to_period("M"))["amount"].sum().reset_index()

        monthly["date"] = monthly["date"].astype(str)

        fig2 = px.bar(
            monthly,
            x="date",
            y="amount",
            title="Monthly Expenses"
        )

        st.plotly_chart(fig2, use_container_width=True)

st.divider()

# ---------------------------
# ADD EXPENSE
# ---------------------------

st.subheader("➕ Add Expense")

with st.form("add_expense_form"):

    col1, col2 = st.columns(2)

    title = col1.text_input("Title")

    amount = col2.number_input("Amount", min_value=0.0)

    col3, col4 = st.columns(2)

    category = col3.text_input("Category")

    date = col4.date_input("Date")

    submitted = st.form_submit_button("Add Expense")

    if submitted:

        new_expense = {
            "id": int(pd.Timestamp.now().timestamp()),
            "title": title,
            "amount": amount,
            "category": category,
            "date": str(date)
        }

        create_expense(new_expense)

        st.success("Expense Added")

        st.rerun()

st.divider()

# ---------------------------
# FILTER
# ---------------------------

if not df.empty:

    st.subheader("🔍 Filter")

    categories = ["All"] + list(df["category"].unique())

    selected = st.selectbox("Category", categories)

    if selected != "All":
        df = df[df["category"] == selected]

# ---------------------------
# EXPORT CSV
# ---------------------------

if not df.empty:

    csv = df.to_csv(index=False)

    st.download_button(
        "📤 Export Expenses CSV",
        data=csv,
        file_name="expenses.csv",
        mime="text/csv"
    )

# ---------------------------
# EXPENSE LIST
# ---------------------------

st.subheader("📋 Expense List")

if df.empty:

    st.info("No expenses to display.")

else:

    for _, row in df.iterrows():

        col1, col2, col3, col4, col5 = st.columns([2,2,2,2,1])

        col1.write(row["title"])
        col2.write(f"${row['amount']}")
        col3.write(row["category"])
        col4.write(row["date"].date())

        if col5.button("Delete", key=row["id"]):

            delete_expense(row["id"])

            st.success("Expense Deleted")

            st.rerun()
