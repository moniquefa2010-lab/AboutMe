import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Page Setup
st.set_page_config(page_title="HousingPulse Dashboard", layout="wide")

#App title and purpose
st.title("HousingPulse: U.S. Rent & Housing Affordability Analysis")
st.write("This dashboard analyzes the relationship between rent, housing prices, and affordability across U.S. states over time.")

#Load Live Google Sheets Data
@st.cache_data(ttl=5)
def load_data():
    url = "https://docs.google.com/spreadsheets/d/1qzakLa-HyV-0JMFknycrUqQbrG88vMdIC8MVSQN-Fng/export?format=csv&gid=1925372574"
    df = pd.read_csv(url)
    return df

df = load_data()


#Cleans and Prepares Data
df["state"] = df["state"].astype(str).str.strip().str.upper()
df["year"] = pd.to_numeric(df["year"], errors="coerce")
df["rent"] = pd.to_numeric(df["rent"], errors="coerce")
df["hpi"] = pd.to_numeric(df["hpi"], errors="coerce")

# Create affordability ratio
# Higher ratio = less affordable, lower ratio = more affordable
df["affordability"] = df["rent"] / df["hpi"]

df = df.dropna()

#Sidebar filters
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

#Filter data based on user selections
filtered = df[
    (df["state"].isin(selected_states)) &
    (df["year"].between(year_range[0], year_range[1]))
]

if filtered.empty:
    st.warning("Select at least one state.")
    st.stop()

#Summary metrics
st.subheader("📊 Key Metrics")
st.write("These metrics summarize the selected states and years.")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("💰 Average Rent", f"${filtered['rent'].mean():,.0f}")

with col2:
    st.metric("🏠 Average HPI", f"{filtered['hpi'].mean():.1f}")

with col3:
    corr = filtered["rent"].corr(filtered["hpi"])
    st.metric("📈 Rent vs HPI Correlation", f"{corr:.2f}")

st.caption("💡 Rent is in USD ($). HPI is an index with base = 100, not a dollar value.")


#Data preview
st.subheader("Data Preview")
st.write("This table shows the filtered data used in the dashboard.")
st.dataframe(filtered)

#Prepare x-axis year ticks
years = sorted(filtered["year"].unique())
tick_years = years[::2]

#Rent trend chart
st.subheader("Rent Trend Over Time")
st.write("This chart shows how average rent changes over time for the selected states.")

fig, ax = plt.subplots(figsize=(10, 6))

for state in selected_states:
    state_data = filtered[filtered["state"] == state].sort_values("year")
    ax.plot(state_data["year"], state_data["hpi"], marker="o", label=state)

ax.set_xlabel("Year")
ax.set_ylabel("Rent ($)")
ax.set_title("Rent Trend Over Time")
ax.set_xticks(tick_years)
ax.legend()
ax.grid(True)

st.pyplot(fig)

#HPI trend chart
st.subheader("Housing Price Index Trend")
st.write("This chart shows how housing price index values change over time.")

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


#Affordability ratio explanation
st.subheader("Affordability Trend Over Time")
st.write(""" **Affordability Ratio = Rent ÷ Housing Price Index (HPI)** 
- Higher ratio = less affordable because rent is high compared to housing value trends.
- Lower ratio = more affordable because rent is lower compared to housing value trends.

This ratio helps compare rent pressure across states more clearly.
""")

# Affordability trend chart
st.subheader("Affordability Trend Over Time")
st.write("This chart shows whether affordability pressure is increasing or decreasing over time.")

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


#Scatterplot relationship
st.subheader("Rent vs Housing Price Index")
st.write("This chart shows the relationship between rent and housing price index values.")

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

#State affordability rankings
st.subheader("State Affordability Rankings")
st.write("""
These rankings use the most recent selected year to compare states by affordability ratio.
Lower affordability ratio means the state is more affordable.
""")

latest_year = df["year"].max()
latest_data = df[df["year"] == latest_year]

most_affordable_ranked = latest_data.sort_values(by="affordability").head(5)
least_affordable_ranked = latest_data.sort_values(by="affordability", ascending=False).head(5)

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🟢 Most Affordable")
    st.dataframe(most_affordable_ranked[["state", "year", "rent", "hpi", "affordability"]])

with col2:
    st.markdown("### 🔴 Least Affordable")
    st.dataframe(least_affordable_ranked[["state", "year", "rent", "hpi", "affordability"]])



# Insights section
st.subheader("Insights")
st.write("This section summarizes the key takeaways from the selected data.")

highest_rent = filtered.loc[filtered["rent"].idxmax()]
least_affordable = filtered.loc[filtered["affordability"].idxmax()]
most_affordable = filtered.loc[filtered["affordability"].idxmin()]

corr = filtered["rent"].corr(filtered["hpi"])

st.write(f"**Highest rent:** {highest_rent['state']} ({int(highest_rent['year'])}) — ${highest_rent['rent']:,.0f}")
st.write(f"**Least affordable:** {least_affordable['state']} ({int(least_affordable['year'])})")
st.write(f"**Most affordable:** {most_affordable['state']} ({int(most_affordable['year'])})")
st.write(f"**Correlation:** Rent and HPI have a positive relationship of {corr:.2f}.")
st.write("""
**Overall takeaway:** HousingPulse shows how rent, housing prices, and affordability move over time.
This helps users identify which states may be experiencing stronger affordability pressure.
""")
