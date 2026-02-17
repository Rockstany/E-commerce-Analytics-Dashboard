"""
E-COMMERCE DATA AGGREGATION SCRIPT
===================================

PURPOSE:
This script reads raw e-commerce tracking data (CSV files) and creates
aggregated summary tables for fast dashboard loading.

WHAT IT DOES:
1. Loads 8 raw CSV files (user, session, order, etc.)
2. Performs calculations and aggregations
3. Creates 7 aggregated summary tables
4. Exports results as CSV files

WHY WE NEED THIS:
- Dashboards load 10-100x faster by reading pre-calculated summaries
- Consistent metrics across all dashboards
- Reduces database load

WHEN TO RUN:
- Daily at 1 AM (automated via cron job or task scheduler)
- After any raw data updates
- When adding new calculated fields

HOW TO MODIFY:
- See DATABASE_DESIGN_DOCUMENTATION.md for detailed instructions
- Each function has comments explaining what can be changed

AUTHOR: Data Engineering Team
LAST UPDATED: 2026-02-17
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import warnings
warnings.filterwarnings('ignore')

# ==============================================================================
# CONFIGURATION SECTION
# ==============================================================================

class Config:
    """
    Configuration settings for the data processing pipeline
    
    MODIFY THESE PATHS based on your folder structure
    """
    # Input folder - where raw CSV files are stored
    RAW_DATA_DIR = 'raw_data/'
    
    # Output folder - where aggregated CSV files will be saved
    AGGREGATED_DATA_DIR = 'aggregated_data/'
    
    # Log folder - where processing logs are saved
    LOG_DIR = 'logs/'
    
    # Date range to process
    # None = process all data
    # Set specific date to process only that day: datetime(2026, 2, 13)
    START_DATE = None
    END_DATE = None
    
    # Date format used across all output columns
    # DD/MM/YYYY
    DATE_FORMAT = '%d/%m/%Y'

    # Create directories if they don't exist
    @staticmethod
    def setup_directories():
        """Creates necessary folders if they don't exist"""
        for directory in [Config.RAW_DATA_DIR, 
                         Config.AGGREGATED_DATA_DIR, 
                         Config.LOG_DIR]:
            if not os.path.exists(directory):
                os.makedirs(directory)
                print(f"Created directory: {directory}")

# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def log_message(message, log_file='aggregation_log.txt'):
    """
    Writes messages to both console and log file
    
    WHY: Track when script runs and if errors occur
    
    Args:
        message (str): Message to log
        log_file (str): Name of log file
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] {message}"
    print(log_entry)
    
    # Ensure log directory exists before writing
    if not os.path.exists(Config.LOG_DIR):
        os.makedirs(Config.LOG_DIR)
    
    # Write to log file
    log_path = os.path.join(Config.LOG_DIR, log_file)
    with open(log_path, 'a') as f:
        f.write(log_entry + '\n')


def load_csv_safe(filename, required_columns=None):
    """
    Safely loads a CSV file with error handling
    
    WHY: Prevents script from crashing if file is missing or corrupted
    
    Args:
        filename (str): Name of CSV file to load
        required_columns (list): Columns that must exist
        
    Returns:
        DataFrame or None if file not found
    """
    filepath = os.path.join(Config.RAW_DATA_DIR, filename)
    
    try:
        df = pd.read_csv(filepath)
        log_message(f"✓ Loaded {filename}: {len(df)} rows")
        
        # Check if required columns exist
        if required_columns:
            missing = set(required_columns) - set(df.columns)
            if missing:
                log_message(f"⚠ Warning: {filename} missing columns: {missing}")
        
        return df
    
    except FileNotFoundError:
        log_message(f"✗ Error: {filename} not found in {Config.RAW_DATA_DIR}")
        return None
    
    except Exception as e:
        log_message(f"✗ Error loading {filename}: {str(e)}")
        return None


def parse_dates(df, date_columns):
    """
    Converts string dates to datetime format
    
    WHY: Pandas needs proper datetime format for date operations
    
    Args:
        df (DataFrame): DataFrame to process
        date_columns (list): Column names containing dates
        
    Returns:
        DataFrame with parsed dates
    """
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    return df


# ==============================================================================
# DATA LOADING FUNCTIONS
# ==============================================================================

def load_all_raw_data():
    """
    Loads all 8 raw CSV files into memory
    
    WHY: Central function to load all data with consistent error handling
    
    Returns:
        dict: Dictionary with DataFrames for each table
    """
    log_message("="*60)
    log_message("STARTING DATA LOAD")
    log_message("="*60)
    
    data = {}
    
    # 1. USER TABLE
    # Contains: user_id, has_purchase_last_year, has_purchase_last_qtr
    log_message("\n1. Loading user_table.csv...")
    data['users'] = load_csv_safe('user_table.csv', 
                                   required_columns=['user_id'])
    
    # 2. SESSION TABLE  
    # Contains: user_id, session_id, time, utm_source, utm_medium, etc.
    log_message("\n2. Loading session_table.csv...")
    data['sessions'] = load_csv_safe('session_table.csv',
                                      required_columns=['user_id', 'session_id', 'time'])
    if data['sessions'] is not None:
        data['sessions'] = parse_dates(data['sessions'], ['time'])
    
    # 3. ORDER TABLE
    # Contains: order_id, user_id, session_id, total_price, discount, etc.
    log_message("\n3. Loading order_table.csv...")
    data['orders'] = load_csv_safe('order_table.csv',
                                    required_columns=['order_id', 'user_id', 'session_id', 'time'])
    if data['orders'] is not None:
        data['orders'] = parse_dates(data['orders'], ['time'])
    
    # 4. ORDER LINE ITEM TABLE
    # Contains: product_name, product_price, product_qty, order_id, etc.
    log_message("\n4. Loading order_line_item_table.csv...")
    data['order_items'] = load_csv_safe('order_line_item_table.csv',
                                         required_columns=['order_id', 'product_name'])
    if data['order_items'] is not None:
        data['order_items'] = parse_dates(data['order_items'], ['time'])
    
    # 5. ADD TO CART TABLE
    # Contains: product_name, product_price, session_id, time, etc.
    log_message("\n5. Loading add_to_cart_table.csv...")
    data['cart'] = load_csv_safe('add_to_cart_table.csv',
                                  required_columns=['session_id', 'product_name'])
    if data['cart'] is not None:
        data['cart'] = parse_dates(data['cart'], ['time'])
    
    # 6. PAGEVIEW TABLE
    # Contains: session_id, path, time, etc.
    log_message("\n6. Loading pageview_table.csv...")
    data['pageviews'] = load_csv_safe('pageview_table.csv',
                                       required_columns=['session_id', 'path'])
    if data['pageviews'] is not None:
        data['pageviews'] = parse_dates(data['pageviews'], ['time'])
    
    # 7. SCROLL TABLE
    # Contains: session_id, scroll_percent, path, time, etc.
    log_message("\n7. Loading scroll_table.csv...")
    data['scrolls'] = load_csv_safe('scroll_table.csv',
                                     required_columns=['session_id', 'scroll_percent'])
    if data['scrolls'] is not None:
        data['scrolls'] = parse_dates(data['scrolls'], ['time'])
    
    # 8. CLICK TABLE
    # Contains: session_id, target_text, href, time, etc.
    log_message("\n8. Loading click_table.csv...")
    data['clicks'] = load_csv_safe('click_table.csv',
                                    required_columns=['session_id'])
    if data['clicks'] is not None:
        data['clicks'] = parse_dates(data['clicks'], ['time'])
    
    log_message("\n" + "="*60)
    log_message("DATA LOAD COMPLETE")
    log_message("="*60)
    
    return data


# ==============================================================================
# AGGREGATION FUNCTION 1: DAILY BUSINESS METRICS
# ==============================================================================

def create_daily_business_metrics(orders_df, sessions_df, users_df):
    """
    Creates high-level daily KPIs for executive dashboard
    
    PURPOSE:
    - Provides daily snapshot of business health
    - Fast loading for executive dashboard
    - Historical trend analysis
    
    CALCULATES:
    - Total revenue per day
    - Number of orders per day
    - Number of sessions (website visits) per day
    - Conversion rate (% of sessions that become orders)
    - Average order value
    - New vs repeat customers
    
    HOW TO ADD NEW FIELD:
    Example - Add "Total Discount Given":
    1. Add this line: metrics['total_discount'] = orders_df.groupby('date')['discount'].sum()
    2. Add 'total_discount' to the DataFrame creation at the end
    
    Args:
        orders_df (DataFrame): Order data
        sessions_df (DataFrame): Session data
        users_df (DataFrame): User data
        
    Returns:
        DataFrame: Daily aggregated metrics
    """
    log_message("\n" + "="*60)
    log_message("CREATING: daily_business_metrics")
    log_message("="*60)
    
    # Check if we have required data
    if orders_df is None or sessions_df is None:
        log_message("⚠ Skipping - missing required data")
        return None
    
    # Extract date from timestamp — format: DD/MM/YYYY HH:MM:SS
    orders_df['date'] = orders_df['time'].dt.strftime(Config.DATE_FORMAT)
    sessions_df['date'] = sessions_df['time'].dt.strftime(Config.DATE_FORMAT)
    
    # Initialize metrics dictionary
    metrics = {}
    
    # 1. TOTAL REVENUE PER DAY
    # WHY: Core business metric - how much money made each day
    # HOW: Sum all order.total_price for each date
    log_message("  Calculating total revenue...")
    metrics['total_revenue'] = orders_df.groupby('date')['total_price'].sum()
    
    # 2. TOTAL ORDERS PER DAY
    # WHY: Volume metric - how many transactions
    # HOW: Count unique order_id for each date
    log_message("  Calculating total orders...")
    metrics['total_orders'] = orders_df.groupby('date')['order_id'].nunique()
    
    # 3. TOTAL SESSIONS PER DAY
    # WHY: Traffic metric - how many website visits
    # HOW: Count unique session_id for each date
    log_message("  Calculating total sessions...")
    metrics['total_sessions'] = sessions_df.groupby('date')['session_id'].nunique()
    
    # 4. TOTAL UNIQUE USERS PER DAY
    # WHY: Reach metric - how many different people visited
    # HOW: Count unique user_id for each date
    log_message("  Calculating total users...")
    metrics['total_users'] = sessions_df.groupby('date')['user_id'].nunique()
    
    # 5. CONVERSION RATE
    # WHY: Performance metric - % of visits that result in purchase
    # HOW: (orders / sessions) * 100
    # FORMULA: If 100 sessions and 5 orders = 5% conversion rate
    log_message("  Calculating conversion rate...")
    metrics['conversion_rate'] = (metrics['total_orders'] / metrics['total_sessions'] * 100).fillna(0)
    
    # 6. AVERAGE ORDER VALUE (AOV)
    # WHY: Basket size metric - average amount per order
    # HOW: total_revenue / total_orders
    # EXAMPLE: $10,000 revenue / 50 orders = $200 AOV
    log_message("  Calculating average order value...")
    metrics['avg_order_value'] = (metrics['total_revenue'] / metrics['total_orders']).fillna(0)
    
    # 7. NEW VS REPEAT CUSTOMERS
    # WHY: Acquisition vs retention tracking
    # HOW: Join orders with users, count based on has_purchase_last_year flag
    if users_df is not None and 'has_purchase_last_year' in users_df.columns:
        log_message("  Calculating new vs repeat customers...")
        
        # Merge orders with user data to get purchase history
        orders_with_user = orders_df.merge(users_df[['user_id', 'has_purchase_last_year']], 
                                           on='user_id', 
                                           how='left')
        
        # Count new customers (has_purchase_last_year = 0)
        metrics['new_customers'] = orders_with_user[
            orders_with_user['has_purchase_last_year'] == 0
        ].groupby('date')['user_id'].nunique()
        
        # Count repeat customers (has_purchase_last_year = 1)
        metrics['repeat_customers'] = orders_with_user[
            orders_with_user['has_purchase_last_year'] == 1
        ].groupby('date')['user_id'].nunique()
    
    # Combine all metrics into single DataFrame
    log_message("  Combining metrics...")
    result_df = pd.DataFrame(metrics)
    result_df = result_df.reset_index()
    result_df.columns.name = None
    
    # Round decimal places for cleaner output
    result_df['total_revenue'] = result_df['total_revenue'].round(2)
    result_df['conversion_rate'] = result_df['conversion_rate'].round(2)
    result_df['avg_order_value'] = result_df['avg_order_value'].round(2)
    
    log_message(f"✓ Created {len(result_df)} daily records")
    log_message(f"  Date range: {result_df['date'].min()} to {result_df['date'].max()}")
    log_message(f"  Total revenue in dataset: ${result_df['total_revenue'].sum():,.2f}")
    
    return result_df


# ==============================================================================
# AGGREGATION FUNCTION 2: SESSION ATTRIBUTION
# ==============================================================================

def create_session_attribution(sessions_df, orders_df):
    """
    Links each session to its marketing source and conversion outcome
    
    PURPOSE:
    - Marketing attribution (which campaigns drive sales)
    - ROI calculation for ad spend
    - Channel performance comparison
    
    CREATES:
    - One row per session
    - Includes marketing source (UTM parameters)
    - Includes outcome (did they buy? how much?)
    
    HOW IT WORKS:
    1. Take all sessions
    2. LEFT JOIN with orders (some sessions have orders, some don't)
    3. If order exists → converted=True, revenue=order_amount
    4. If no order → converted=False, revenue=0
    
    HOW TO ADD NEW FIELD:
    Example - Add "Time to Conversion":
    1. Calculate: merged['time_to_conversion'] = (merged['order_time'] - merged['session_time']).dt.total_seconds() / 60
    2. Add to column list when saving
    
    Args:
        sessions_df (DataFrame): Session data
        orders_df (DataFrame): Order data
        
    Returns:
        DataFrame: Session-level attribution data
    """
    log_message("\n" + "="*60)
    log_message("CREATING: session_attribution")
    log_message("="*60)
    
    if sessions_df is None:
        log_message("⚠ Skipping - missing session data")
        return None
    
    log_message("  Merging sessions with orders...")
    
    # LEFT JOIN sessions with orders
    # LEFT JOIN means: keep all sessions, add order data if it exists
    # Result: sessions with orders get order details, sessions without orders get NULL
    merged = sessions_df.merge(
        orders_df[['session_id', 'order_id', 'total_price', 'time']] if orders_df is not None else pd.DataFrame(),
        on='session_id',
        how='left',
        suffixes=('_session', '_order')
    )
    
    # Extract date from session time — format: DD/MM/YYYY HH:MM:SS
    merged['date'] = merged['time_session'].dt.strftime(Config.DATE_FORMAT)
    
    # Create converted flag
    # If order_id exists (not NULL) → converted = 1 (True)
    # If order_id is NULL → converted = 0 (False)
    log_message("  Calculating conversion flags...")
    merged['converted'] = merged['order_id'].notna().astype(int)
    
    # Set revenue
    # If converted → use total_price
    # If not converted → 0
    merged['revenue'] = merged['total_price'].fillna(0)
    
    # Select and rename columns for output
    log_message("  Selecting columns...")
    output_columns = [
        'session_id',
        'user_id',
        'date',
        'utm_source',
        'utm_medium',
        'utm_campaign',
        'country',
        'device_type',
        'platform',
        'converted',
        'revenue',
        'order_id'
    ]
    
    # Only keep columns that exist in the data
    available_columns = [col for col in output_columns if col in merged.columns]
    result_df = merged[available_columns].copy()
    
    # Round revenue
    result_df['revenue'] = result_df['revenue'].round(2)
    
    # Fill missing UTM values with 'direct'
    # WHY: Sessions without UTM = direct traffic (typed URL, bookmark, etc.)
    for col in ['utm_source', 'utm_medium', 'utm_campaign']:
        if col in result_df.columns:
            result_df[col] = result_df[col].fillna('direct')
    
    log_message(f"✓ Created {len(result_df)} session records")
    log_message(f"  Converted sessions: {result_df['converted'].sum()}")
    log_message(f"  Conversion rate: {result_df['converted'].mean()*100:.2f}%")
    log_message(f"  Total attributed revenue: ${result_df['revenue'].sum():,.2f}")
    
    return result_df


# ==============================================================================
# AGGREGATION FUNCTION 3: SESSION FUNNEL
# ==============================================================================

def create_session_funnel(sessions_df, pageviews_df, cart_df, orders_df):
    """
    Tracks each session's progress through the conversion funnel
    
    PURPOSE:
    - Identify where users drop off
    - Calculate conversion rate at each funnel step
    - Optimize low-performing steps
    
    FUNNEL STEPS:
    1. Session Start (100% - everyone has this)
    2. Product View (did they view a product page?)
    3. Add to Cart (did they add item to cart?)
    4. Purchase (did they complete order?)
    
    HOW IT WORKS:
    - Take all sessions as base
    - Check if session_id appears in pageviews with '/product/' path → had_product_view = True
    - Check if session_id appears in cart table → had_add_to_cart = True
    - Check if session_id appears in orders table → had_order = True
    
    HOW TO ADD NEW FUNNEL STEP:
    Example - Add "Viewed Checkout":
    1. Create flag: funnel['had_checkout_view'] = funnel['session_id'].isin(
           pageviews_df[pageviews_df['path'].str.contains('/checkout')]['session_id']
       )
    2. Add to output columns
    
    Args:
        sessions_df (DataFrame): Session data
        pageviews_df (DataFrame): Pageview data
        cart_df (DataFrame): Add-to-cart data
        orders_df (DataFrame): Order data
        
    Returns:
        DataFrame: Session-level funnel data
    """
    log_message("\n" + "="*60)
    log_message("CREATING: session_funnel")
    log_message("="*60)
    
    if sessions_df is None:
        log_message("⚠ Skipping - missing session data")
        return None
    
    # Start with all sessions
    log_message("  Building funnel base...")
    funnel = sessions_df[['session_id', 'user_id', 'time']].copy()

    # Extract date from session time — format: DD/MM/YYYY HH:MM:SS
    funnel['date'] = funnel['time'].dt.strftime(Config.DATE_FORMAT)
    
    # STEP 1: HAD PAGEVIEW (always True since session = at least 1 pageview)
    funnel['had_pageview'] = 1
    
    # STEP 2: HAD PRODUCT VIEW
    # Logic: Did this session view any page with '/product/' in the path?
    log_message("  Checking product views...")
    if pageviews_df is not None and 'path' in pageviews_df.columns:
        product_view_sessions = pageviews_df[
            pageviews_df['path'].str.contains('/product/', na=False)
        ]['session_id'].unique()
        
        # Mark sessions that viewed products
        funnel['had_product_view'] = funnel['session_id'].isin(product_view_sessions).astype(int)
    else:
        funnel['had_product_view'] = 0
    
    # STEP 3: HAD ADD TO CART
    # Logic: Did this session add anything to cart?
    log_message("  Checking cart additions...")
    if cart_df is not None:
        cart_sessions = cart_df['session_id'].unique()
        funnel['had_add_to_cart'] = funnel['session_id'].isin(cart_sessions).astype(int)
    else:
        funnel['had_add_to_cart'] = 0
    
    # STEP 4: HAD ORDER
    # Logic: Did this session result in a purchase?
    log_message("  Checking orders...")
    if orders_df is not None:
        order_sessions = orders_df['session_id'].unique()
        funnel['had_order'] = funnel['session_id'].isin(order_sessions).astype(int)
    else:
        funnel['had_order'] = 0
    
    # CALCULATE TIME METRICS
    # Time from session start to first cart add
    log_message("  Calculating time metrics...")
    if cart_df is not None:
        # Get first cart add time for each session
        first_cart = cart_df.groupby('session_id')['time'].min().reset_index()
        first_cart.columns = ['session_id', 'first_cart_time']
        
        funnel = funnel.merge(first_cart, on='session_id', how='left')
        
        # Calculate minutes to cart
        funnel['time_to_cart_minutes'] = (
            (funnel['first_cart_time'] - funnel['time']).dt.total_seconds() / 60
        ).round(2)
    else:
        funnel['time_to_cart_minutes'] = None
    
    # Time from session start to order
    if orders_df is not None:
        # Get order time for each session
        order_time = orders_df.groupby('session_id')['time'].min().reset_index()
        order_time.columns = ['session_id', 'order_time']
        
        funnel = funnel.merge(order_time, on='session_id', how='left')
        
        # Calculate minutes to order
        funnel['time_to_order_minutes'] = (
            (funnel['order_time'] - funnel['time']).dt.total_seconds() / 60
        ).round(2)
    else:
        funnel['time_to_order_minutes'] = None
    
    # Select final columns
    output_columns = [
        'session_id',
        'user_id',
        'date',
        'had_pageview',
        'had_product_view',
        'had_add_to_cart',
        'had_order',
        'time_to_cart_minutes',
        'time_to_order_minutes'
    ]
    
    result_df = funnel[output_columns].copy()
    
    # Calculate funnel statistics for logging
    total_sessions = len(result_df)
    product_views = result_df['had_product_view'].sum()
    cart_adds = result_df['had_add_to_cart'].sum()
    orders = result_df['had_order'].sum()
    
    log_message(f"✓ Created {len(result_df)} session funnel records")
    log_message(f"  Funnel breakdown:")
    log_message(f"    Sessions: {total_sessions} (100.0%)")
    log_message(f"    Product Views: {product_views} ({product_views/total_sessions*100:.1f}%)")
    log_message(f"    Cart Adds: {cart_adds} ({cart_adds/total_sessions*100:.1f}%)")
    log_message(f"    Orders: {orders} ({orders/total_sessions*100:.1f}%)")
    
    return result_df


# ==============================================================================
# AGGREGATION FUNCTION 4: PRODUCT PERFORMANCE
# ==============================================================================

def create_product_performance_daily(order_items_df, cart_df, pageviews_df):
    """
    Daily performance metrics for each product
    
    PURPOSE:
    - Identify best/worst selling products
    - Track product trends over time
    - Optimize inventory and merchandising
    
    METRICS PER PRODUCT PER DAY:
    - Times purchased
    - Total quantity sold
    - Total revenue
    - Times added to cart
    - Cart-to-purchase conversion rate
    
    HOW TO ADD NEW METRIC:
    Example - Add "Product Views":
    1. Extract product name from pageview path
    2. Count views per product: product_views = pageviews_df.groupby(['date', 'product_name']).size()
    3. Merge into product_metrics
    
    Args:
        order_items_df (DataFrame): Order line items
        cart_df (DataFrame): Cart additions
        pageviews_df (DataFrame): Page views
        
    Returns:
        DataFrame: Product-level daily metrics
    """
    log_message("\n" + "="*60)
    log_message("CREATING: product_performance_daily")
    log_message("="*60)
    
    if order_items_df is None:
        log_message("⚠ Skipping - missing order items data")
        return None
    
    # Extract date from timestamp — format: DD/MM/YYYY HH:MM:SS
    order_items_df['date'] = order_items_df['time'].dt.strftime(Config.DATE_FORMAT)
    
    # GROUP BY: date + product_name
    # This creates one row per product per day
    log_message("  Aggregating order data...")
    
    # METRIC 1: Times Purchased
    # Count how many separate orders included this product
    times_purchased = order_items_df.groupby(['date', 'product_name'])['event_id'].count()
    
    # METRIC 2: Total Quantity Sold
    # Sum of all quantities sold
    quantity_sold = order_items_df.groupby(['date', 'product_name'])['product_qty'].sum()
    
    # METRIC 3: Total Revenue
    # Sum of (price × quantity) for each line item
    order_items_df['line_revenue'] = order_items_df['product_price'] * order_items_df['product_qty']
    revenue = order_items_df.groupby(['date', 'product_name'])['line_revenue'].sum()
    
    # Combine purchase metrics
    product_metrics = pd.DataFrame({
        'times_purchased': times_purchased,
        'total_quantity_sold': quantity_sold,
        'total_revenue': revenue
    }).reset_index()
    
    # METRIC 4: Times Added to Cart
    # How many times was this product added to cart?
    log_message("  Adding cart data...")
    if cart_df is not None:
        # Extract date from timestamp — format: DD/MM/YYYY HH:MM:SS
        cart_df['date'] = cart_df['time'].dt.strftime(Config.DATE_FORMAT)
        cart_adds = cart_df.groupby(['date', 'product_name'])['event_id'].count().reset_index()
        cart_adds.columns = ['date', 'product_name', 'times_added_to_cart']
        
        # Merge cart data
        product_metrics = product_metrics.merge(cart_adds, 
                                               on=['date', 'product_name'], 
                                               how='left')
        product_metrics['times_added_to_cart'] = product_metrics['times_added_to_cart'].fillna(0).astype(int)
        
        # METRIC 5: Cart-to-Purchase Rate
        # What % of cart adds result in purchase?
        # Formula: (purchases / cart_adds) * 100
        # Example: 20 cart adds, 10 purchases = 50% conversion
        product_metrics['cart_to_purchase_rate'] = (
            product_metrics['times_purchased'] / 
            product_metrics['times_added_to_cart'] * 100
        ).fillna(0).round(2)
    else:
        product_metrics['times_added_to_cart'] = 0
        product_metrics['cart_to_purchase_rate'] = 0
    
    # Round revenue
    product_metrics['total_revenue'] = product_metrics['total_revenue'].round(2)
    
    # Sort by date and revenue
    product_metrics = product_metrics.sort_values(['date', 'total_revenue'], 
                                                  ascending=[True, False])
    
    log_message(f"✓ Created {len(product_metrics)} product-day records")
    log_message(f"  Unique products: {product_metrics['product_name'].nunique()}")
    log_message(f"  Date range: {product_metrics['date'].min()} to {product_metrics['date'].max()}")
    log_message(f"  Total revenue: ${product_metrics['total_revenue'].sum():,.2f}")
    
    # Show top 5 products
    top_products = product_metrics.groupby('product_name')['total_revenue'].sum().nlargest(5)
    log_message("  Top 5 products by revenue:")
    for product, rev in top_products.items():
        log_message(f"    {product}: ${rev:,.2f}")
    
    return product_metrics


# ==============================================================================
# AGGREGATION FUNCTION 5: USER LIFETIME METRICS
# ==============================================================================

def create_user_lifetime_metrics(users_df, orders_df):
    """
    One row per user with lifetime statistics
    
    PURPOSE:
    - Customer segmentation (VIP, regular, at-risk)
    - Calculate customer lifetime value (LTV)
    - Identify customers for retention campaigns
    
    METRICS PER USER:
    - First order date
    - Last order date
    - Total orders (frequency)
    - Total revenue (monetary value)
    - Average order value
    - Days since last order (recency)
    - RFM segment (Champion, Loyal, At-Risk, Lost)
    
    RFM SCORING SYSTEM:
    R = Recency (how recently they bought)
      5 = Last 30 days (best)
      4 = 31-90 days
      3 = 91-180 days
      2 = 181-365 days
      1 = 365+ days (worst)
    
    F = Frequency (how often they buy)
      5 = 10+ orders (best)
      4 = 5-9 orders
      3 = 3-4 orders
      2 = 2 orders
      1 = 1 order (worst)
    
    M = Monetary (how much they spend)
      5 = $1000+ (best)
      4 = $500-999
      3 = $200-499
      2 = $50-199
      1 = <$50 (worst)
    
    SEGMENTS:
    - 555, 554, 544, 545 = Champion
    - 444, 434, 443 = Loyal
    - 111, 112, 121, 122 = Lost
    - 211, 212, 221, 222 = At Risk
    
    HOW TO ADD NEW METRIC:
    Example - Add "Favorite Product Category":
    1. Need product_category in order_items first
    2. Join orders with order_items
    3. Find most common category: user_metrics['favorite_category'] = orders.groupby('user_id')['category'].agg(lambda x: x.mode()[0])
    
    Args:
        users_df (DataFrame): User data
        orders_df (DataFrame): Order data
        
    Returns:
        DataFrame: User-level lifetime metrics
    """
    log_message("\n" + "="*60)
    log_message("CREATING: user_lifetime_metrics")
    log_message("="*60)
    
    if orders_df is None or users_df is None:
        log_message("⚠ Skipping - missing required data")
        return None
    
    log_message("  Calculating user metrics...")
    
    # GROUP BY user_id
    # This creates one row per user
    user_metrics = orders_df.groupby('user_id').agg({
        'time': ['min', 'max'],           # First and last order dates
        'order_id': 'nunique',             # Count of unique orders
        'total_price': ['sum', 'mean']     # Total and average spending
    }).reset_index()
    
    # Flatten column names
    user_metrics.columns = [
        'user_id',
        'first_order_date',
        'last_order_date', 
        'total_orders',
        'total_revenue',
        'avg_order_value'
    ]
    
    # Round monetary values
    user_metrics['total_revenue'] = user_metrics['total_revenue'].round(2)
    user_metrics['avg_order_value'] = user_metrics['avg_order_value'].round(2)
    
    # Calculate days since last order (BEFORE converting to formatted string)
    log_message("  Calculating recency...")
    today = pd.Timestamp(datetime.now().date())
    user_metrics['days_since_last_order'] = (today - user_metrics['last_order_date']).dt.days
    
    # Convert dates to DD/MM/YYYY HH:MM:SS format for output
    user_metrics['first_order_date'] = user_metrics['first_order_date'].dt.strftime(Config.DATE_FORMAT)
    user_metrics['last_order_date'] = user_metrics['last_order_date'].dt.strftime(Config.DATE_FORMAT)
    
    # RFM SCORING
    log_message("  Calculating RFM scores...")
    
    # R = Recency Score (1-5, where 5 is best/most recent)
    user_metrics['rfm_recency_score'] = pd.cut(
        user_metrics['days_since_last_order'],
        bins=[-1, 30, 90, 180, 365, float('inf')],
        labels=[5, 4, 3, 2, 1]
    ).fillna(1).astype(int)
    
    # F = Frequency Score (1-5, where 5 is best/most orders)
    user_metrics['rfm_frequency_score'] = pd.cut(
        user_metrics['total_orders'],
        bins=[0, 1, 2, 4, 9, float('inf')],
        labels=[1, 2, 3, 4, 5]
    ).fillna(1).astype(int)
    
    # M = Monetary Score (1-5, where 5 is best/highest spend)
    user_metrics['rfm_monetary_score'] = pd.cut(
        user_metrics['total_revenue'],
        bins=[0, 50, 200, 500, 1000, float('inf')],
        labels=[1, 2, 3, 4, 5]
    ).fillna(1).astype(int)
    
    # Combine RFM scores into single string (e.g., "555" = Champion)
    user_metrics['rfm_score'] = (
        user_metrics['rfm_recency_score'].astype(str) +
        user_metrics['rfm_frequency_score'].astype(str) +
        user_metrics['rfm_monetary_score'].astype(str)
    )
    
    # SEGMENT ASSIGNMENT
    log_message("  Assigning customer segments...")
    
    def assign_segment(rfm_score):
        """
        Assigns customer segment based on RFM score
        
        Logic:
        - Champions: High recency, high frequency, high monetary (555, 554, 544, 545, etc.)
        - Loyal: Good recency, high frequency (444, 434, 443, etc.)
        - Potential Loyalist: Medium recency, medium frequency
        - At Risk: Low recency, decent frequency
        - Lost: Very low recency, low frequency
        - Others: Everything else
        """
        r = int(rfm_score[0])  # Recency
        f = int(rfm_score[1])  # Frequency
        m = int(rfm_score[2])  # Monetary
        
        # Champion: Recent, frequent, high-value
        if r >= 4 and f >= 4 and m >= 4:
            return 'Champion'
        
        # Loyal: Recent, very frequent
        elif r >= 3 and f >= 4:
            return 'Loyal Customer'
        
        # Potential Loyalist: Recent, medium frequency
        elif r >= 3 and f >= 2:
            return 'Potential Loyalist'
        
        # At Risk: Not recent, but was frequent
        elif r <= 2 and f >= 3:
            return 'At Risk'
        
        # Lost: Not recent, infrequent
        elif r == 1 and f <= 2:
            return 'Lost'
        
        # Need Attention: Low on multiple dimensions
        elif r <= 2 and f <= 2:
            return 'Needs Attention'
        
        # New Customer: Only 1-2 orders, any recency
        elif f <= 2:
            return 'New Customer'
        
        else:
            return 'Regular'
    
    user_metrics['rfm_segment'] = user_metrics['rfm_score'].apply(assign_segment)
    
    # Merge with original user data
    if 'has_purchase_last_year' in users_df.columns:
        user_metrics = user_metrics.merge(
            users_df[['user_id', 'has_purchase_last_year', 'has_purchase_last_qtr']],
            on='user_id',
            how='left'
        )
    
    # Sort by total revenue (highest first)
    user_metrics = user_metrics.sort_values('total_revenue', ascending=False)
    
    log_message(f"✓ Created {len(user_metrics)} user records")
    log_message(f"  Total users: {len(user_metrics)}")
    log_message(f"  Total revenue (all users): ${user_metrics['total_revenue'].sum():,.2f}")
    log_message(f"  Average LTV per user: ${user_metrics['total_revenue'].mean():,.2f}")
    
    # Show segment distribution
    log_message("  Customer segment breakdown:")
    segment_counts = user_metrics['rfm_segment'].value_counts()
    for segment, count in segment_counts.items():
        pct = count / len(user_metrics) * 100
        log_message(f"    {segment}: {count} ({pct:.1f}%)")
    
    return user_metrics


# ==============================================================================
# AGGREGATION FUNCTION 6: PAGE ENGAGEMENT METRICS
# ==============================================================================

def create_page_engagement_metrics(pageviews_df, scrolls_df, clicks_df):
    """
    Daily engagement metrics for each page
    
    PURPOSE:
    - Identify high/low performing pages
    - UX optimization insights
    - Content effectiveness measurement
    
    METRICS PER PAGE PER DAY:
    - Total pageviews
    - Unique users who viewed
    - Average scroll depth (how far down page)
    - Total clicks on page
    - Sessions that included this page
    
    HOW TO ADD NEW METRIC:
    Example - Add "Average Time on Page":
    1. Calculate time between this pageview and next: 
       pageviews_df['time_on_page'] = next_page_time - current_page_time
    2. Group by page and calculate mean:
       page_metrics['avg_time_on_page'] = pageviews_df.groupby(['date', 'path'])['time_on_page'].mean()
    
    Args:
        pageviews_df (DataFrame): Pageview data
        scrolls_df (DataFrame): Scroll data
        clicks_df (DataFrame): Click data
        
    Returns:
        DataFrame: Page-level daily metrics
    """
    log_message("\n" + "="*60)
    log_message("CREATING: page_engagement_metrics")
    log_message("="*60)
    
    if pageviews_df is None:
        log_message("⚠ Skipping - missing pageview data")
        return None
    
    # Extract date from timestamp — format: DD/MM/YYYY HH:MM:SS
    pageviews_df['date'] = pageviews_df['time'].dt.strftime(Config.DATE_FORMAT)
    
    log_message("  Aggregating pageview data...")
    
    # GROUP BY: date + page path
    # METRIC 1: Total Pageviews
    pageviews_count = pageviews_df.groupby(['date', 'path'])['event_id'].count()
    
    # METRIC 2: Unique Users
    unique_users = pageviews_df.groupby(['date', 'path'])['user_id'].nunique()
    
    # METRIC 3: Sessions with this page
    sessions_count = pageviews_df.groupby(['date', 'path'])['session_id'].nunique()
    
    # Combine pageview metrics
    page_metrics = pd.DataFrame({
        'pageviews': pageviews_count,
        'unique_users': unique_users,
        'sessions_with_page': sessions_count
    }).reset_index()
    
    # METRIC 4: Average Scroll Depth
    # How far down the page do users scroll on average?
    log_message("  Adding scroll data...")
    if scrolls_df is not None:
        # Extract date from timestamp — format: DD/MM/YYYY HH:MM:SS
        scrolls_df['date'] = scrolls_df['time'].dt.strftime(Config.DATE_FORMAT)
        
        # Calculate average scroll percent per page per day
        avg_scroll = scrolls_df.groupby(['date', 'path'])['scroll_percent'].mean().reset_index()
        avg_scroll.columns = ['date', 'path', 'avg_scroll_depth']
        avg_scroll['avg_scroll_depth'] = avg_scroll['avg_scroll_depth'].round(2)
        
        # Merge scroll data
        page_metrics = page_metrics.merge(avg_scroll, 
                                         on=['date', 'path'], 
                                         how='left')
        page_metrics['avg_scroll_depth'] = page_metrics['avg_scroll_depth'].fillna(0)
    else:
        page_metrics['avg_scroll_depth'] = 0
    
    # METRIC 5: Total Clicks
    # How many clicks happened on this page?
    log_message("  Adding click data...")
    if clicks_df is not None:
        # Extract date from timestamp — format: DD/MM/YYYY HH:MM:SS
        clicks_df['date'] = clicks_df['time'].dt.strftime(Config.DATE_FORMAT)
        
        # Count clicks per page per day
        clicks_count = clicks_df.groupby(['date', 'path'])['event_id'].count().reset_index()
        clicks_count.columns = ['date', 'path', 'total_clicks']
        
        # Merge click data
        page_metrics = page_metrics.merge(clicks_count, 
                                         on=['date', 'path'], 
                                         how='left')
        page_metrics['total_clicks'] = page_metrics['total_clicks'].fillna(0).astype(int)
    else:
        page_metrics['total_clicks'] = 0
    
    # Sort by date and pageviews
    page_metrics = page_metrics.sort_values(['date', 'pageviews'], 
                                           ascending=[True, False])
    
    log_message(f"✓ Created {len(page_metrics)} page-day records")
    log_message(f"  Unique pages: {page_metrics['path'].nunique()}")
    log_message(f"  Total pageviews: {page_metrics['pageviews'].sum():,}")
    
    # Show top 5 pages
    top_pages = page_metrics.groupby('path')['pageviews'].sum().nlargest(5)
    log_message("  Top 5 pages by pageviews:")
    for path, views in top_pages.items():
        log_message(f"    {path}: {views:,} views")
    
    return page_metrics


# ==============================================================================
# AGGREGATION FUNCTION 7: COUPON PERFORMANCE
# ==============================================================================

def create_coupon_performance(orders_df):
    """
    Daily performance metrics for discount coupons
    
    PURPOSE:
    - Measure promotion effectiveness
    - Calculate ROI of discount campaigns
    - Identify popular coupons
    
    METRICS PER COUPON PER DAY:
    - Number of times used
    - Total discount amount given
    - Total revenue from orders with coupon
    - Average order value with coupon
    
    NOTE: Also creates summary for orders WITHOUT coupons (NULL coupon code)
    
    HOW TO ADD NEW METRIC:
    Example - Add "New vs Repeat Customer Usage":
    1. Need is_first_purchase field in orders first
    2. Count: coupon_metrics['new_customer_usage'] = orders[orders['is_first_purchase']==1].groupby('discount_coupon_code').size()
    
    Args:
        orders_df (DataFrame): Order data
        
    Returns:
        DataFrame: Coupon-level daily metrics
    """
    log_message("\n" + "="*60)
    log_message("CREATING: coupon_performance")
    log_message("="*60)
    
    if orders_df is None or 'discount_coupon_code' not in orders_df.columns:
        log_message("⚠ Skipping - missing order data or coupon field")
        return None
    
    # Extract date from timestamp — format: DD/MM/YYYY HH:MM:SS
    orders_df['date'] = orders_df['time'].dt.strftime(Config.DATE_FORMAT)
    
    # Fill NULL coupon codes with 'NO_COUPON'
    # WHY: Makes it clear these are orders without discounts
    orders_df['discount_coupon_code'] = orders_df['discount_coupon_code'].fillna('NO_COUPON')
    
    log_message("  Aggregating coupon data...")
    
    # GROUP BY: date + coupon code
    coupon_metrics = orders_df.groupby(['date', 'discount_coupon_code']).agg({
        'order_id': 'count',              # METRIC 1: Usage count
        'discount': 'sum',                # METRIC 2: Total discount given
        'total_price': ['sum', 'mean']    # METRIC 3 & 4: Revenue and AOV
    }).reset_index()
    
    # Flatten column names
    coupon_metrics.columns = [
        'date',
        'discount_coupon_code',
        'usage_count',
        'total_discount_given',
        'total_revenue',
        'avg_order_value'
    ]
    
    # Round monetary values
    coupon_metrics['total_discount_given'] = coupon_metrics['total_discount_given'].round(2)
    coupon_metrics['total_revenue'] = coupon_metrics['total_revenue'].round(2)
    coupon_metrics['avg_order_value'] = coupon_metrics['avg_order_value'].round(2)
    
    # Calculate discount percentage
    # What % of revenue was discount?
    # Formula: (total_discount / total_revenue) * 100
    coupon_metrics['discount_percentage'] = (
        coupon_metrics['total_discount_given'] / 
        coupon_metrics['total_revenue'] * 100
    ).round(2)
    
    # Sort by date and usage
    coupon_metrics = coupon_metrics.sort_values(['date', 'usage_count'], 
                                                ascending=[True, False])
    
    log_message(f"✓ Created {len(coupon_metrics)} coupon-day records")
    log_message(f"  Unique coupons: {coupon_metrics['discount_coupon_code'].nunique()}")
    log_message(f"  Total discount given: ${coupon_metrics['total_discount_given'].sum():,.2f}")
    log_message(f"  Total revenue with coupons: ${coupon_metrics['total_revenue'].sum():,.2f}")
    
    # Show top coupons
    top_coupons = coupon_metrics.groupby('discount_coupon_code').agg({
        'usage_count': 'sum',
        'total_discount_given': 'sum'
    }).nlargest(5, 'usage_count')
    
    log_message("  Top 5 coupons by usage:")
    for idx, row in top_coupons.iterrows():
        log_message(f"    {idx}: {row['usage_count']} uses, ${row['total_discount_given']:,.2f} discount")
    
    return coupon_metrics


# ==============================================================================
# MAIN EXECUTION FUNCTION
# ==============================================================================

def save_to_csv(df, filename):
    """
    Saves DataFrame to CSV with error handling
    
    Args:
        df (DataFrame): Data to save
        filename (str): Output filename
    """
    if df is None or df.empty:
        log_message(f"⚠ Skipping save - {filename} has no data")
        return
    
    try:
        filepath = os.path.join(Config.AGGREGATED_DATA_DIR, filename)
        df.to_csv(filepath, index=False)
        log_message(f"✓ Saved: {filename} ({len(df)} rows)")
    except Exception as e:
        log_message(f"✗ Error saving {filename}: {str(e)}")


def main():
    """
    Main execution function - orchestrates entire pipeline
    
    WORKFLOW:
    1. Setup directories
    2. Load all raw data
    3. Create each aggregated table
    4. Save all aggregated tables
    5. Log summary
    
    TO RUN THIS SCRIPT:
    python ecommerce_data_processor.py
    
    TO SCHEDULE DAILY (Linux/Mac):
    crontab -e
    Add: 0 1 * * * /usr/bin/python3 /path/to/ecommerce_data_processor.py
    
    TO SCHEDULE DAILY (Windows):
    Use Task Scheduler to run this script at 1 AM daily
    """
    
    # Start timing
    start_time = datetime.now()
    
    log_message("\n" + "="*60)
    log_message("E-COMMERCE DATA AGGREGATION PIPELINE")
    log_message("="*60)
    log_message(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Setup
    Config.setup_directories()
    
    # STEP 1: Load all raw data
    data = load_all_raw_data()
    
    # Check if we have minimum required data
    if data['sessions'] is None or data['orders'] is None:
        log_message("\n✗ CRITICAL: Missing core data (sessions or orders)")
        log_message("Cannot continue without minimum required data")
        return
    
    # STEP 2: Create aggregated tables
    
    # Table 1: Daily Business Metrics
    daily_metrics = create_daily_business_metrics(
        data['orders'], 
        data['sessions'], 
        data['users']
    )
    
    # Table 2: Session Attribution
    session_attr = create_session_attribution(
        data['sessions'], 
        data['orders']
    )
    
    # Table 3: Session Funnel
    funnel = create_session_funnel(
        data['sessions'],
        data['pageviews'],
        data['cart'],
        data['orders']
    )
    
    # Table 4: Product Performance
    product_perf = create_product_performance_daily(
        data['order_items'],
        data['cart'],
        data['pageviews']
    )
    
    # Table 5: User Lifetime Metrics
    user_ltv = create_user_lifetime_metrics(
        data['users'],
        data['orders']
    )
    
    # Table 6: Page Engagement
    page_engagement = create_page_engagement_metrics(
        data['pageviews'],
        data['scrolls'],
        data['clicks']
    )
    
    # Table 7: Coupon Performance
    coupon_perf = create_coupon_performance(
        data['orders']
    )
    
    # STEP 3: Save all aggregated tables
    log_message("\n" + "="*60)
    log_message("SAVING AGGREGATED TABLES")
    log_message("="*60)
    
    save_to_csv(daily_metrics, 'daily_business_metrics.csv')
    save_to_csv(session_attr, 'session_attribution.csv')
    save_to_csv(funnel, 'session_funnel.csv')
    save_to_csv(product_perf, 'product_performance_daily.csv')
    save_to_csv(user_ltv, 'user_lifetime_metrics.csv')
    save_to_csv(page_engagement, 'page_engagement_metrics.csv')
    save_to_csv(coupon_perf, 'coupon_performance.csv')
    
    # STEP 4: Summary
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    log_message("\n" + "="*60)
    log_message("PIPELINE COMPLETE")
    log_message("="*60)
    log_message(f"End time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    log_message(f"Duration: {duration:.2f} seconds")
    log_message(f"\nAggregated files saved to: {Config.AGGREGATED_DATA_DIR}")
    log_message("="*60)


# ==============================================================================
# RUN THE SCRIPT
# ==============================================================================

if __name__ == "__main__":
    """
    This runs when you execute: python ecommerce_data_processor.py
    """
    main()