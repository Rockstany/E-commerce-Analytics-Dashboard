import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ---------------------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------------------
st.set_page_config(page_title="User Analytics", page_icon="👥", layout="wide")

st.markdown("""
    <style>
    .main {padding: 0rem 1rem;}
    h1 {color: #1f77b4; border-bottom: 3px solid #1f77b4; padding-bottom: 10px;}
    </style>
""", unsafe_allow_html=True)

st.title("👥 User Analytics Dashboard")
st.markdown("### Track user engagement, retention, and loyalty")

# ---------------------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------------------
@st.cache_data
def load_data():
    try:
        users = pd.read_csv("raw_data/user_table.csv")
        sessions = pd.read_csv("aggregated_data/session_attribution.csv")
        user_metrics = pd.read_csv("aggregated_data/user_lifetime_metrics.csv")
        return users, sessions, user_metrics
    except FileNotFoundError:
        st.error("❌ Missing one of the required CSV files")
        return None, None, None

users_df, sessions_df, user_metrics_df = load_data()

if users_df is None or sessions_df is None:
    st.stop()

# ---------------------------------------------------------------------
# DATE PROCESSING
# ---------------------------------------------------------------------
if "date" in sessions_df.columns:
    sessions_df["date"] = pd.to_datetime(sessions_df["date"])

    col1, col2 = st.columns(2)

    with col1:
        start_date = st.date_input(
            "Start Date",
            value=sessions_df["date"].max().date() - timedelta(days=30),
            min_value=sessions_df["date"].min().date(),
            max_value=sessions_df["date"].max().date()
        )

    with col2:
        end_date = st.date_input(
            "End Date",
            value=sessions_df["date"].max().date(),
            min_value=sessions_df["date"].min().date(),
            max_value=sessions_df["date"].max().date()
        )

    mask = (sessions_df["date"].dt.date >= start_date) & \
           (sessions_df["date"].dt.date <= end_date)

    filtered_sessions = sessions_df[mask]
else:
    filtered_sessions = sessions_df

# ---------------------------------------------------------------------
# CALCULATE KPIs
# ---------------------------------------------------------------------
total_users = len(users_df)

active_users = filtered_sessions["user_id"].nunique()

user_session_counts = filtered_sessions.groupby("user_id").size()
multi_session_users = (user_session_counts > 1).sum()
multi_session_rate = (multi_session_users / active_users * 100) if active_users > 0 else 0

# -----------------------------------------
# PURCHASE KPIs (from user_lifetime_metrics.csv)
# -----------------------------------------
if user_metrics_df is not None and 'total_orders' in user_metrics_df.columns:
    purchasers = (user_metrics_df["total_orders"] >= 1).sum()
    purchasers_rate = purchasers / total_users * 100

    repeat_purchasers = (user_metrics_df["total_orders"] > 1).sum()
    repeat_purchase_rate = repeat_purchasers / total_users * 100
else:
    purchasers = repeat_purchasers = 0
    purchasers_rate = repeat_purchase_rate = 0


# ---------------------------------------------------------------------
# KPI ROW
# ---------------------------------------------------------------------
st.markdown("---")
st.markdown("### 📊 Key User KPIs")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("🟢 Active Users", f"{active_users:,}")

with col2:
    st.metric(
        "🔁 Multi-Session Users",
        f"{multi_session_users:,}",
        f"{multi_session_rate:.1f}% of active",
        help="Users who had more than one session in selected period"
    )

with col3:
    st.metric(
        "🛒 Purchasers (≥1 Order)",
        f"{purchasers:,}",
        f"{purchasers_rate:.1f}% of users"
    )

with col4:
    st.metric(
        "💳 Repeat Purchasers (>1 Order)",
        f"{repeat_purchasers:,}",
        f"{repeat_purchase_rate:.1f}%",
        help="True loyalty indicator"
    )

# ---------------------------------------------------------------------
# USER FUNNEL (FIXED)
# ---------------------------------------------------------------------
st.markdown("---")
st.markdown("### 🔽 User Engagement & Purchase Funnel")

funnel_labels = [
    "Total Users",
    "Active Users",
    "Multi-Session Users",
    "Purchasers (≥1 Order)",
    "Repeat Purchasers (>1 Order)"
]

funnel_values = [
    total_users,
    active_users,
    multi_session_users,
    purchasers,
    repeat_purchasers
]

fig_funnel = go.Figure(go.Funnel(
    y=funnel_labels,
    x=funnel_values,
    textinfo="value+percent initial"
))
fig_funnel.update_layout(height=400)
st.plotly_chart(fig_funnel, use_container_width=True)

# ---------------------------------------------------------------------
# PIE CHART: NEW vs MULTI-SESSION
# ---------------------------------------------------------------------
new_users = active_users - multi_session_users

pie_df = pd.DataFrame({
    "Type": ["New Users (Single Session)", "Multi-Session Users"],
    "Count": [new_users, multi_session_users]
})

fig_pie = px.pie(
    pie_df,
    values="Count",
    names="Type",
    title="User Visit Frequency Breakdown",
    hole=0.45
)

st.plotly_chart(fig_pie, use_container_width=True)

# ---------------------------------------------------------------------
# DAILY ACTIVE USERS TREND
# ---------------------------------------------------------------------
if "date" in filtered_sessions.columns:
    st.markdown("---")
    st.markdown("### 📈 Daily Active Users")

    dau = (
        filtered_sessions.groupby("date")["user_id"]
        .nunique()
        .reset_index()
        .rename(columns={"user_id": "Active Users"})
    )

    fig_trend = px.line(
        dau,
        x="date",
        y="Active Users",
        markers=True,
        title="Daily Active Users Trend"
    )
    st.plotly_chart(fig_trend, use_container_width=True)

# ---------------------------------------------------------------------
# USER LIFETIME METRICS
# ---------------------------------------------------------------------
if user_metrics_df is not None:
    st.markdown("---")
    st.markdown("### 💎 User Lifetime Metrics")

    col1, col2 = st.columns(2)

    with col1:
        fig_hist = px.histogram(
            user_metrics_df,
            x="total_revenue",
            nbins=40,
            title="Total Revenue Distribution per User"
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    with col2:
        fig_orders = px.histogram(
            user_metrics_df,
            x="total_orders",
            nbins=20,
            title="Order Count Distribution per User"
        )
        st.plotly_chart(fig_orders, use_container_width=True)

# ---------------------------------------------------------------------
# INSIGHTS
# ---------------------------------------------------------------------
st.markdown("---")
st.markdown("### 💡 Insights Summary")

col1, col2 = st.columns(2)

with col1:
    st.info(f"""
    **User Engagement**
    - {active_users:,} active users in selected period  
    - {multi_session_rate:.1f}% returned within period  
    """)

with col2:
    st.success(f"""
    **Purchase Behavior**
    - {purchasers:,} purchasers (≥1 order)  
    - {repeat_purchasers:,} repeat purchasers  
    - Repeat Purchase Rate: **{repeat_purchase_rate:.1f}%**  
    """)

# ---------------------------------------------------------------------
# DATA LIMITATION NOTE
# ---------------------------------------------------------------------
st.warning("""
⚠️ **Note on Data Coverage:**  
Your dataset contains only *one year of data (Jan–Dec)*.  
Therefore:
- “Multi-Session Users” is *not* a true returning-user metric.
- Users who were active in previous years will appear as new unless present in this year.
""")

# FOOTER
st.markdown("---")
st.markdown("<div style='text-align: center; color: gray;'>User Analytics Dashboard</div>", unsafe_allow_html=True)
