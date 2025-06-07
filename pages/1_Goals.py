
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Goal-Based Spending", layout="wide")
st.title("🎯 Goal-Based Spending")

st.markdown("""Use this page to define custom financial goals that affect retirement
spending. These might include:

- 🚗 Car purchases
- 🏠 Home renovations
- ✈️ Major travel
- 💊 Medical procedures
""")

# Let the user define multiple goals
st.markdown("### Define Your Financial Goals")

with st.form("goals_form"):
    num_goals = st.slider("How many goals would you like to add?", 1, 5, 2)

    goals = []
    for i in range(num_goals):
        st.markdown(f"#### Goal {i + 1}")
        name = st.text_input(f"Name of Goal {i + 1}", key=f"name_{i}")
        age = st.number_input(f"Target Age for Goal {i + 1}", min_value=50, max_value=95, value=60, key=f"age_{i}")
        amount = st.number_input(f"Amount for Goal {i + 1}", min_value=1000, max_value=1000000, value=10000, key=f"amt_{i}")
        recurring = st.checkbox(f"Repeat yearly for 5 years?", key=f"repeat_{i}")
        goals.append({ "Name": name, "Age": age, "Amount": amount, "Recurring": recurring })

    submitted = st.form_submit_button("Save Goals")

if submitted:
    st.success("Goals Saved. These will be applied to the spending forecast.")

    # Build a goals DataFrame for export or application
    expanded_goals = []
    for g in goals:
        if g["Recurring"]:
            for offset in range(5):
                expanded_goals.append({ "Name": g["Name"], "Age": g["Age"] + offset, "Amount": g["Amount"] })
        else:
            expanded_goals.append({ "Name": g["Name"], "Age": g["Age"], "Amount": g["Amount"] })

    df_goals = pd.DataFrame(expanded_goals)
    st.dataframe(df_goals)

    # Offer download
    csv = df_goals.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download Goal Data as CSV", data=csv, file_name="retirement_goals.csv", mime="text/csv")
