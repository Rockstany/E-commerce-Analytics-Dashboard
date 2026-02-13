import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Conversion Funnel", page_icon="🛒", layout="wide")

st.title("🛒 Conversion Funnel Analysis")

@st.cache_data
def load_data():
    return pd.read_csv('data/session_funnel.csv')

df = load_data()

# Calculate funnel metrics
total_sessions = len(df)
product_views = df['had_product_view'].sum()
cart_adds = df['had_add_to_cart'].sum()
orders = df['had_order'].sum()

# Create funnel chart
fig = go.Figure(go.Funnel(
    y=['Sessions', 'Product Views', 'Add to Cart', 'Orders'],
    x=[total_sessions, product_views, cart_adds, orders],
    textinfo="value+percent initial"
))

fig.update_layout(title="Conversion Funnel", height=500)
st.plotly_chart(fig, use_container_width=True)

# Metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Sessions", f"{total_sessions:,}")
with col2:
    st.metric("Product Views", f"{product_views:,}", 
              f"{product_views/total_sessions*100:.1f}%")
with col3:
    st.metric("Cart Adds", f"{cart_adds:,}", 
              f"{cart_adds/total_sessions*100:.1f}%")
with col4:
    st.metric("Orders", f"{orders:,}", 
              f"{orders/total_sessions*100:.1f}%")