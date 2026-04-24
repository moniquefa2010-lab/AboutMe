import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="HousingPulse Dashboard", layout="wide")

st.title("HousingPulse: U.S. Rent & Housing Affordability Analysis")
st.write("This dashboard analyzes the relationship between rent, housing prices, and affordability across U.S. states over time.")

@st.cache_data(ttl=600)
def load_data():
    url = "https://docs.google.com/spreadsheets/d/1qzakLa-HyV-0JMFknycrUqQbrG88vMdIC8MVSQN-Fng/export?format=csv&gid=1925372574"
    df = pd.read_csv(url)
    return df

df = load_data()

df["state"] = df["state"].astype(str).str.strip().str.upper()
df["year"] = pd.to_numeric(df["year"], errors="coerce")
df["rent"] = pd.to_numeric(df["rent"], errors="coerce")
df["hpi"] = pd.to_numeric(df["hpi"], errors="coerce")
df["affordability"] = pd.to_numeric(df["affordability"], errors="coerce")

df = df.dropna()

st.sidebar.header("Filters")

selected_states = st.sidebar.multiselect(
    "Select States",
    options=sorted(df["state"].unique()),
    default=["CA", "AL"]
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

st.subheader("Summary Metrics")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Average Rent", f"${filtered['rent'].mean():,.2f}")

with col2:
    st.metric("Average HPI", f"{filtered['hpi'].mean():.2f}")

with col3:
    corr = filtered["rent"].corr(filtered["hpi"])
    st.metric("Correlation (Rent vs HPI)", f"{corr:.2f}")

st.subheader("Data Preview")
st.dataframe(filtered)

years = sorted(filtered["year"].unique())
tick_years = years[::2]

st.subheader("Rent Trend Over Time")

fig, ax = plt.subplots(figsize=(10, 6))

for state in selected_states:
    state_data = filtered[filtered["state"] == state].sort_values("year")
    ax.plot(state_data["year"], state_data["rent"], marker="o", label=state)

ax.set_xlabel("Year")
ax.set_ylabel("Rent ($)")
ax.set_title("Rent Trend Over Time")
ax.set_xticks(tick_years)
ax.legend()
ax.grid(True)

st.pyplot(fig)

st.subheader("Housing Price Index Trend")

fig, ax = plt.subplots(figsize=(10, 6))

for state in selected_states:
    state_data = filtered[filtered["state"] == state].sort_values("year")
    ax.plot(state_data["year"], state_data["hpi"], marker="o", label=state)

ax.set_xlabel("Year")
ax.set_ylabel("Housing Price Index")
ax.set_title("Housing Price Index Trend Over Time")
ax.set_xticks(tick_years)
ax.legend()
ax.grid(True)

st.pyplot(fig)

st.subheader("Affordability Trend Over Time")

fig, ax = plt.subplots(figsize=(10, 6))

for state in selected_states:
    state_data = filtered[filtered["state"] == state].sort_values("year")
    ax.plot(state_data["year"], state_data["affordability"], marker="o", label=state)

ax.set_xlabel("Year")
ax.set_ylabel("Affordability Ratio")
ax.set_title("Affordability Trend Over Time")
ax.set_xticks(tick_years)
ax.legend()
ax.grid(True)

st.pyplot(fig)

st.subheader("Rent vs Housing Price Index")

fig, ax = plt.subplots(figsize=(10, 6))

ax.scatter(filtered["hpi"], filtered["rent"])

x = filtered["hpi"]
y = filtered["rent"]

if len(filtered) > 1:
    slope, intercept = np.polyfit(x, y, 1)
    trend_line = slope * x + intercept
    ax.plot(x, trend_line, linestyle="--", label="Trend Line")
    ax.legend()

ax.set_xlabel("Housing Price Index (HPI)")
ax.set_ylabel("Rent ($)")
ax.set_title("Relationship Between Rent and HPI")
ax.grid(True)

st.pyplot(fig)

st.subheader("Insights")

highest_rent = filtered.loc[filtered["rent"].idxmax()]
least_affordable = filtered.loc[filtered["affordability"].idxmax()]
lowest_affordable = filtered.loc[filtered["affordability"].idxmin()]

st.write(
    f"Highest rent observed: {highest_rent['state']} in {int(highest_rent['year'])} "
    f"with rent of ${highest_rent['rent']:,.2f}."
)

st.write(
    f"Least affordable selected state/year: {least_affordable['state']} in "
    f"{int(least_affordable['year'])}, where rent was highest relative to the housing price index."
)

st.write(
    f"Most affordable selected state/year: {lowest_affordable['state']} in "
    f"{int(lowest_affordable['year'])}, where rent was lower relative to the housing price index."
)

if corr > 0:
    st.write(
        f"The correlation value of {corr:.2f} shows a positive relationship between rent and HPI. "
        "This means that as housing prices increase, rent generally tends to increase too."
    )
else:
    st.write(
        f"The correlation value of {corr:.2f} shows a weak or negative relationship between rent and HPI."
    )

st.write(
    "Overall, this dashboard helps compare how rent, housing prices, and affordability change across states over time."
)
