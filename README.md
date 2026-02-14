# E-commerce Analytics Data Processing System

## 📖 What This Is

A complete Python-based system that transforms raw e-commerce tracking data into dashboard-ready analytics tables. Instead of querying millions of raw event records every time you need a metric, this system pre-calculates and stores aggregated summaries for lightning-fast dashboard loading.

**Speed Improvement:** 10-100x faster dashboard queries  
**Use Case:** E-commerce analytics, marketing attribution, customer segmentation

---

## 📁 Files in This Package

| File | Purpose | When to Use |
|------|---------|-------------|
| `ecommerce_data_processor.py` | Main processing script | Run daily to create aggregated tables |
| `generate_sample_data.py` | Sample data generator | Testing and learning |
| `DATABASE_DESIGN_DOCUMENTATION.md` | Complete technical documentation | Understanding data structure |
| `QUICK_REFERENCE.md` | Quick modification guide | Making changes |
| `README.md` | This file | Getting started |

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Install Python & Libraries
```bash
# Install Python from: https://www.python.org/downloads/
# Then install required libraries:
pip install pandas numpy
```

### Step 2: Generate Sample Data (for testing)
```bash
python generate_sample_data.py
```
This creates sample CSV files in `raw_data/` folder.

### Step 3: Run the Processing Script
```bash
python ecommerce_data_processor.py
```
This creates aggregated CSV files in `aggregated_data/` folder.

### Step 4: Check Results
Open `aggregated_data/` folder and you'll see 7 new CSV files ready for dashboards!

---

## 📊 What Gets Created

### Input (Raw Data)
8 CSV files tracking every user action:
- `user_table.csv` - Customer profiles
- `session_table.csv` - Website visits
- `order_table.csv` - Purchases
- `order_line_item_table.csv` - Product details
- `add_to_cart_table.csv` - Cart additions
- `pageview_table.csv` - Page views
- `scroll_table.csv` - Scroll events
- `click_table.csv` - Click events

### Output (Aggregated Data)
7 pre-calculated summary tables:

| Table | What It Contains | Use For |
|-------|-----------------|---------|
| `daily_business_metrics.csv` | Daily revenue, orders, conversion rate | Executive dashboard |
| `session_attribution.csv` | Marketing source + conversion outcome | Marketing ROI |
| `session_funnel.csv` | User journey through purchase funnel | Conversion optimization |
| `product_performance_daily.csv` | Sales by product | Product analytics |
| `user_lifetime_metrics.csv` | Customer LTV and RFM segments | Customer segmentation |
| `page_engagement_metrics.csv` | Page views, scroll depth, clicks | UX optimization |
| `coupon_performance.csv` | Discount code effectiveness | Promotion analysis |

---

## 🎯 Common Use Cases

### Use Case 1: Executive Dashboard
**Goal:** Show daily revenue, orders, conversion rate  
**Solution:** Use `daily_business_metrics.csv`  
**Dashboard loads in:** <1 second instead of 10+ seconds

### Use Case 2: Marketing Attribution
**Goal:** Which campaigns drive the most revenue?  
**Solution:** Use `session_attribution.csv`  
**Query:** `SELECT utm_campaign, SUM(revenue) FROM session_attribution GROUP BY utm_campaign`

### Use Case 3: Customer Segmentation
**Goal:** Identify VIP customers for retention campaign  
**Solution:** Use `user_lifetime_metrics.csv`  
**Filter:** `SELECT * FROM user_lifetime_metrics WHERE rfm_segment = 'Champion'`

### Use Case 4: Product Performance
**Goal:** Which products are added to cart but not purchased?  
**Solution:** Use `product_performance_daily.csv`  
**Metric:** Low `cart_to_purchase_rate` indicates abandonment

---

## 🔧 Customization Guide

### Adding a New Metric

**Example: Add "Mobile Revenue" to daily metrics**

1. Open `ecommerce_data_processor.py`
2. Find function `create_daily_business_metrics()`
3. Add this code:
```python
# Calculate mobile revenue
mobile_sessions = sessions_df[sessions_df['platform'] == 'mobile']['session_id']
mobile_orders = orders_df[orders_df['session_id'].isin(mobile_sessions)]
metrics['mobile_revenue'] = mobile_orders.groupby('date')['total_price'].sum()
```
4. Save and re-run script
5. New column appears in `daily_business_metrics.csv`!

**More examples:** See `QUICK_REFERENCE.md`

---

## 📅 Automation (Run Daily)

### Why Automate?
Run this script every night at 1 AM so dashboards always show fresh data.

### Windows (Task Scheduler)
1. Open Task Scheduler
2. Create Basic Task → Daily at 1:00 AM
3. Action: `python C:\path\to\ecommerce_data_processor.py`

### Mac/Linux (Cron)
```bash
crontab -e
# Add this line:
0 1 * * * /usr/bin/python3 /path/to/ecommerce_data_processor.py
```

---

## 📈 Dashboard Integration

### Connecting to Dashboards

**Tableau:**
1. Data → New Data Source → Text File
2. Select file from `aggregated_data/`
3. Create visualizations

**Power BI:**
1. Get Data → Text/CSV
2. Select file from `aggregated_data/`
3. Transform if needed → Load

**Excel:**
1. Data → From Text/CSV
2. Select file from `aggregated_data/`
3. Create pivot tables

**Python/Jupyter:**
```python
import pandas as pd
df = pd.read_csv('aggregated_data/daily_business_metrics.csv')
df.plot(x='date', y='total_revenue')
```

---

## 🧪 Testing Your Changes

