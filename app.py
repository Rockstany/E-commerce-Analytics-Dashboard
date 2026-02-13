import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# PAGE CONFIG - Must be first Streamlit command
st.set_page_config(
    page_title="E-commerce Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CUSTOM CSS for better styling
st.markdown("""
    <style>
    .main {padding: 0rem 1rem;}
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# TITLE
st.title("🛍️ E-commerce Analytics Dashboard")
st.markdown("### Real-time insights into your business performance")

# SIDEBAR
with st.sidebar:
    st.image("https://via.placeholder.com/150x50?text=Your+Logo", width=150)
    st.markdown("---")
    st.markdown("### 📌 Navigation")
    st.info("Use the pages menu above to explore different dashboards")
    
    st.markdown("---")
    st.markdown("### 🔄 Last Updated")
    st.text(datetime.now().strftime("%Y-%m-%d %H:%M"))

# LOAD DATA
@st.cache_data  # Cache data for faster reloads
def load_data(filename):
    """Load CSV file with caching"""
    try:
        df = pd.read_csv(f'data/{filename}')
        return df
    except FileNotFoundError:
        st.error(f"❌ File not found: data/{filename}")
        return None

# Load daily metrics
daily_metrics = load_data('daily_business_metrics.csv')

if daily_metrics is not None:
    # Convert date column to datetime
    daily_metrics['date'] = pd.to_datetime(daily_metrics['date'])
    
    # DATE FILTER
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "Start Date",
            value=daily_metrics['date'].max() - timedelta(days=30),
            min_value=daily_metrics['date'].min(),
            max_value=daily_metrics['date'].max()
        )
    with col2:
        end_date = st.date_input(
            "End Date",
            value=daily_metrics['date'].max(),
            min_value=daily_metrics['date'].min(),
            max_value=daily_metrics['date'].max()
        )
    
    # Filter data by date range
    mask = (daily_metrics['date'] >= pd.to_datetime(start_date)) & \
           (daily_metrics['date'] <= pd.to_datetime(end_date))
    filtered_data = daily_metrics[mask]
    
    # KEY METRICS ROW
    st.markdown("---")
    st.markdown("### 📈 Key Performance Indicators")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_revenue = filtered_data['total_revenue'].sum()
        st.metric(
            label="💰 Total Revenue",
            value=f"${total_revenue:,.0f}",
            delta=f"{filtered_data['total_revenue'].pct_change().iloc[-1]*100:.1f}%"
        )
    
    with col2:
        total_orders = filtered_data['total_orders'].sum()
        st.metric(
            label="🛒 Total Orders",
            value=f"{total_orders:,.0f}",
            delta=f"{filtered_data['total_orders'].pct_change().iloc[-1]*100:.1f}%"
        )
    
    with col3:
        avg_conversion = filtered_data['conversion_rate'].mean()
        st.metric(
            label="📊 Conversion Rate",
            value=f"{avg_conversion:.2f}%",
            delta=f"{filtered_data['conversion_rate'].diff().iloc[-1]:.2f}%"
        )
    
    with col4:
        avg_aov = filtered_data['avg_order_value'].mean()
        st.metric(
            label="💳 Avg Order Value",
            value=f"${avg_aov:.2f}",
            delta=f"{filtered_data['avg_order_value'].pct_change().iloc[-1]*100:.1f}%"
        )
    
    # CHARTS
    st.markdown("---")
    
    # Revenue Trend Chart
    st.markdown("### 📈 Revenue Trend")
    fig_revenue = px.line(
        filtered_data,
        x='date',
        y='total_revenue',
        title='Daily Revenue Over Time',
        labels={'total_revenue': 'Revenue ($)', 'date': 'Date'}
    )
    fig_revenue.update_traces(line_color='#1f77b4', line_width=3)
    fig_revenue.update_layout(hovermode='x unified')
    st.plotly_chart(fig_revenue, use_container_width=True)
    
    # Two column charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🛒 Orders vs Sessions")
        fig_funnel = px.bar(
            filtered_data,
            x='date',
            y=['total_sessions', 'total_orders'],
            title='Sessions vs Orders',
            labels={'value': 'Count', 'variable': 'Metric'}
        )
        st.plotly_chart(fig_funnel, use_container_width=True)
    
    with col2:
        st.markdown("### 👥 New vs Repeat Customers")
        if 'new_customers' in filtered_data.columns:
            fig_customers = px.area(
                filtered_data,
                x='date',
                y=['new_customers', 'repeat_customers'],
                title='Customer Type Distribution',
                labels={'value': 'Customers', 'variable': 'Type'}
            )
            st.plotly_chart(fig_customers, use_container_width=True)
    
    # DATA TABLE
    st.markdown("---")
    st.markdown("### 📋 Raw Data")
    st.dataframe(
        filtered_data.sort_values('date', ascending=False),
        use_container_width=True,
        hide_index=True
    )
    
    # DOWNLOAD BUTTON
    csv = filtered_data.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Data as CSV",
        data=csv,
        file_name=f'business_metrics_{start_date}_{end_date}.csv',
        mime='text/csv',
    )

else:
    st.error("❌ Unable to load data. Please check if files exist in the 'data/' folder.")
    st.info("💡 Make sure you've run the data processing script first!")

# FOOTER
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: gray;'>
        <p>E-commerce Analytics Dashboard | Built with Streamlit</p>
    </div>
""", unsafe_allow_html=True)