import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Marketing Attribution", page_icon="🎯", layout="wide")

st.title("🎯 Marketing Attribution")
st.markdown("Analyze which marketing channels drive conversions")

@st.cache_data
def load_data():
    return pd.read_csv('data/session_attribution.csv')

df = load_data()

# Group by UTM source
if 'utm_source' in df.columns:
    channel_performance = df.groupby('utm_source').agg({
        'session_id': 'count',
        'converted': 'sum',
        'revenue': 'sum'
    }).reset_index()
    
    channel_performance.columns = ['Channel', 'Sessions', 'Conversions', 'Revenue']
    channel_performance['Conversion Rate'] = (
        channel_performance['Conversions'] / channel_performance['Sessions'] * 100
    ).round(2)
    
    # Display metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Sessions", f"{channel_performance['Sessions'].sum():,.0f}")
    with col2:
        st.metric("Total Conversions", f"{channel_performance['Conversions'].sum():,.0f}")
    with col3:
        st.metric("Total Revenue", f"${channel_performance['Revenue'].sum():,.2f}")
    
    # Chart
    st.markdown("### Revenue by Channel")
    fig = px.bar(
        channel_performance.sort_values('Revenue', ascending=False),
        x='Channel',
        y='Revenue',
        title='Revenue by Marketing Channel'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Table
    st.markdown("### Channel Performance Details")
    st.dataframe(channel_performance, use_container_width=True, hide_index=True)