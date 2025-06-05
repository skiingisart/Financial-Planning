import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Retirement Planner", layout="centered")

st.title("📊 Retirement Income Planner")
st.markdown("Enter your assumptions below to forecast retirement cash flow.")

# --- Input Section ---
st.sidebar.header("Assumptions")
retire_age = st.sidebar.number_input("Retirement Age", 50, 70, 53)
withdraw_401k_age = st.sidebar.number_input("401(k) Withdrawal Age", 59, 75, 63)
social_security_age = st.sidebar.number_input("Social Security Start Age", 62, 70, 67)
end_age = 95

annual_need = st.sidebar.number_input("Annual Spending Need (Real, After-Tax)", 0, 300000, 100000)
after_tax_start = st.sidebar.number_input("After-Tax Portfolio at Retirement", 0, 10000000, 1300000)
dividend_start = st.sidebar.number_input("Dividend Portfolio at Retirement", 0, 10000000, 1000000)

# Rates
after_tax_return = st.sidebar.slider("After-Tax Portfolio Return (%)", 0.0, 10.0, 6.0) / 100
dividend_yield = st.sidebar.slider("Dividend Yield (%)", 0.0, 10.0, 4.0) / 100
capital_appreciation = st.sidebar.slider("Dividend Growth Rate (%)", 0.0, 10.0, 3.0) / 100
inflation = st.sidebar.slider("Inflation Rate (%)", 0.0, 10.0, 2.5) / 100

# Taxes
tax_dividends = 0.15
tax_401k = 0.14

# Social Security
social_security_income = 60000

# Build Forecast
ages = list(range(retire_age, end_age + 1))
df = pd.DataFrame(index=ages)
df.index.name = "Age"

# Spouse income fixed to 34K through 60
df["Spouse Income"] = np.where(df.index <= 60, 34000, 0)

# Base dividend income
df["Dividend Income"] = np.where(df.index < 75, dividend_start * dividend_yield * (1 - tax_dividends), 0)

# After-tax draw
df["After-Tax Draw"] = annual_need - df["Dividend Income"] - df["Spouse Income"]
df["After-Tax Draw"] = df["After-Tax Draw"].clip(lower=0)

# After-tax balance growth and draw
after_tax_balance = after_tax_start
balances = []
for age in df.index:
    if age < withdraw_401k_age:
        after_tax_balance *= (1 + after_tax_return)
        after_tax_balance -= df.loc[age, "After-Tax Draw"]
    else:
        after_tax_balance *= (1 + after_tax_return)
    balances.append(after_tax_balance)
df["After-Tax Balance"] = balances

# Dividend portfolio growth and drawdown
div_balance = dividend_start
div_balances = []
for age in df.index:
    if age < 75:
        div_balance *= (1 + capital_appreciation)
    elif age == 75:
        years = end_age - 75 + 1
        r = capital_appreciation
        pmt = div_balance * (r * (1 + r)**years) / ((1 + r)**years - 1)
    if age >= 75:
        div_balance *= (1 + capital_appreciation)
        div_balance -= pmt
        df.loc[age, "Dividend Income"] = pmt * (1 - tax_dividends)
    div_balances.append(div_balance)
df["Dividend Balance"] = div_balances

# 401k Income
df["401k Income"] = np.where(df.index >= withdraw_401k_age, 130900, 0)

# Social Security
df["Social Security"] = np.where(df.index >= social_security_age, social_security_income, 0)

# Total Income
df["Total Income"] = df[["Spouse Income", "Dividend Income", "401k Income", "Social Security"]].sum(axis=1)

# --- Output Section ---
st.subheader("Summary Forecast")
st.line_chart(df[["Total Income"]])
st.dataframe(df.style.format("{:.0f}"))

# Download option
csv = df.to_csv().encode("utf-8")
st.download_button("📥 Download Forecast as CSV", data=csv, file_name="retirement_forecast.csv", mime="text/csv")
