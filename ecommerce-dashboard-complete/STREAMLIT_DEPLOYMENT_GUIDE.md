# Streamlit Deployment Guide - E-commerce Analytics Dashboard

## 📋 Overview

This guide shows you how to:
1. Create interactive dashboards with Streamlit
2. Push your code to GitHub
3. Deploy to Streamlit Cloud (free hosting)
4. Connect to your data

---

## 🎯 What You'll Build

A web-based analytics dashboard that:
- Loads your aggregated CSV files
- Displays interactive charts and metrics
- Updates automatically when you push changes to GitHub
- Is accessible from any browser at a public URL

---

## 📁 File Structure for Streamlit

```
your-project/
├── .streamlit/                    # Streamlit configuration
│   └── config.toml
├── data/                          # Your data files
│   ├── daily_business_metrics.csv
│   ├── session_attribution.csv
│   ├── session_funnel.csv
│   ├── product_performance_daily.csv
│   ├── user_lifetime_metrics.csv
│   ├── page_engagement_metrics.csv
│   └── coupon_performance.csv
├── pages/                         # Multi-page dashboard
│   ├── 1_📊_Executive_Dashboard.py
│   ├── 2_🎯_Marketing_Attribution.py
│   ├── 3_🛒_Conversion_Funnel.py
│   ├── 4_📦_Product_Performance.py
│   ├── 5_👤_Customer_Segmentation.py
│   └── 6_💰_Discount_Analysis.py
├── app.py                         # Main Streamlit app (homepage)
├── requirements.txt               # Python dependencies
├── .gitignore                     # Files to exclude from GitHub
└── README.md                      # Project description
```

---

## 🚀 Step-by-Step Setup

### STEP 1: Install Streamlit Locally

```bash
# Install Streamlit
pip install streamlit

# Install other required libraries
pip install pandas plotly altair
```

---

### STEP 2: Create Main Dashboard (app.py)

This will be your homepage when users visit your dashboard.

**File: `app.py`**
```python
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
```

---

### STEP 3: Create Additional Dashboard Pages

Create a `pages/` folder and add individual dashboard pages.

**File: `pages/1_📊_Executive_Dashboard.py`**
```python
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
```

**File: `pages/2_🎯_Marketing_Attribution.py`**
```python
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
```

**File: `pages/3_🛒_Conversion_Funnel.py`**
```python
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
```

Continue creating pages for other dashboards...

---

### STEP 4: Create requirements.txt

**File: `requirements.txt`**
```
streamlit>=1.28.0
pandas>=2.0.0
plotly>=5.17.0
altair>=5.1.0
numpy>=1.24.0
```

---

### STEP 5: Create .gitignore

**File: `.gitignore`**
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
*.egg-info/
.eggs/

# Streamlit
.streamlit/secrets.toml

# Data (if large files)
# Uncomment if you don't want to commit data files
# data/*.csv

# Logs
logs/
*.log

