
import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Base Forecast", layout="wide")
st.title("🏠 Base Retirement Forecast")

st.markdown("""Use the sidebar to adjust retirement parameters for Scenario A and B,
then compare results including income, 401(k) balance, and downloadable forecast.
""")

adjust_for_inflation = st.sidebar.checkbox("Adjust for Inflation (2%)", value=True)
inflation_rate = 0.02 if adjust_for_inflation else 0.0

def forecast(retire_age, withdraw_401k_age, social_security_age, annual_need,
             after_tax_start, dividend_start, after_tax_return, dividend_yield,
             capital_appreciation, contrib_start_age, contrib_end_age,
             annual_contribution, return_401k, roth_pct, withdraw_tax_rate,
             end_age=95):

    tax_dividends = 0.15
    social_security_income = 60000
    roth_ratio = roth_pct / 100

    ages = list(range(min(retire_age, contrib_start_age), end_age + 1))
    df = pd.DataFrame(index=ages)
    df.index.name = "Age"

    df["Spouse Income"] = np.where(df.index <= 60, 34000, 0)
    df["Dividend Income"] = np.where(df.index < 75, dividend_start * dividend_yield * (1 - tax_dividends), 0)
    df["After-Tax Draw"] = annual_need - df["Dividend Income"] - df["Spouse Income"]
    df["After-Tax Draw"] = df["After-Tax Draw"].clip(lower=0)

    after_tax_balance = after_tax_start
    balances = []
    for age in df.index:
        after_tax_balance *= (1 + after_tax_return - inflation_rate)
        if age < withdraw_401k_age:
            after_tax_balance -= df.loc[age, "After-Tax Draw"]
        balances.append(after_tax_balance)
    df["After-Tax Balance"] = balances

    div_balance = dividend_start
    div_balances = []
    pmt = 0
    for age in df.index:
        if age < 75:
            div_balance *= (1 + capital_appreciation - inflation_rate)
        elif age == 75:
            years = end_age - 75 + 1
            r = capital_appreciation - inflation_rate
            pmt = div_balance * (r * (1 + r)**years) / ((1 + r)**years - 1)
        if age >= 75:
            div_balance *= (1 + capital_appreciation - inflation_rate)
            div_balance -= pmt
            df.loc[age, "Dividend Income"] = pmt * (1 - tax_dividends)
        div_balances.append(div_balance)
    df["Dividend Balance"] = div_balances

    balance_401k = 865000
    balance_401k_values = []
    income_401k_values = []
    for age in df.index:
        if contrib_start_age <= age <= contrib_end_age:
            balance_401k += annual_contribution
        if age < withdraw_401k_age:
            balance_401k *= (1 + return_401k - inflation_rate)
            income_401k_values.append(0)
        else:
            draw_years = end_age - withdraw_401k_age + 1
            r = return_401k - inflation_rate
            withdrawal = balance_401k * (r * (1 + r)**draw_years) / ((1 + r)**draw_years - 1)
            balance_401k *= (1 + return_401k - inflation_rate)
            balance_401k -= withdrawal
            tax = withdrawal * (1 - roth_ratio) * withdraw_tax_rate
            income_401k_values.append(withdrawal - tax)
        balance_401k_values.append(balance_401k)

    df["401k Income"] = [0]*(withdraw_401k_age - ages[0]) + income_401k_values
    df["401k Balance"] = balance_401k_values
    df["Social Security"] = np.where(df.index >= social_security_age, social_security_income, 0)
    df["Total Income"] = df[["Spouse Income", "Dividend Income", "401k Income", "Social Security"]].sum(axis=1)
    df["Gap"] = df["Total Income"] - annual_need
    return df

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
contrib_start_a = st.sidebar.number_input("401k Contrib Start Age (A)", 40, 70, 50)
contrib_end_a = st.sidebar.number_input("401k Contrib End Age (A)", 40, 70, 53)
contrib_amt_a = st.sidebar.number_input("401k Annual Contribution (A)", 0, 200000, 90000)
return_401k_a = st.sidebar.slider("401k Return Rate (A) %", 0.0, 10.0, 7.0) / 100
roth_pct_a = st.sidebar.slider("Roth % (A)", 0, 100, 30)
tax_401k_a = st.sidebar.slider("401k Tax Rate % (A)", 0, 50, 22) / 100

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
contrib_start_b = st.sidebar.number_input("401k Contrib Start Age (B)", 40, 70, 50)
contrib_end_b = st.sidebar.number_input("401k Contrib End Age (B)", 40, 70, 55)
contrib_amt_b = st.sidebar.number_input("401k Annual Contribution (B)", 0, 200000, 90000)
return_401k_b = st.sidebar.slider("401k Return Rate (B) %", 0.0, 10.0, 6.5) / 100
roth_pct_b = st.sidebar.slider("Roth % (B)", 0, 100, 30)
tax_401k_b = st.sidebar.slider("401k Tax Rate % (B)", 0, 50, 22) / 100

df_a = forecast(retire_age_a, withdraw_401k_age_a, social_security_age_a, annual_need_a,
                after_tax_start_a, dividend_start_a, after_tax_return_a, dividend_yield_a,
                cap_growth_a, contrib_start_a, contrib_end_a, contrib_amt_a,
                return_401k_a, roth_pct_a, tax_401k_a)

df_b = forecast(retire_age_b, withdraw_401k_age_b, social_security_age_b, annual_need_b,
                after_tax_start_b, dividend_start_b, after_tax_return_b, dividend_yield_b,
                cap_growth_b, contrib_start_b, contrib_end_b, contrib_amt_b,
                return_401k_b, roth_pct_b, tax_401k_b)

st.subheader("💵 Total Income Comparison")
st.line_chart(pd.DataFrame({ "Scenario A": df_a["Total Income"], "Scenario B": df_b["Total Income"] }))

st.subheader("📈 401(k) Balance Comparison")
st.line_chart(pd.DataFrame({ "Scenario A": df_a["401k Balance"], "Scenario B": df_b["401k Balance"] }))

def convert_df_to_excel(dfa, dfb):
    import io
    from pandas import ExcelWriter
    output = io.BytesIO()
    with ExcelWriter(output, engine='xlsxwriter') as writer:
        dfa.to_excel(writer, sheet_name='Scenario A')
        dfb.to_excel(writer, sheet_name='Scenario B')
    return output.getvalue()

excel_data = convert_df_to_excel(df_a, df_b)
st.download_button("📥 Download Forecasts (Excel)", data=excel_data, file_name="retirement_forecasts.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

col1, col2 = st.columns(2)
with col1:
    st.markdown("### 📊 Scenario A")
    st.dataframe(df_a.style.format("{:.0f}"))
with col2:
    st.markdown("### 📊 Scenario B")
    st.dataframe(df_b.style.format("{:.0f}"))
