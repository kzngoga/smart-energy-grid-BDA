import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from utils import get_db_engine

# ─── Page config ───
st.set_page_config(page_title="Smart Energy Grid", layout="wide")
st.title("Smart Energy Grid - Analytics & Dashboard")


def run_query(sql, label="Loading data..."):
    """Run a query and return a pandas DataFrame."""
    with st.spinner(label):
        engine = get_db_engine()
        return pd.read_sql(sql, engine)


def style_datetime_axis(fig, tickformat, hoverformat=None):
    """Apply readable date/time labels on the x-axis."""
    fig.update_xaxes(
        tickformat=tickformat,
        hoverformat=hoverformat or tickformat,
    )
    return fig


# ─────────────────────────────────────────
# Section 1: Real-time meter readings (last hour)
# ─────────────────────────────────────────
st.header("1. Real-Time Meter Readings (Last Hour)")

df_realtime = run_query("""
    SELECT time_bucket('5 minutes', timestamp) AS bucket,
           AVG(power) as avg_power
    FROM energy_readings
    WHERE timestamp >= (SELECT MAX(timestamp) - INTERVAL '1 hour' FROM energy_readings)
    GROUP BY bucket
    ORDER BY bucket
""", "Fetching real-time readings...")

df_realtime["bucket"] = pd.to_datetime(df_realtime["bucket"]).dt.floor("5min")

fig1 = px.line(df_realtime, x="bucket", y="avg_power",
               title="Average Power - Last Hour",
               labels={"bucket": "Time", "avg_power": "Avg Power (kW)"})
style_datetime_axis(fig1, tickformat="%H:%M", hoverformat="%Y-%m-%d %H:%M")
st.plotly_chart(fig1, width="stretch")


# ─────────────────────────────────────────
# Section 2: Daily consumption (today vs yesterday)
# ─────────────────────────────────────────
st.header("2. Daily Consumption Patterns")

df_daily = run_query("""
    SELECT DATE(time_bucket('1 hour', timestamp)) AS day,
           EXTRACT(HOUR FROM time_bucket('1 hour', timestamp))::int AS hour_of_day,
           AVG(power) AS avg_power
    FROM energy_readings
    WHERE timestamp >= (SELECT MAX(timestamp)::date - INTERVAL '2 days' FROM energy_readings)
    GROUP BY day, hour_of_day
    ORDER BY day, hour_of_day
""", "Fetching daily consumption...")

df_daily["day"] = pd.to_datetime(df_daily["day"]).dt.strftime("%Y-%m-%d")
days = sorted(df_daily["day"].unique())
df_plot = df_daily[df_daily["day"].isin(days[-2:])] if len(days) >= 2 else df_daily

df_plot = df_plot.copy()
df_plot["hour_label"] = df_plot["hour_of_day"].map(lambda h: f"{int(h):02d}:00")
hour_order = [f"{h:02d}:00" for h in range(24)]

fig2 = px.line(
    df_plot,
    x="hour_label",
    y="avg_power",
    color="day",
    title="Today vs Yesterday - Hourly Avg Power",
    labels={"hour_label": "Hour of day", "avg_power": "Avg Power (kW)", "day": "Date"},
    category_orders={"hour_label": hour_order},
)
fig2.update_xaxes(type="category")
st.plotly_chart(fig2, width="stretch")


# ─────────────────────────────────────────
# Section 3: Weekly trends
# ─────────────────────────────────────────
st.header("3. Weekly Trends")

df_weekly = run_query("""
    SELECT time_bucket('1 day', timestamp) AS day,
           AVG(power) as avg_power,
           SUM(energy) as total_energy
    FROM energy_readings
    WHERE timestamp >= (SELECT MAX(timestamp) - INTERVAL '7 days' FROM energy_readings)
    GROUP BY day
    ORDER BY day
""", "Fetching weekly trends...")

df_weekly["day"] = pd.to_datetime(df_weekly["day"]).dt.floor("D")

