
import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Retirement Scenario Comparison", layout="wide")

st.title("📊 Retirement Scenario A vs. B Comparison")
st.markdown("Compare two retirement scenarios side-by-side.")

def forecast(retire_age, withdraw_401k_age, social_security_age, annual_need,
             after_tax_start, dividend_start, after_tax_return, dividend_yield,
             capital_appreciation, end_age=95):

    tax_dividends = 0.15
    social_security_income = 60000

    ages = list(range(retire_age, end_age + 1))
    df = pd.DataFrame(index=ages)
    df.index.name = "Age"

    df["Spouse Income"] = np.where(df.index <= 60, 34000, 0)
    df["Dividend Income"] = np.where(df.index < 75, dividend_start * dividend_yield * (1 - tax_dividends), 0)

    df["After-Tax Draw"] = annual_need - df["Dividend Income"] - df["Spouse Income"]
    df["After-Tax Draw"] = df["After-Tax Draw"].clip(lower=0)

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

    df["401k Income"] = np.where(df.index >= withdraw_401k_age, 130900, 0)
    df["Social Security"] = np.where(df.index >= social_security_age, social_security_income, 0)
    df["Total Income"] = df[["Spouse Income", "Dividend Income", "401k Income", "Social Security"]].sum(axis=1)
    return df

# --- Sidebar for Scenario A ---
st.sidebar.header("Scenario A Inputs")
retire_age_a = st.sidebar.number_input("Retirement Age (A)", 50, 70, 53)
withdraw_401k_age_a = st.sidebar.number_input("401(k) Withdrawal Age (A)", 59, 75, 63)
social_security_age_a = st.sidebar.number_input("Social Security Start Age (A)", 62, 70, 67)
after_tax_start_a = st.sidebar.number_input("After-Tax Portfolio (A)", 0, 10000000, 1300000)
dividend_start_a = st.sidebar.number_input("Dividend Portfolio (A)", 0, 10000000, 1000000)
after_tax_return_a = st.sidebar.slider("After-Tax Return (A) %", 0.0, 10.0, 6.0) / 100
dividend_yield_a = st.sidebar.slider("Dividend Yield (A) %", 0.0, 10.0, 4.0) / 100
cap_growth_a = st.sidebar.slider("Capital Growth (A) %", 0.0, 10.0, 3.0) / 100
annual_need_a = st.sidebar.number_input("Spending Need (A)", 0, 300000, 100000)

# --- Sidebar for Scenario B ---
st.sidebar.header("Scenario B Inputs")
retire_age_b = st.sidebar.number_input("Retirement Age (B)", 50, 70, 57)
withdraw_401k_age_b = st.sidebar.number_input("401(k) Withdrawal Age (B)", 59, 75, 65)
social_security_age_b = st.sidebar.number_input("Social Security Start Age (B)", 62, 70, 67)
after_tax_start_b = st.sidebar.number_input("After-Tax Portfolio (B)", 0, 10000000, 1000000)
dividend_start_b = st.sidebar.number_input("Dividend Portfolio (B)", 0, 10000000, 800000)
after_tax_return_b = st.sidebar.slider("After-Tax Return (B) %", 0.0, 10.0, 5.0) / 100
dividend_yield_b = st.sidebar.slider("Dividend Yield (B) %", 0.0, 10.0, 4.0) / 100
cap_growth_b = st.sidebar.slider("Capital Growth (B) %", 0.0, 10.0, 3.0) / 100
annual_need_b = st.sidebar.number_input("Spending Need (B)", 0, 300000, 90000)

# Forecast both scenarios
df_a = forecast(retire_age_a, withdraw_401k_age_a, social_security_age_a, annual_need_a,
                after_tax_start_a, dividend_start_a, after_tax_return_a, dividend_yield_a,
                cap_growth_a)

df_b = forecast(retire_age_b, withdraw_401k_age_b, social_security_age_b, annual_need_b,
                after_tax_start_b, dividend_start_b, after_tax_return_b, dividend_yield_b,
                cap_growth_b)

# --- Display Results ---
st.subheader("Scenario A vs. B: Total Income")
st.line_chart(pd.DataFrame({"Scenario A": df_a["Total Income"], "Scenario B": df_b["Total Income"]}))

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📈 Scenario A Forecast")
    st.dataframe(df_a.style.format("{:.0f}"))

with col2:
    st.markdown("### 📉 Scenario B Forecast")
    st.dataframe(df_b.style.format("{:.0f}"))
