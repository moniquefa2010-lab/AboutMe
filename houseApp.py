import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="HousingPulse Dashboard", layout="wide")

st.title("HousingPulse Dashboard")
st.write("Compare rent and housing prices across U.S. states over time.")

# Load LIVE data from Google Sheets
@st.cache_data(ttl=600)
def load_data():
    url = "https://docs.google.com/spreadsheets/d/1qzakLa-HyV-0JMFknycrUqQbrG88vMdIC8MVSQN-Fng/export?format=csv&gid=1925372574"
    df = pd.read_csv(url)
    return df

df = load_data()

# Clean data
df["state"] = df["state"].astype(str).str.strip().str.upper()
df["year"] = pd.to_numeric(df["year"], errors="coerce")
df["rent"] = pd.to_numeric(df["rent"], errors="coerce")
df["hpi"] = pd.to_numeric(df["hpi"], errors="coerce")
df["affordability"] = pd.to_numeric(df["affordability"], errors="coerce")

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

# Summary metrics
st.subheader("Summary Metrics")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Average Rent", f"${filtered['rent'].mean():,.2f}")

with col2:
    st.metric("Average HPI", f"{filtered['hpi'].mean():.2f}")

with col3:
    corr = filtered["rent"].corr(filtered["hpi"])
    st.metric("Correlation (Rent vs HPI)", f"{corr:.2f}")

# Data preview
st.subheader("Data Preview")
st.dataframe(filtered)

# Rent Trend (YEAR ON X-AXIS)
st.subheader("Rent Trend Over Time")

rent_chart = filtered.pivot(index="year", columns="state", values="rent")
st.line_chart(rent_chart)

# HPI Trend
st.subheader("Housing Price Index Trend")

hpi_chart = filtered.pivot(index="year", columns="state", values="hpi")
st.line_chart(hpi_chart)

# Scatter plot
st.subheader("Rent vs Housing Price Index")

fig, ax = plt.subplots()
ax.scatter(filtered["hpi"], filtered["rent"])

ax.set_xlabel("Housing Price Index (HPI)")
ax.set_ylabel("Rent ($)")
ax.set_title("Relationship Between Rent and HPI")

st.pyplot(fig)

# Insights
st.subheader("Insights")

highest_rent = filtered.loc[filtered["rent"].idxmax()]
least_affordable = filtered.loc[filtered["affordability"].idxmax()]

st.write(
    f"Highest rent observed in {highest_rent['state']} during {int(highest_rent['year'])}."
)

st.write(
    f"{least_affordable['state']} is the least affordable based on rent-to-HPI ratio."
)

st.write(
    "Overall, rent and housing prices tend to move together, as shown by the positive correlation."
)