fig3 = px.bar(df_weekly, x="day", y="total_energy",
              title="Daily Total Energy Consumption - Last 7 Days",
              labels={"day": "Date", "total_energy": "Total Energy (kWh)"})
style_datetime_axis(fig3, tickformat="%b %d", hoverformat="%Y-%m-%d")
st.plotly_chart(fig3, width="stretch")


# ─────────────────────────────────────────
# Section 4: Monthly energy usage by region
# ─────────────────────────────────────────
st.header("4. Monthly Energy Usage by Region")
st.caption("Meters grouped by first digit of meter ID (e.g. 1xxxxxxxx = Region 1)")

df_region = run_query("""
    SELECT LEFT(meter_id, 1) as region,
           DATE_TRUNC('month', timestamp) as month,
           SUM(energy) as total_energy
    FROM energy_readings
    GROUP BY region, month
    ORDER BY month, region
""", "Fetching regional usage...")

df_region["region"] = "Region " + df_region["region"]

df_region["month"] = pd.to_datetime(df_region["month"]).dt.to_period("M").dt.to_timestamp()

fig4 = px.bar(df_region, x="month", y="total_energy", color="region",
              title="Monthly Energy Usage by Region",
              labels={"month": "Month", "total_energy": "Total Energy (kWh)", "region": "Region"},
              barmode="group")
style_datetime_axis(fig4, tickformat="%b %Y", hoverformat="%b %Y")
st.plotly_chart(fig4, width="stretch")


# ─────────────────────────────────────────
# Section 5: Performance metrics panel
# ─────────────────────────────────────────
st.header("5. Performance Metrics")

# ─── 5a: Raw vs aggregated query time ───
st.subheader("Query Execution Time: Raw vs Aggregated View")

df_perf = pd.DataFrame({
    "Query Type": ["Raw Data", "Continuous Aggregation"],
    "Time (ms)":  [448.925, 41.379]
})
fig5 = px.bar(df_perf, x="Query Type", y="Time (ms)", color="Query Type",
              title="15-min Avg Power Query: Raw vs Aggregated",
              labels={"Time (ms)": "Execution Time (ms)"})
st.plotly_chart(fig5, width="stretch")

# ─── 5b: Storage before vs after compression ───
st.subheader("Storage Efficiency: Before vs After Compression")

df_storage = pd.DataFrame({
    "Table":       ["energy_readings", "energy_readings_3h", "energy_readings_week"],
    "Before (MB)": [780, 791, 780],
    "After (MB)":  [395, 410, 392]
})
fig6 = go.Figure(data=[
    go.Bar(name="Before Compression", x=df_storage["Table"], y=df_storage["Before (MB)"]),
    go.Bar(name="After Compression",  x=df_storage["Table"], y=df_storage["After (MB)"])
])
fig6.update_layout(barmode="group", title="Disk Usage Before vs After Compression",
                   yaxis_title="Size (MB)")
st.plotly_chart(fig6, width="stretch")

# ─── 5c: Chunk strategy performance comparison ───
st.subheader("Query Performance by Chunk Strategy")

df_chunk = pd.DataFrame({
    "Query":              ["Q1", "Q2", "Q3", "Q4"],
    "3h chunks (ms)":    [292.465, 769.295, 16891.154, 611.979],
    "1-day chunks (ms)": [71.448, 301.371, 3419.732, 397.062],
    "1-week chunks (ms)":[121.676, 1810.048, 5314.832, 457.101]
})
fig7 = go.Figure(data=[
    go.Bar(name="3h chunks",    x=df_chunk["Query"], y=df_chunk["3h chunks (ms)"]),
    go.Bar(name="1-day chunks", x=df_chunk["Query"], y=df_chunk["1-day chunks (ms)"]),
    go.Bar(name="1-week chunks",x=df_chunk["Query"], y=df_chunk["1-week chunks (ms)"])
])
fig7.update_layout(barmode="group", title="Query Execution Time by Chunk Strategy",
                   yaxis_title="Execution Time (ms)")
st.plotly_chart(fig7, width="stretch")