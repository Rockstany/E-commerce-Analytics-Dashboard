# 🛍️ E-commerce Analytics Dashboard

A powerful, interactive analytics dashboard for e-commerce businesses built with Streamlit.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-url.streamlit.app)

## 🌟 Features

- **📊 Executive Dashboard** - High-level KPIs and business metrics
- **🎯 Marketing Attribution** - Track which campaigns drive revenue
- **🛒 Conversion Funnel** - Identify where customers drop off
- **📦 Product Performance** - Analyze top-selling products
- **👤 Customer Segmentation** - RFM analysis and customer segments
- **💰 Discount Analysis** - Measure coupon effectiveness

## 🚀 Quick Start

### Run Locally

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/ecommerce-analytics-dashboard.git
cd ecommerce-analytics-dashboard

# Install dependencies
pip install -r requirements.txt

# Generate sample data (for testing)
python generate_sample_data.py

# Run dashboard
streamlit run app.py
```

Dashboard will open at: http://localhost:8501

### Deploy to Streamlit Cloud

1. Fork this repository
2. Go to [share.streamlit.io](https://share.streamlit.io/)
3. Click "New app"
4. Select your repository
5. Set main file to `app.py`
6. Click "Deploy"

## 📁 Project Structure

```
.
├── app.py                          # Main dashboard homepage
├── pages/                          # Additional dashboard pages
│   ├── 1_📊_Executive_Dashboard.py
│   ├── 2_🎯_Marketing_Attribution.py
│   ├── 3_🛒_Conversion_Funnel.py
│   ├── 4_📦_Product_Performance.py
│   ├── 5_👤_Customer_Segmentation.py
│   └── 6_💰_Discount_Analysis.py
├── data/                           # CSV data files
│   ├── daily_business_metrics.csv
│   ├── session_attribution.csv
│   └── ...
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

## 📊 Data Requirements

The dashboard expects CSV files in the `data/` folder:

- `daily_business_metrics.csv` - Daily revenue, orders, conversion rates
- `session_attribution.csv` - Session-level marketing attribution
- `session_funnel.csv` - Conversion funnel data
- `product_performance_daily.csv` - Product sales metrics
- `user_lifetime_metrics.csv` - Customer lifetime value and RFM segments
- `page_engagement_metrics.csv` - Page-level engagement data
- `coupon_performance.csv` - Discount code performance

### Generate Sample Data

To test the dashboard with sample data:

```bash
python generate_sample_data.py
python ecommerce_data_processor.py
```

### Use Your Own Data

1. Process your raw data using `ecommerce_data_processor.py`
2. Place resulting CSV files in the `data/` folder
3. Run the dashboard

## 🎨 Customization

### Update Branding

Edit `app.py` and modify:
- Logo in sidebar
- Color scheme in CSS
- Page title and icon

### Add New Metrics

1. Modify aggregation functions in `ecommerce_data_processor.py`
2. Update dashboard pages to display new metrics

### Change Data Source

Replace CSV loading with database connections:

```python
import psycopg2
import pandas as pd

@st.cache_resource
def init_connection():
    return psycopg2.connect(**st.secrets["postgres"])

@st.cache_data
def load_data(query):
    conn = init_connection()
    return pd.read_sql_query(query, conn)
```

## 🔒 Security

- Never commit sensitive data to GitHub
- Use Streamlit Secrets for API keys and credentials
- Add large data files to `.gitignore`

## 📚 Documentation

- [Streamlit Deployment Guide](STREAMLIT_DEPLOYMENT_GUIDE.md) - Complete deployment instructions
- [Database Design Documentation](DATABASE_DESIGN_DOCUMENTATION.md) - Data structure details
- [Quick Reference](QUICK_REFERENCE.md) - Common modifications

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Charts powered by [Plotly](https://plotly.com/)
- Data processing with [Pandas](https://pandas.pydata.org/)

## 📧 Contact

Your Name - [@yourtwitter](https://twitter.com/yourtwitter)

Project Link: [https://github.com/YOUR_USERNAME/ecommerce-analytics-dashboard](https://github.com/YOUR_USERNAME/ecommerce-analytics-dashboard)

---

**⭐ Star this repo if you find it useful!**
