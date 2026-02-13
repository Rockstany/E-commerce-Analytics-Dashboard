import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Executive Dashboard", page_icon="📊", layout="wide")

st.title("📊 Executive Dashboard")
st.markdown("High-level business metrics and trends")

# Load data
@st.cache_data
def load_data():
    return pd.read_csv('data/daily_business_metrics.csv')

df = load_data()
df['date'] = pd.to_datetime(df['date'])

# Add your charts and metrics here
# (Similar structure to app.py)