# OS
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/
*.swp
*.swo
```

---

### STEP 6: Create Streamlit Config

**File: `.streamlit/config.toml`**
```toml
[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[server]
headless = true
port = 8501
enableCORS = false
```

---

## 📤 Deploying to GitHub

### STEP 1: Initialize Git Repository

```bash
# Navigate to your project folder
cd your-project

# Initialize git
git init

# Add all files
git add .

# First commit
git commit -m "Initial commit - E-commerce Analytics Dashboard"
```

---

### STEP 2: Create GitHub Repository

1. Go to https://github.com
2. Click **"New Repository"** (green button)
3. Name it: `ecommerce-analytics-dashboard`
4. **Don't** initialize with README (you already have one)
5. Click **"Create Repository"**

---

### STEP 3: Push to GitHub

GitHub will show you commands. Run these:

```bash
# Add GitHub as remote
git remote add origin https://github.com/YOUR_USERNAME/ecommerce-analytics-dashboard.git

# Push to GitHub
git branch -M main
git push -u origin main
```

---

## ☁️ Deploy to Streamlit Cloud

### STEP 1: Go to Streamlit Cloud

1. Visit: https://share.streamlit.io/
2. Click **"Sign in"** (use your GitHub account)
3. Authorize Streamlit to access your GitHub

---

### STEP 2: Deploy Your App

1. Click **"New app"**
2. Select:
   - **Repository:** `your-username/ecommerce-analytics-dashboard`
   - **Branch:** `main`
   - **Main file path:** `app.py`
3. Click **"Deploy!"**

⏱️ Deployment takes 2-3 minutes...

---

### STEP 3: Your Dashboard is LIVE! 🎉

Streamlit will give you a URL like:
```
https://your-username-ecommerce-analytics-dashboard.streamlit.app
```

Share this URL with anyone! No server setup needed.

---

## 🔄 Updating Your Dashboard

### To Update Data or Code:

```bash
# 1. Make your changes locally
# 2. Test locally:
streamlit run app.py

# 3. Commit changes
git add .
git commit -m "Updated dashboard with new features"

# 4. Push to GitHub
git push

# 5. Streamlit Cloud automatically redeploys! ✨
```

---

## 💾 Data Management Strategies

### Strategy 1: Store Data in GitHub (Simple)

**Good for:**
- Small datasets (<100MB)
- Static data that doesn't change often

**How:**
- Put CSV files in `data/` folder
- Commit to GitHub
- Streamlit reads directly from `data/` folder

**Limitations:**
- GitHub has 100MB file size limit
- Every data update requires git commit

---

### Strategy 2: Google Sheets Integration (Dynamic)

**Good for:**
- Data that updates frequently
- Collaborative data entry
- Medium-sized datasets

**Setup:**

1. Upload CSVs to Google Sheets
2. Share sheets (Anyone with link can view)
3. Modify your Streamlit code:

```python
import pandas as pd

@st.cache_data(ttl=600)  # Cache for 10 minutes
def load_data_from_sheets(sheet_url):
    """Load data from Google Sheets"""
    # Convert share URL to CSV export URL
    csv_url = sheet_url.replace('/edit#gid=', '/export?format=csv&gid=')
    df = pd.read_csv(csv_url)
    return df

# Use it
sheet_url = 'https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit#gid=0'
df = load_data_from_sheets(sheet_url)
```

---

### Strategy 3: Cloud Storage (AWS S3, Google Cloud Storage)

**Good for:**
- Large datasets (>100MB)
- Automated data pipelines
- Production environments

**Example with AWS S3:**

1. Install boto3: Add `boto3` to `requirements.txt`
2. Store AWS credentials in Streamlit Secrets
3. Load data:

```python
import boto3
import pandas as pd
from io import StringIO

@st.cache_data
def load_from_s3(bucket, key):
    s3 = boto3.client(
        's3',
        aws_access_key_id=st.secrets["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=st.secrets["AWS_SECRET_ACCESS_KEY"]
    )
    obj = s3.get_object(Bucket=bucket, Key=key)
    df = pd.read_csv(obj['Body'])
    return df

df = load_from_s3('my-bucket', 'data/daily_metrics.csv')
```

**Add secrets in Streamlit Cloud:**
- Go to app settings
- Click "Secrets"
- Add:
```toml
AWS_ACCESS_KEY_ID = "your_key"
AWS_SECRET_ACCESS_KEY = "your_secret"
```

---

### Strategy 4: Database Connection (PostgreSQL, MySQL)

**Good for:**
- Very large datasets
- Real-time data
- Multiple apps using same data

**Example with PostgreSQL:**

1. Add to `requirements.txt`: `psycopg2-binary`
2. Store credentials in Streamlit Secrets:

```toml
# .streamlit/secrets.toml
[postgres]
host = "your-db-host.com"
port = 5432
database = "ecommerce"
user = "your_user"
password = "your_password"
```

3. Connect and query:

```python
import streamlit as st
import pandas as pd
import psycopg2

@st.cache_resource
def init_connection():
    return psycopg2.connect(**st.secrets["postgres"])

@st.cache_data
def load_data(query):
    conn = init_connection()
    df = pd.read_sql_query(query, conn)
    return df

df = load_data("SELECT * FROM daily_business_metrics")
```

---

## 🎨 Customization Tips

### Custom Styling

Add custom CSS in your Streamlit app:

```python
st.markdown("""
    <style>
    /* Main background */
    .stApp {
        background-color: #f5f5f5;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background-color: #1e1e1e;
    }
    
    /* Metrics */
    div[data-testid="stMetricValue"] {
        font-size: 28px;
        color: #1f77b4;
    }
    
    /* Headers */
    h1 {
        color: #2c3e50;
        font-weight: 700;
    }
    </style>
""", unsafe_allow_html=True)
```

---

### Add Logo and Favicon

```python
st.set_page_config(
    page_title="Your Company",
    page_icon="🏢",  # Or path to .png file
    layout="wide"
)

# Sidebar logo
with st.sidebar:
    st.image("logo.png", width=200)
```

---

### Interactive Filters

```python
# Multi-select filter
selected_countries = st.multiselect(
    "Select Countries",
    options=df['country'].unique(),
    default=df['country'].unique()
)

filtered_df = df[df['country'].isin(selected_countries)]

# Date range slider
date_range = st.slider(
    "Select Date Range",
    min_value=df['date'].min(),
    max_value=df['date'].max(),
    value=(df['date'].min(), df['date'].max())
)
```

---

## 🐛 Common Issues & Solutions

### Issue 1: "FileNotFoundError: data/file.csv"

**Solution:**
```python
import os

# Check if file exists
if os.path.exists('data/daily_business_metrics.csv'):
    df = pd.read_csv('data/daily_business_metrics.csv')
else:
    st.error("Data file not found. Please upload data files.")
```

---

### Issue 2: App is Slow

**Solutions:**
1. Use `@st.cache_data` decorator
2. Filter data before charting
3. Limit rows displayed: `df.head(1000)`
4. Use `st.spinner()` for long operations

```python
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_data():
    return pd.read_csv('data/file.csv')

with st.spinner('Loading data...'):
    df = load_data()
```

---

### Issue 3: Charts Not Displaying

**Solution:** Make sure Plotly is installed
```bash
pip install plotly
```

And use `st.plotly_chart()`:
```python
import plotly.express as px

fig = px.line(df, x='date', y='revenue')
st.plotly_chart(fig, use_container_width=True)
```

---

### Issue 4: Deployment Failed

**Check:**
1. `requirements.txt` includes all packages
2. No syntax errors: Run `streamlit run app.py` locally first
3. File paths are correct (case-sensitive on Linux)
4. GitHub repo is public (or Streamlit has access)

---

## 📊 Dashboard Examples

### Example 1: KPI Cards

```python
col1, col2, col3, col4 = st.columns(4)

col1.metric(
    label="📈 Revenue",
    value="$123,456",
    delta="+12.3%",
    delta_color="normal"
)

col2.metric("🛒 Orders", "1,234", "+5.2%")
col3.metric("👥 Customers", "890", "-2.1%", delta_color="inverse")
col4.metric("💰 AOV", "$100.23", "+8.4%")
```

---

### Example 2: Interactive Charts

```python
import plotly.express as px

# Line chart
fig = px.line(
    df, 
    x='date', 
    y='revenue',
    title='Revenue Trend',
    markers=True
)
fig.update_layout(
    hovermode='x unified',
    xaxis_title='Date',
    yaxis_title='Revenue ($)'
)
st.plotly_chart(fig, use_container_width=True)

# Bar chart
fig2 = px.bar(
    df, 
    x='product_name', 
    y='quantity_sold',
    color='category',
    title='Top Products'
)
st.plotly_chart(fig2, use_container_width=True)
```

---

### Example 3: Data Tables with Search

```python
# Search box
search = st.text_input("🔍 Search products", "")

# Filter dataframe
if search:
    filtered = df[df['product_name'].str.contains(search, case=False)]
else:
    filtered = df

# Display with formatting
st.dataframe(
    filtered.style.format({
        'revenue': '${:,.2f}',
        'quantity': '{:,.0f}'
    }),
    use_container_width=True,
    height=400
)
```

---

## 🔐 Security Best Practices

### 1. Never Commit Secrets

Add to `.gitignore`:
```
.streamlit/secrets.toml
```

Use Streamlit Cloud secrets instead.

---

### 2. Environment Variables

For sensitive data:
```python
import os

API_KEY = os.environ.get('API_KEY') or st.secrets.get('API_KEY')
```

---

### 3. Data Access Control

If using authentication:
```python
import streamlit_authenticator as stauth

# Create authenticator
authenticator = stauth.Authenticate(
    credentials,
    'cookie_name',
    'signature_key',
    cookie_expiry_days=30
)

# Login
name, authentication_status, username = authenticator.login('Login', 'main')

if authentication_status:
    st.write(f'Welcome *{name}*')
    # Show dashboard
elif authentication_status == False:
    st.error('Username/password is incorrect')
```

---

## 📚 Additional Resources

### Streamlit Documentation
- Main docs: https://docs.streamlit.io
- Gallery: https://streamlit.io/gallery
- Forum: https://discuss.streamlit.io

### Deployment Help
- Streamlit Cloud: https://docs.streamlit.io/streamlit-community-cloud
- GitHub basics: https://docs.github.com/en/get-started

### Chart Libraries
- Plotly: https://plotly.com/python/
- Altair: https://altair-viz.github.io/
- Matplotlib: https://matplotlib.org/

---

## ✅ Deployment Checklist

- [ ] Created `app.py` with main dashboard
- [ ] Created additional pages in `pages/` folder
- [ ] Created `requirements.txt` with all dependencies
- [ ] Created `.gitignore` file
- [ ] Tested locally: `streamlit run app.py`
- [ ] Created GitHub repository
- [ ] Pushed code to GitHub
- [ ] Deployed to Streamlit Cloud
- [ ] Verified app works at public URL
- [ ] Set up data update workflow

---

**Last Updated:** 2026-02-13  
**Streamlit Version:** 1.28+