### Test with Sample Data
```bash
# Generate fresh sample data
python generate_sample_data.py

# Process it
python ecommerce_data_processor.py

# Check results
ls aggregated_data/
```

### Verify Output
```python
# Quick verification script
import pandas as pd

# Load and inspect
df = pd.read_csv('aggregated_data/daily_business_metrics.csv')
print(df.head())
print(f"Total Revenue: ${df['total_revenue'].sum():,.2f}")
print(f"Date Range: {df['date'].min()} to {df['date'].max()}")
```

---

## 🐛 Troubleshooting

### Problem: "ModuleNotFoundError: No module named 'pandas'"
**Solution:**
```bash
pip install pandas numpy
```

### Problem: "FileNotFoundError: user_table.csv"
**Solution:** Make sure CSV files are in `raw_data/` folder with exact names.

### Problem: Empty output files
**Solution:**
1. Check `logs/aggregation_log.txt` for errors
2. Verify raw CSV files have data
3. Check date columns are formatted: `YYYY-MM-DD HH:MM:SS`

### Problem: Numbers look wrong
**Solution:**
1. Verify raw data quality (no duplicates, valid dates)
2. Check for NULL values in key columns (user_id, session_id, order_id)
3. Run on one day of data to debug

**More help:** See troubleshooting section in `QUICK_REFERENCE.md`

---

## 📚 Documentation Map

| Document | Best For |
|----------|----------|
| `README.md` (this file) | Getting started, overview |
| `QUICK_REFERENCE.md` | Quick modifications, common tasks |
| `DATABASE_DESIGN_DOCUMENTATION.md` | Understanding structure, adding fields |

### Reading Order
1. **New users:** Start here (README.md) → Run sample data → Explore outputs
2. **Making changes:** QUICK_REFERENCE.md
3. **Deep understanding:** DATABASE_DESIGN_DOCUMENTATION.md

---

## 🎓 Learning Path

### Beginner
1. Run sample data generator
2. Run processing script
3. Open output CSVs in Excel
4. Understand what each table shows

### Intermediate
1. Add one new metric to existing table
2. Modify date range
3. Add filtering conditions
4. Connect to dashboard tool

### Advanced
1. Create entirely new aggregated table
2. Implement incremental updates (only new data)
3. Add data quality checks
4. Optimize for large datasets (millions of rows)

---

## 💡 Key Concepts

### Aggregation = Pre-Calculation
Instead of calculating "sum of revenue" every time dashboard loads, we calculate it once per day and save it. Dashboard reads pre-calculated result → 100x faster.

### Raw vs Aggregated
- **Raw:** Millions of individual events (every click, view, purchase)
- **Aggregated:** Thousands of summaries (daily totals, user summaries)

### GROUP BY = Summarization
- `groupby('date')` → One row per day
- `groupby(['date', 'product'])` → One row per product per day
- `groupby('user_id')` → One row per user

---

## 🔐 Data Privacy & Security

### What to Be Careful With
- User IDs should be anonymized hashes, not emails
- IP addresses should be stored securely
- PII (Personally Identifiable Information) should be encrypted

### Best Practices
1. Don't include email addresses or names in raw data
2. Hash user IDs before processing
3. Secure the `raw_data/` folder with appropriate permissions
4. Delete old raw data after aggregation (keep aggregated only)

---

## 📊 Performance Guidelines

### Small Dataset (<100K rows)
- Runs in seconds
- No optimization needed

### Medium Dataset (100K-1M rows)
- Runs in minutes
- Consider date filtering
- Use incremental updates

### Large Dataset (>1M rows)
- Runs in 10+ minutes
- Use database instead of CSVs
- Implement parallel processing
- Consider Apache Spark for very large data

---

## 🔄 Incremental Updates

By default, script processes ALL data. For large datasets, process only new data:

```python
# In ecommerce_data_processor.py, modify:
class Config:
    # Only process yesterday
    START_DATE = datetime.now() - timedelta(days=1)
    END_DATE = datetime.now()
```

Then APPEND to existing aggregated files instead of overwriting.

---

## 🤝 Contributing

### Adding Features
1. Make a backup copy first
2. Test with sample data
3. Document your changes
4. Update this README if major changes

### Reporting Issues
1. Check `logs/aggregation_log.txt` first
2. Verify sample data works
3. Isolate the problem (which function?)
4. Document steps to reproduce

---

## 📝 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-13 | Initial release with 7 aggregation functions |

---

## 📞 Getting Help

### Resources
1. **Logs:** Check `logs/aggregation_log.txt` for detailed errors
2. **Documentation:** Read the full docs in `DATABASE_DESIGN_DOCUMENTATION.md`
3. **Examples:** See `QUICK_REFERENCE.md` for modification examples

### Learning Resources
- Pandas documentation: https://pandas.pydata.org/docs/
- Python datetime: https://docs.python.org/3/library/datetime.html
- SQL concepts (help with grouping): https://www.w3schools.com/sql/

---

## ⚖️ License

This is a template/framework for your use. Modify freely for your needs.

---

## 🎉 Success Checklist

- [ ] Installed Python and libraries
- [ ] Generated sample data successfully
- [ ] Ran processing script without errors
- [ ] Opened output CSV files
- [ ] Understood what each aggregated table contains
- [ ] Connected one table to a dashboard
- [ ] Made first custom modification
- [ ] Set up daily automation

**If you've checked all boxes, you're ready to process real data!**

---

**Created:** 2026-02-13  
**Last Updated:** 2026-02-13  
**Version:** 1.0
