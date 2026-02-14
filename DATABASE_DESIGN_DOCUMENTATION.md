# E-commerce Analytics Database Design Documentation

## 📋 Table of Contents
1. [Overview](#overview)
2. [Raw Data Tables Explained](#raw-data-tables-explained)
3. [Why We Create Aggregated Tables](#why-we-create-aggregated-tables)
4. [Aggregated Tables Detail](#aggregated-tables-detail)
5. [How to Add New Fields](#how-to-add-new-fields)
6. [Dashboard Mapping](#dashboard-mapping)
7. [Maintenance Guide](#maintenance-guide)

---

## Overview

### What This System Does
This system transforms raw e-commerce tracking data into dashboard-ready analytics tables. Instead of calculating metrics every time a dashboard loads (slow), we pre-calculate and store results (fast).

### The Flow
```
Raw Data (CSV files) 
    ↓
Python Processing (aggregation/calculation)
    ↓
Aggregated Tables (summary data)
    ↓
Dashboards (visualization)
```

---

## Raw Data Tables Explained

### 1. user_table.csv
**What it contains:** Basic customer profile information

| Field | Data Type | What It Means | Why We Need It |
|-------|-----------|---------------|----------------|
| user_id | String | Unique customer identifier | Link all user activity together |
| has_purchase_last_year | Boolean (0/1) | Did they buy in last 365 days? | Identify active vs dormant customers |
| has_purchase_last_qtr | Boolean (0/1) | Did they buy in last 90 days? | Identify recently active customers |

**Future Fields to Consider Adding:**
- `registration_date` - When user signed up (for customer age analysis)
- `email_verified` - Is account verified? (for user quality)
- `customer_tier` - VIP/Regular/New (for segmentation)
- `total_lifetime_revenue` - Total they've ever spent (for quick LTV lookup)

---

### 2. session_table.csv
**What it contains:** Every website visit and how users arrived

| Field | Data Type | What It Means | Why We Need It |
|-------|-----------|---------------|----------------|
| user_id | String | Who visited | Link visit to customer |
| session_id | String | Unique visit identifier | Group all actions in one visit |
| time | Timestamp | When visit started | Time-based analysis |
| platform | String | Desktop/Mobile/Tablet | Device analysis |
| device_type | String | iPhone/Samsung/etc | Specific device insights |
| country | String | User location | Geographic analysis |
| region | String | State/province | Regional targeting |
| city | String | Specific city | Local marketing |
| IP | String | IP address | Fraud detection |
| referrer | URL | Previous website | Traffic source |
| landing_page | URL path | First page seen | Landing page performance |
| landing_page_query | String | URL parameters | A/B test tracking |
| landing_page_hash | String | URL fragment | Single-page apps |
| browser | String | Chrome/Safari/etc | Browser compatibility |
| utm_source | String | google/facebook/email | Marketing source |
| utm_medium | String | cpc/social/email | Marketing medium |
| utm_campaign | String | summer_sale/etc | Campaign tracking |

**Why This Table Matters:**
- Tracks WHERE customers come from (marketing attribution)
- Tracks HOW they browse (device type for UX optimization)
- Essential for calculating conversion rate by channel

**Future Fields to Consider Adding:**
- `session_duration_seconds` - How long they stayed (pre-calculated)
- `pages_viewed` - Number of pages (pre-calculated)
- `is_converted` - Did they buy? (Boolean flag)
- `session_revenue` - Money spent this visit (for quick lookup)

---

### 3. order_table.csv
**What it contains:** Summary of each completed purchase

| Field | Data Type | What It Means | Why We Need It |
|-------|-----------|---------------|----------------|
| event_id | String | Unique purchase event ID | Track specific transaction |
| user_id | String | Who bought | Link to customer |
| session_id | String | Which visit led to purchase | Attribution analysis |
| order_id | String | Order number | Business identifier |
| time | Timestamp | When purchased | Time analysis |
| total_price | Decimal | Final amount paid | Revenue tracking |
| shipping_price | Decimal | Shipping cost | Understand margins |
| discount | Decimal | Discount amount | Promotion effectiveness |
| discount_coupon_code | String | Which coupon used | Coupon tracking |
| total_items | Integer | Number of unique products | Basket size |
| total_qty | Integer | Total quantity of all items | Volume analysis |

**Why This Table Matters:**
- Core revenue data
- Links purchases back to marketing campaigns (via session_id)
- Shows discount impact on sales

**Future Fields to Consider Adding:**
- `order_status` - Pending/Completed/Cancelled/Refunded (for fulfillment tracking)
- `payment_method` - Credit card/PayPal/etc (for payment analysis)
- `is_first_purchase` - Boolean flag (for new customer tracking)
- `profit_margin` - total_price - cost (for profitability)
- `tax_amount` - Taxes paid (for net revenue)

---

### 4. order_line_item_table.csv
**What it contains:** Individual products in each order (line-by-line breakdown)

| Field | Data Type | What It Means | Why We Need It |
|-------|-----------|---------------|----------------|
| event_id | String | Line item event ID | Unique identifier |
| user_id | String | Who bought | Customer link |
| session_id | String | Which visit | Attribution |
| order_id | String | Parent order | Link to order summary |
| time | Timestamp | When added to order | Timing analysis |
| product_name | String | Product identifier | Which product sold |
| product_price | Decimal | Unit price | Pricing analysis |
| product_qty | Integer | Quantity purchased | Volume analysis |

**Why This Table Matters:**
- Shows WHICH products are selling
- Enables product performance analysis
- Required for cross-sell analysis (what's bought together)

**Future Fields to Consider Adding:**
- `product_id` - Unique ID (better than name for variants)
- `product_category` - Electronics/Clothing/etc (for category analysis)
- `product_cost` - What you paid supplier (for profit margin)
- `product_sku` - Stock keeping unit (for inventory)

---

### 5. add_to_cart_table.csv
**What it contains:** Every time someone adds item to cart

| Field | Data Type | What It Means | Why We Need It |
|-------|-----------|---------------|----------------|
| event_id | String | Add-to-cart event ID | Unique identifier |
| user_id | String | Who added | Customer link |
| session_id | String | Which visit | Session tracking |
| time | Timestamp | When added | Timing analysis |
| domain | String | Website domain | Multi-site tracking |
| path | URL path | Page where they added | Page performance |
| hash | String | URL fragment | SPA tracking |
| query | String | URL parameters | Context tracking |
| previous_page | URL | Where they came from | Navigation analysis |
| product_name | String | What they added | Product tracking |
| product_price | Decimal | Price when added | Price sensitivity |
| product_qty | Integer | Quantity added | Volume interest |

**Why This Table Matters:**
- Critical for cart abandonment analysis
- Shows purchase INTENT even if they don't buy
- Conversion funnel step tracking

**Future Fields to Consider Adding:**
- `was_purchased` - Boolean (did this cart item convert to order?)
- `time_in_cart_minutes` - How long before checkout/removal
- `removed_from_cart` - Boolean (did they remove it?)

---

### 6. pageview_table.csv
**What it contains:** Every page a user views

| Field | Data Type | What It Means | Why We Need It |
|-------|-----------|---------------|----------------|
| event_id | String | Pageview event ID | Unique identifier |
| user_id | String | Who viewed | Customer link |
| session_id | String | Which visit | Session tracking |
| time | Timestamp | When viewed | Timing |
| domain | String | Website domain | Multi-site |
| path | URL path | Which page | Page tracking |
| hash | String | URL fragment | SPA tracking |
| query | String | URL parameters | Context |
| previous_page | URL | Navigation path | User journey |

**Why This Table Matters:**
- Shows user navigation patterns
- Identifies popular pages
- Required for bounce rate calculation

**Future Fields to Consider Adding:**
- `page_type` - Homepage/Product/Category/Checkout (for type analysis)
- `time_on_page_seconds` - Engagement duration
- `is_exit_page` - Boolean (did they leave from here?)

---

### 7. scroll_table.csv
**What it contains:** How far users scroll on pages

| Field | Data Type | What It Means | Why We Need It |
|-------|-----------|---------------|----------------|
| event_id | String | Scroll event ID | Unique identifier |
| user_id | String | Who scrolled | Customer link |
| session_id | String | Which visit | Session tracking |
| time | Timestamp | When scrolled | Timing |
| scroll_percent | Integer (0-100) | How far scrolled | Engagement depth |
| domain | String | Website domain | Multi-site |
| path | URL path | Which page | Page tracking |
| hash | String | URL fragment | SPA tracking |
| query | String | URL parameters | Context |
| previous_page | URL | Navigation path | Journey tracking |

**Why This Table Matters:**
- Measures content engagement
- Shows if users read your content
- Helps optimize page design

---

### 8. click_table.csv
**What it contains:** Every button/link click

| Field | Data Type | What It Means | Why We Need It |
|-------|-----------|---------------|----------------|
| event_id | String | Click event ID | Unique identifier |
| user_id | String | Who clicked | Customer link |
| session_id | String | Which visit | Session tracking |
| time | Timestamp | When clicked | Timing |
| domain | String | Website domain | Multi-site |
| path | URL path | Page where clicked | Page tracking |
| hash | String | URL fragment | SPA tracking |
| query | String | URL parameters | Context |
| href | URL | Link destination | Where it leads |
| target_id | String | HTML element ID | Specific element |
| target_tag | String | HTML tag (button/a) | Element type |
| target_text | String | Button/link text | What it says |
| previous_page | URL | Navigation path | Journey tracking |

**Why This Table Matters:**
- Shows which buttons/links work
- Helps optimize CTA placement
- Identifies user intent

---

## Why We Create Aggregated Tables

### The Problem
**Scenario:** You have a dashboard showing "Daily Revenue"

**Without Aggregation (BAD):**
```
User opens dashboard
    ↓
Dashboard queries order_table (50,000 rows)
    ↓
Calculate SUM(total_price) for each day
    ↓
Takes 10 seconds ❌
```

**With Aggregation (GOOD):**
```
User opens dashboard
    ↓
Dashboard queries daily_business_metrics (365 rows, one per day)
    ↓
Data already calculated
    ↓
Takes 0.5 seconds ✅
```

### Benefits
1. **Speed:** 10-100x faster dashboard loading
2. **Consistency:** Everyone sees same numbers (calculated once)
3. **Reduced Load:** Database doesn't get hammered with heavy queries
4. **Historical Snapshot:** Captures data as it was (even if raw data changes)

### Trade-offs
1. **Storage:** Need space for both raw + aggregated tables
2. **Freshness:** Aggregated data updated daily/hourly, not real-time
3. **Maintenance:** Need scripts to update aggregated tables

---

## Aggregated Tables Detail

### 1. daily_business_metrics
**Purpose:** High-level daily business KPIs for executive dashboard

**Why Created:** 
- Avoids scanning entire order_table every time dashboard opens
- Provides consistent daily snapshots

**Fields:**

| Field | Data Type | Calculation | Why Needed |
|-------|-----------|-------------|------------|
| date | Date | DATE(order.time) | Time dimension |
| total_revenue | Decimal | SUM(order.total_price) | Core business metric |
| total_orders | Integer | COUNT(DISTINCT order.order_id) | Volume tracking |
| total_sessions | Integer | COUNT(DISTINCT session.session_id) | Traffic tracking |
| total_users | Integer | COUNT(DISTINCT user.user_id) | Unique visitors |
| conversion_rate | Decimal | orders / sessions * 100 | Performance metric |
| avg_order_value | Decimal | revenue / orders | Basket size |
| new_customers | Integer | COUNT where has_purchase_last_year=0 | Acquisition |
| repeat_customers | Integer | COUNT where has_purchase_last_year=1 | Retention |

**How to Add New Field:**
Example - Add "Total Discount Given"
1. Modify `create_daily_business_metrics()` function
2. Add: `'total_discount': orders_df.groupby('date')['discount'].sum()`
3. Re-run aggregation script

**Update Frequency:** Once daily at 1 AM (after previous day completes)

---

### 2. session_attribution
**Purpose:** Link each session to its marketing source and outcome

**Why Created:**
- Enables marketing attribution (which campaigns drive sales)
- Pre-joins session + order data for faster queries

**Fields:**

| Field | Data Type | Source | Why Needed |
|-------|-----------|--------|------------|
| session_id | String | session_table | Primary key |
| user_id | String | session_table | User link |
| date | Date | session_table.time | Time dimension |
| utm_source | String | session_table | Marketing source |
| utm_medium | String | session_table | Marketing medium |
| utm_campaign | String | session_table | Campaign tracking |
| country | String | session_table | Geographic |
| device_type | String | session_table | Device analysis |
| platform | String | session_table | Desktop/Mobile |
| converted | Boolean | JOIN with order_table | Did they buy? |
| revenue | Decimal | order_table.total_price | Money made |
| order_id | String | order_table | Order reference |

**How It's Built:**
- LEFT JOIN session_table with order_table
- If order exists → converted=1, revenue=order.total_price
- If no order → converted=0, revenue=0

**How to Add New Field:**
Example - Add "Time to Conversion"
1. In `create_session_attribution()` function
2. Add: `merged['time_to_conversion'] = (merged['order_time'] - merged['session_time']).dt.total_seconds() / 60`
3. This shows minutes from session start to purchase

**Update Frequency:** Once daily

---

### 3. session_funnel
**Purpose:** Track each session's progress through conversion funnel

**Why Created:**
- Identifies WHERE users drop off in journey
- Enables funnel optimization

**Fields:**

| Field | Data Type | Calculation | Why Needed |
|-------|-----------|-------------|------------|
| session_id | String | session_table | Primary key |
| user_id | String | session_table | User link |
| date | Date | session_table.time | Time dimension |
| had_pageview | Boolean | Always 1 (every session has pageviews) | Funnel step 1 |
| had_product_view | Boolean | EXISTS in pageview where path contains '/product/' | Funnel step 2 |
| had_add_to_cart | Boolean | EXISTS in add_to_cart_table | Funnel step 3 |
| had_order | Boolean | EXISTS in order_table | Funnel step 4 |
| time_to_cart_minutes | Decimal | Minutes from session start to first cart add | Speed metric |
| time_to_order_minutes | Decimal | Minutes from session start to purchase | Conversion speed |

**Funnel Logic:**
```
All Sessions (100%)
    ↓ Drop-off %
Product Views (65%)
    ↓ Drop-off %
Add to Cart (20%)
    ↓ Drop-off %
Purchase (5%)
```

**How to Add New Field:**
Example - Add "Had Checkout View"
1. In `create_session_funnel()` function
2. Add: `funnel['had_checkout_view'] = funnel['session_id'].isin(checkout_sessions)`
3. Where `checkout_sessions` = pageview_df[pageview_df['path'].str.contains('/checkout')]

**Update Frequency:** Once daily

---

### 4. product_performance_daily
**Purpose:** Daily metrics for each product

**Why Created:**
- Avoid scanning millions of line items every dashboard load
- Track product trends over time

**Fields:**

| Field | Data Type | Calculation | Why Needed |
|-------|-----------|-------------|------------|
| date | Date | DATE(time) | Time dimension |
| product_name | String | order_line_item.product_name | Product identifier |
| times_purchased | Integer | COUNT(DISTINCT event_id) | Purchase frequency |
| total_quantity_sold | Integer | SUM(product_qty) | Volume sold |
| total_revenue | Decimal | SUM(product_price * product_qty) | Revenue tracking |
| times_added_to_cart | Integer | COUNT from add_to_cart_table | Interest level |
| cart_to_purchase_rate | Decimal | purchases / cart_adds * 100 | Conversion rate |

**How to Add New Field:**
Example - Add "Average Discount Per Product"
1. In `create_product_performance()` function
2. Need to add discount field to order_line_item_table first (raw data)
3. Then: `product_metrics['avg_discount'] = product_metrics.groupby(['date', 'product_name'])['discount'].mean()`

**Update Frequency:** Once daily

---

### 5. user_lifetime_metrics
**Purpose:** One row per user with all-time statistics

**Why Created:**
- Quick customer segmentation (VIP/Regular/At-Risk)
- No need to calculate LTV every time

**Fields:**

| Field | Data Type | Calculation | Why Needed |
|-------|-----------|-------------|------------|
| user_id | String | user_table | Primary key |
| first_order_date | Date | MIN(order.time) | Customer age |
| last_order_date | Date | MAX(order.time) | Recency |
| total_orders | Integer | COUNT(DISTINCT order_id) | Frequency |
| total_revenue | Decimal | SUM(order.total_price) | Monetary value |
| avg_order_value | Decimal | total_revenue / total_orders | Basket size |
| days_since_last_order | Integer | TODAY - last_order_date | Churn risk |
| rfm_recency_score | Integer (1-5) | Score based on recency | RFM component |
| rfm_frequency_score | Integer (1-5) | Score based on frequency | RFM component |
| rfm_monetary_score | Integer (1-5) | Score based on revenue | RFM component |
| rfm_segment | String | Combined RFM logic | Champion/Loyal/At-Risk/etc |

**RFM Scoring Logic:**
```
Recency (How recently they bought):
  Last 30 days = 5 (Best)
  31-90 days = 4
  91-180 days = 3
  181-365 days = 2
  365+ days = 1 (Worst)

Frequency (How often they buy):
  10+ orders = 5
  5-9 orders = 4
  3-4 orders = 3
  2 orders = 2
  1 order = 1

Monetary (How much they spend):
  $1000+ = 5
  $500-999 = 4
  $200-499 = 3
  $50-199 = 2
  <$50 = 1

Segment Examples:
  555 = Champion (recent, frequent, high-value)
  511 = Loyal (recent, frequent, but low-spend)
  155 = Big Spender (hasn't bought recently but high value)
  111 = Lost (haven't bought in year, infrequent, low-spend)
```

**How to Add New Field:**
Example - Add "Favorite Product Category"
1. Need product_category in order_line_item_table first
2. In `create_user_lifetime_metrics()` function
3. Add: `user_metrics['favorite_category'] = orders.groupby('user_id')['product_category'].agg(lambda x: x.mode()[0])`

**Update Frequency:** Once weekly (customer behavior changes slowly)

---

### 6. page_engagement_metrics
**Purpose:** Daily performance for each page

**Why Created:**
- Identify high/low performing pages
- UX optimization insights

**Fields:**

| Field | Data Type | Calculation | Why Needed |
|-------|-----------|-------------|------------|
| date | Date | DATE(time) | Time dimension |
| page_path | String | pageview.path | Page identifier |
| pageviews | Integer | COUNT(*) | Traffic volume |
| unique_users | Integer | COUNT(DISTINCT user_id) | Reach |
| avg_scroll_depth | Decimal | AVG(scroll.scroll_percent) | Engagement depth |
| total_clicks | Integer | COUNT from click_table | Interaction count |
| sessions_with_this_page | Integer | COUNT(DISTINCT session_id) | Session reach |

**How to Add New Field:**
Example - Add "Bounce Rate"
1. In `create_page_engagement_metrics()` function
2. Add: 
```python
bounces = pageview_df.groupby('session_id').size() == 1
page_metrics['bounce_rate'] = bounces.sum() / total_sessions * 100
```

**Update Frequency:** Once daily

---

### 7. coupon_performance
**Purpose:** Track discount code effectiveness

**Why Created:**
- Measure ROI of promotions
- Identify popular coupons

**Fields:**

| Field | Data Type | Calculation | Why Needed |
|-------|-----------|-------------|------------|
| date | Date | DATE(order.time) | Time dimension |
| discount_coupon_code | String | order.discount_coupon_code | Coupon identifier |
| usage_count | Integer | COUNT(DISTINCT order_id) | How many times used |
| total_discount_given | Decimal | SUM(order.discount) | Cost of promotion |
| total_revenue | Decimal | SUM(order.total_price) | Revenue with coupon |
| avg_order_value | Decimal | total_revenue / usage_count | Basket size |

**How to Add New Field:**
Example - Add "New vs Repeat Customer Usage"
1. In `create_coupon_performance()` function
2. Add: 
```python
coupon_metrics['new_customer_usage'] = orders[orders['is_first_purchase']==1].groupby('discount_coupon_code').size()
coupon_metrics['repeat_customer_usage'] = orders[orders['is_first_purchase']==0].groupby('discount_coupon_code').size()
```

**Update Frequency:** Once daily

---

## How to Add New Fields

### Step-by-Step Process

#### Example: Adding "Profit Margin" to daily_business_metrics

**Step 1: Check if raw data exists**
- Do we have `cost` field in order_line_item_table?
- If NO → Need to add to raw data collection first
- If YES → Proceed to Step 2

**Step 2: Modify aggregation function**
```python
def create_daily_business_metrics(orders_df, sessions_df, users_df, order_items_df):
    # Existing calculations...
    
    # NEW: Calculate profit margin
    # First, calculate total cost
    order_items_df['total_cost'] = order_items_df['product_cost'] * order_items_df['product_qty']
    daily_cost = order_items_df.groupby('date')['total_cost'].sum()
    
    # Add to metrics dictionary
    metrics['total_cost'] = daily_cost
    metrics['profit_margin'] = ((metrics['total_revenue'] - metrics['total_cost']) / 
                                 metrics['total_revenue'] * 100)
    
    return metrics
```

**Step 3: Update CSV column list**
```python
# In the CSV writing section, add new columns
daily_metrics_df.to_csv('daily_business_metrics.csv', 
                        columns=['date', 'total_revenue', 'total_orders', ..., 'profit_margin'])
```

**Step 4: Re-run aggregation script**
```bash
python ecommerce_data_processor.py
```

**Step 5: Update dashboard**
- Dashboard now has access to new `profit_margin` column

---

### Common Field Addition Scenarios

#### Scenario 1: Simple Aggregation (SUM/AVG/COUNT)
**Example:** Add "Total Shipping Costs"
```python
metrics['total_shipping'] = orders_df.groupby('date')['shipping_price'].sum()
```

#### Scenario 2: Conditional Counting
**Example:** Add "Orders Over $500"
```python
metrics['high_value_orders'] = orders_df[orders_df['total_price'] > 500].groupby('date')['order_id'].count()
```

#### Scenario 3: Ratio/Percentage Calculation
**Example:** Add "Mobile Conversion Rate"
```python
mobile_sessions = sessions_df[sessions_df['platform'] == 'mobile']
mobile_orders = orders_df[orders_df['session_id'].isin(mobile_sessions['session_id'])]
metrics['mobile_conversion_rate'] = (len(mobile_orders) / len(mobile_sessions)) * 100
```

#### Scenario 4: Time-based Calculation
**Example:** Add "Average Time to Purchase"
```python
merged = sessions_df.merge(orders_df, on='session_id')
merged['time_to_purchase'] = (merged['order_time'] - merged['session_time']).dt.total_seconds() / 60
metrics['avg_time_to_purchase_minutes'] = merged.groupby('date')['time_to_purchase'].mean()
```

#### Scenario 5: Cross-table Calculation
**Example:** Add "Cart Abandonment Rate"
```python
# Sessions with cart adds
sessions_with_cart = add_to_cart_df['session_id'].unique()
# Sessions with orders
sessions_with_order = orders_df['session_id'].unique()
# Sessions with cart but no order
abandoned_sessions = set(sessions_with_cart) - set(sessions_with_order)
metrics['cart_abandonment_rate'] = (len(abandoned_sessions) / len(sessions_with_cart)) * 100
```

---

## Dashboard Mapping

### Which Aggregated Table Powers Which Dashboard

| Dashboard | Primary Tables | Refresh Frequency |
|-----------|---------------|-------------------|
| **Executive Overview** | daily_business_metrics | Daily at 1 AM |
| **Marketing Attribution** | session_attribution, daily_channel_performance | Daily at 1 AM |
| **Conversion Funnel** | session_funnel, daily_funnel_summary | Daily at 1 AM |
| **Product Performance** | product_performance_daily | Daily at 1 AM |
| **Customer Segmentation** | user_lifetime_metrics, cohort_analysis | Weekly on Sundays |
| **UX Engagement** | page_engagement_metrics, click_heatmap | Daily at 1 AM |
| **Discount Analysis** | coupon_performance | Daily at 1 AM |
| **Real-Time Operations** | RAW TABLES (direct query) | Real-time |

---

## Maintenance Guide

### Daily Tasks (Automated)
1. **1:00 AM** - Run aggregation scripts for previous day
2. **1:30 AM** - Verify all aggregated tables updated
3. **2:00 AM** - Dashboard cache refresh

### Weekly Tasks
1. **Sunday 2:00 AM** - Update user_lifetime_metrics (slower changing)
2. **Sunday 3:00 AM** - Generate cohort analysis

### Monthly Tasks
1. **1st of month** - Archive previous month raw data
2. **1st of month** - Validate aggregated vs raw data consistency
3. **1st of month** - Review and optimize slow queries

### How to Debug Issues

#### Issue: Dashboard shows zero revenue
**Check:**
1. Did aggregation script run? Check log file
2. Is raw data present for that date?
3. Run manual aggregation for one day to test

#### Issue: Numbers don't match between dashboards
**Check:**
1. Are all dashboards using same aggregated table?
2. Did aggregation script complete successfully?
3. Check for timezone issues in date filtering

#### Issue: New field not showing in dashboard
**Check:**
1. Did you add field to aggregation function?
2. Did you re-run aggregation script?
3. Did you update CSV columns list?
4. Did dashboard refresh its cache?

---

## File Structure

```
/ecommerce_analytics/
├── raw_data/
│   ├── user_table.csv
│   ├── session_table.csv
│   ├── order_table.csv
│   ├── order_line_item_table.csv
│   ├── add_to_cart_table.csv
│   ├── pageview_table.csv
│   ├── scroll_table.csv
│   └── click_table.csv
│
├── aggregated_data/
│   ├── daily_business_metrics.csv
│   ├── session_attribution.csv
│   ├── session_funnel.csv
│   ├── product_performance_daily.csv
│   ├── user_lifetime_metrics.csv
│   ├── page_engagement_metrics.csv
│   └── coupon_performance.csv
│
├── scripts/
│   ├── ecommerce_data_processor.py (main script)
│   └── data_validator.py (validation checks)
│
├── logs/
│   └── aggregation_log_YYYY-MM-DD.txt
│
└── documentation/
    └── DATABASE_DESIGN_DOCUMENTATION.md (this file)
```

---

## Performance Optimization Tips

### 1. Use Date Partitioning
Instead of one huge CSV, split by date:
```
aggregated_data/
├── daily_business_metrics_2024.csv
├── daily_business_metrics_2025.csv
└── daily_business_metrics_2026.csv
```

### 2. Index Important Columns
When loading to database, index:
- date (for time filtering)
- user_id (for user lookup)
- session_id (for session lookup)
- product_name (for product filtering)

### 3. Incremental Updates
Only recalculate yesterday's data, not entire history:
```python
# Only process new data
new_orders = orders_df[orders_df['date'] == yesterday]
```

### 4. Compression
Save aggregated CSVs with compression:
```python
df.to_csv('metrics.csv.gz', compression='gzip')
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-13 | Initial documentation created |

---

## Contact & Support
For questions about this documentation or data structure changes, contact the data engineering team.
