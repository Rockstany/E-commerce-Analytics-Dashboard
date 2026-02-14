# Quick Reference Guide - How to Modify the System

## 📁 File Structure
```
/your_project/
├── raw_data/                          # Put your CSV files here
│   ├── user_table.csv
│   ├── session_table.csv
│   ├── order_table.csv
│   ├── order_line_item_table.csv
│   ├── add_to_cart_table.csv
│   ├── pageview_table.csv
│   ├── scroll_table.csv
│   └── click_table.csv
│
├── aggregated_data/                   # Script outputs CSVs here
│   ├── daily_business_metrics.csv
│   ├── session_attribution.csv
│   ├── session_funnel.csv
│   ├── product_performance_daily.csv
│   ├── user_lifetime_metrics.csv
│   ├── page_engagement_metrics.csv
│   └── coupon_performance.csv
│
├── logs/                              # Script logs here
│   └── aggregation_log.txt
│
├── ecommerce_data_processor.py        # Main script
├── DATABASE_DESIGN_DOCUMENTATION.md   # Full documentation
└── QUICK_REFERENCE.md                 # This file
```

---

## 🚀 How to Run

### First Time Setup
```bash
# 1. Install Python (if not already installed)
# Download from: https://www.python.org/downloads/

# 2. Install required libraries
pip install pandas numpy

# 3. Put your CSV files in raw_data/ folder

# 4. Run the script
python ecommerce_data_processor.py
```

### Output
After running, check `aggregated_data/` folder for 7 new CSV files.

---

## 🔧 Common Modifications

### 1. Add New Field to Existing Table

**Example: Add "Total Shipping Cost" to daily_business_metrics**

**Step 1:** Open `ecommerce_data_processor.py`

**Step 2:** Find the function `create_daily_business_metrics()`

**Step 3:** Add this code (around line 320):
```python
# NEW FIELD: Total Shipping Cost
log_message("  Calculating total shipping...")
metrics['total_shipping'] = orders_df.groupby('date')['shipping_price'].sum()
```

**Step 4:** Scroll down to where DataFrame is created (around line 370) and add field:
```python
result_df['total_shipping'] = result_df['total_shipping'].round(2)
```

**Step 5:** Save and re-run:
```bash
python ecommerce_data_processor.py
```

**Step 6:** Check `aggregated_data/daily_business_metrics.csv` - new column will be there!

---

### 2. Create Entirely New Aggregated Table

**Example: Create "hourly_traffic_metrics" table**

**Step 1:** Add new function (around line 900):
```python
def create_hourly_traffic_metrics(sessions_df):
    """
    Traffic metrics by hour of day
    """
    log_message("\n" + "="*60)
    log_message("CREATING: hourly_traffic_metrics")
    log_message("="*60)
    
    if sessions_df is None:
        return None
    
    # Extract hour from timestamp
    sessions_df['hour'] = sessions_df['time'].dt.hour
    sessions_df['date'] = sessions_df['time'].dt.date
    
    # Group by date and hour
    hourly_metrics = sessions_df.groupby(['date', 'hour']).agg({
        'session_id': 'nunique',
        'user_id': 'nunique'
    }).reset_index()
    
    hourly_metrics.columns = ['date', 'hour', 'sessions', 'users']
    
    log_message(f"✓ Created {len(hourly_metrics)} hourly records")
    return hourly_metrics
```

**Step 2:** Call it in `main()` function (around line 1050):
```python
# Table 8: Hourly Traffic
hourly_traffic = create_hourly_traffic_metrics(data['sessions'])
```

**Step 3:** Save it (around line 1100):
```python
save_to_csv(hourly_traffic, 'hourly_traffic_metrics.csv')
```

**Step 4:** Run script - new file appears!

---

### 3. Change Date Range to Process

**Step 1:** Open `ecommerce_data_processor.py`

**Step 2:** Find `class Config` (around line 40)

**Step 3:** Modify these lines:
```python
# Process only specific date range
START_DATE = datetime(2026, 2, 1)  # February 1, 2026
END_DATE = datetime(2026, 2, 13)   # February 13, 2026

# Or process everything
START_DATE = None
END_DATE = None
```

---

### 4. Add Filtering/Conditions

**Example: Only include orders over $50**

**Step 1:** In any aggregation function, add filter:
```python
# Before grouping, filter the data
orders_df = orders_df[orders_df['total_price'] > 50]
```

**Example: Exclude test users**
```python
# Remove test users
sessions_df = sessions_df[~sessions_df['user_id'].str.contains('test')]
```

---

## 📊 Dashboard Connection

### Which Aggregated Table to Use for Each Dashboard

