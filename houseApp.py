import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="HousingPulse Dashboard", layout="wide")

st.title("HousingPulse Dashboard")
st.write("Compare rent and housing prices across U.S. states.")

# LIVE merged dataset load (Google Sheets)
@st.cache_data(ttl=600)
def load_data():
    url = "https://docs.google.com/spreadsheets/d/1qzakLa-HyV-0JMFknycrUqQbrG88vMdIC8MVSQN-Fng/export?format=csv&gid=1925372574"
    df = pd.read_csv(url)
    return df

df = load_data()

# Clean just in case
df["state"] = df["state"].astype(str).str.strip().str.upper()
df["year"] = pd.to_numeric(df["year"], errors="coerce")
df["rent"] = pd.to_numeric(df["rent"], errors="coerce")
df["hpi"] = pd.to_numeric(df["hpi"], errors="coerce")

df = df.dropna()

# Sidebar filters
st.sidebar.header("Filters")

selected_states = st.sidebar.multiselect(
    "Select States",
    options=sorted(df["state"].unique()),
    default=["CA", "TX"]
)

year_range = st.sidebar.slider(
    "Select Year Range",
    int(df["year"].min()),
    int(df["year"].max()),
    (2000, 2020)
)

filtered = df[
    (df["state"].isin(selected_states)) &
    (df["year"].between(year_range[0], year_range[1]))
]

if filtered.empty:
    st.warning("Select at least one state.")
    st.stop()

# Summary
st.subheader("Summary Metrics")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Average Rent", f"${filtered['rent'].mean():,.2f}")

with col2:
    st.metric("Average HPI", f"{filtered['hpi'].mean():.2f}")

with col3:
    corr = filtered["rent"].corr(filtered["hpi"])
    st.metric("Correlation", f"{corr:.2f}")

# Data
st.subheader("Data Preview")
st.dataframe(filtered)

# Rent Trend (TIME COMPONENT)
st.subheader("Rent Trend Over Time")
rent_chart = filtered.pivot(index="year", columns="state", values="rent")
st.line_chart(rent_chart)

# HPI Trend
st.subheader("Housing Price Index Trend")
hpi_chart = filtered.pivot(index="year", columns="state", values="hpi")
st.line_chart(hpi_chart)

# Scatter
st.subheader("Rent vs Housing Price Index")

fig, ax = plt.subplots(figsize=(10, 6))
ax.scatter(filtered["hpi"], filtered["rent"])

ax.set_xlabel("Housing Price Index")
ax.set_ylabel("Rent")
ax.set_title("HPI vs Rent")
ax.grid(True)

st.pyplot(fig)

# Insights
st.subheader("Insights")

highest = filtered.loc[filtered["rent"].idxmax()]
least_affordable = filtered.loc[filtered["affordability"].idxmax()]

st.write(f"Highest rent: {highest['state']} in {int(highest['year'])}")
st.write(f"Least affordable: {least_affordable['state']} in {int(least_affordable['year'])}")
st.write("Higher affordability = rent is high relative to housing prices.")