| Dashboard | Use This File |
|-----------|--------------|
| Executive Overview | `daily_business_metrics.csv` |
| Marketing Attribution | `session_attribution.csv` |
| Conversion Funnel | `session_funnel.csv` |
| Product Performance | `product_performance_daily.csv` |
| Customer Segmentation | `user_lifetime_metrics.csv` |
| UX/Engagement | `page_engagement_metrics.csv` |
| Discount Analysis | `coupon_performance.csv` |

### How to Connect
1. In your dashboard tool (Tableau, Power BI, etc.)
2. Import CSV from `aggregated_data/` folder
3. Dashboard loads instantly because data is pre-calculated!

---

## ⚠️ Troubleshooting

### Problem: Script says "File not found"
**Solution:** Make sure CSV files are in `raw_data/` folder with exact names:
- `user_table.csv`
- `session_table.csv`
- etc.

### Problem: "KeyError: 'column_name'"
**Solution:** Your CSV is missing a required column. Check column names match exactly.

### Problem: Empty output files
**Solution:** 
1. Check `logs/aggregation_log.txt` for errors
2. Make sure raw CSV files have data
3. Check date range settings

### Problem: Numbers look wrong
**Solution:**
1. Verify raw data is correct
2. Check for NULL values in key fields
3. Run script with just one day of data to test

---

## 📅 Scheduling (Run Automatically)

### Windows (Task Scheduler)
1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Daily at 1:00 AM
4. Action: Start a program
5. Program: `python`
6. Arguments: `C:\path\to\ecommerce_data_processor.py`

### Mac/Linux (Cron)
```bash
# Open crontab
crontab -e

# Add this line (runs daily at 1 AM)
0 1 * * * /usr/bin/python3 /path/to/ecommerce_data_processor.py

# Save and exit
```

---

## 🎯 Common Use Cases

### Use Case 1: "I need to track mobile vs desktop revenue separately"

**Solution:** Modify `create_daily_business_metrics()`:
```python
# Add device-specific metrics
metrics['mobile_revenue'] = orders_df[
    orders_df.merge(sessions_df, on='session_id')['platform'] == 'mobile'
]['total_price'].sum()

metrics['desktop_revenue'] = orders_df[
    orders_df.merge(sessions_df, on='session_id')['platform'] == 'desktop'
]['total_price'].sum()
```

### Use Case 2: "I want to see which hour of day has most orders"

**Solution:** Create new aggregation:
```python
def create_hourly_order_distribution(orders_df):
    orders_df['hour'] = orders_df['time'].dt.hour
    hourly = orders_df.groupby('hour').agg({
        'order_id': 'count',
        'total_price': 'sum'
    })
    return hourly
```

### Use Case 3: "I need to calculate profit margin"

**Solution:** 
1. Add `product_cost` column to `order_line_item_table.csv`
2. Modify `create_product_performance_daily()`:
```python
# Calculate profit
order_items_df['profit'] = (order_items_df['product_price'] - order_items_df['product_cost']) * order_items_df['product_qty']
profit = order_items_df.groupby(['date', 'product_name'])['profit'].sum()
product_metrics['profit'] = profit
product_metrics['profit_margin'] = (profit / revenue * 100).round(2)
```

---

## 🔑 Key Concepts to Remember

### Aggregation = Summary
Don't repeat calculations. Calculate once, save result, use forever.

### GROUP BY = One Row Per...
- `groupby('date')` → One row per day
- `groupby(['date', 'product_name'])` → One row per product per day
- `groupby('user_id')` → One row per user

### Merge = JOIN tables
```python
# LEFT JOIN - keep all left table rows
result = left_df.merge(right_df, on='key', how='left')

# INNER JOIN - only matching rows
result = left_df.merge(right_df, on='key', how='inner')
```

### Filter BEFORE Grouping
```python
# CORRECT: Filter first (faster)
filtered = df[df['price'] > 100]
result = filtered.groupby('date')['price'].sum()

# WRONG: Group then filter (slower)
result = df.groupby('date')['price'].sum()
result = result[result > 100]
```

---

## 📞 Getting Help

1. **Check logs:** `logs/aggregation_log.txt` has detailed error messages
2. **Read documentation:** `DATABASE_DESIGN_DOCUMENTATION.md` has full explanations
3. **Test with small data:** Run with just 100 rows to debug faster
4. **Print variables:** Add `print(df.head())` to see what data looks like

---

## 📝 Before Making Changes

**Always:**
1. Make a backup copy of the script
2. Test with sample data first
3. Check log file after running
4. Verify output CSV has expected data
5. Update documentation if you add major features

---

## 🎓 Learning Resources

### To understand Pandas better:
- Official docs: https://pandas.pydata.org/docs/
- Tutorial: https://www.kaggle.com/learn/pandas

### To understand SQL concepts (helps with grouping):
- W3Schools SQL: https://www.w3schools.com/sql/

### To understand datetime operations:
- Python datetime: https://docs.python.org/3/library/datetime.html

---

**Last Updated:** 2026-02-13  
**Version:** 1.0
