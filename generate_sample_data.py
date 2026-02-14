"""
SAMPLE DATA GENERATOR
=====================

PURPOSE:
Generates realistic sample e-commerce data for testing the aggregation system.

WHAT IT CREATES:
- 8 CSV files with sample data
- Realistic relationships between tables
- Covers various scenarios (purchases, cart abandonment, browsing)

HOW TO USE:
1. Run this script: python generate_sample_data.py
2. It will create sample CSVs in raw_data/ folder
3. Then run: python ecommerce_data_processor.py
4. Check aggregated_data/ folder for results

MODIFY THIS TO:
- Change number of records generated
- Adjust data patterns
- Add new fields to test
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

# Configuration
NUM_USERS = 100
NUM_SESSIONS = 500
NUM_ORDERS = 150
OUTPUT_DIR = 'raw_data/'

# Sample data lists
COUNTRIES = ['US', 'UK', 'CA', 'AU', 'DE', 'FR', 'IN', 'JP']
DEVICES = ['iPhone', 'Samsung Galaxy', 'iPad', 'Desktop', 'MacBook', 'Android Phone']
PLATFORMS = ['mobile', 'desktop', 'tablet']
BROWSERS = ['Chrome', 'Safari', 'Firefox', 'Edge']
UTM_SOURCES = ['google', 'facebook', 'instagram', 'email', 'direct', 'twitter']
UTM_MEDIUMS = ['cpc', 'social', 'email', 'organic', 'referral']
CAMPAIGNS = ['summer_sale', 'black_friday', 'new_year', 'spring_promo', 'None']

PRODUCTS = [
    ('Blue Sneakers', 99.99),
    ('Red T-Shirt', 24.99),
    ('Black Jeans', 59.99),
    ('White Hoodie', 49.99),
    ('Gray Sweatpants', 39.99),
    ('Running Shoes', 119.99),
    ('Denim Jacket', 79.99),
    ('Cotton Socks', 9.99),
    ('Leather Belt', 34.99),
    ('Baseball Cap', 19.99),
    ('Winter Coat', 149.99),
    ('Yoga Pants', 44.99),
]

PAGES = [
    '/',
    '/category/clothing',
    '/category/shoes',
    '/category/accessories',
    '/product/blue-sneakers',
    '/product/red-tshirt',
    '/product/black-jeans',
    '/product/white-hoodie',
    '/product/running-shoes',
    '/cart',
    '/checkout',
    '/about',
    '/contact'
]

COUPON_CODES = ['SAVE10', 'SAVE20', 'WELCOME15', 'SUMMER25', None]


def generate_user_table():
    """Generate user_table.csv"""
    print("Generating user_table.csv...")
    
    users = []
    for i in range(1, NUM_USERS + 1):
        users.append({
            'user_id': f'user_{i:04d}',
            'has_purchase_last_year': random.choice([0, 0, 1]),  # 33% have purchased
            'has_purchase_last_qtr': random.choice([0, 0, 0, 1])  # 25% recent purchasers
        })
    
    df = pd.DataFrame(users)
    df.to_csv(os.path.join(OUTPUT_DIR, 'user_table.csv'), index=False)
    print(f"  ✓ Created {len(df)} users")


def generate_session_table():
    """Generate session_table.csv"""
    print("\nGenerating session_table.csv...")
    
    sessions = []
    start_date = datetime.now() - timedelta(days=30)
    
    for i in range(1, NUM_SESSIONS + 1):
        user_id = f'user_{random.randint(1, NUM_USERS):04d}'
        session_time = start_date + timedelta(
            days=random.randint(0, 30),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        
        utm_source = random.choice(UTM_SOURCES)
        
        sessions.append({
            'user_id': user_id,
            'session_id': f'sess_{i:05d}',
            'time': session_time.strftime('%Y-%m-%d %H:%M:%S'),
            'platform': random.choice(PLATFORMS),
            'device_type': random.choice(DEVICES),
            'country': random.choice(COUNTRIES),
            'region': 'CA' if random.random() > 0.5 else 'NY',
            'city': 'San Francisco' if random.random() > 0.5 else 'New York',
            'IP': f'{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}',
            'referrer': f'https://{utm_source}.com' if utm_source != 'direct' else '',
            'landing_page': random.choice(PAGES[:5]),
            'landing_page_query': f'?campaign={random.choice(CAMPAIGNS)}',
            'landing_page_hash': '',
            'browser': random.choice(BROWSERS),
            'utm_source': utm_source if utm_source != 'direct' else '',
            'utm_medium': random.choice(UTM_MEDIUMS) if utm_source != 'direct' else '',
            'utm_campaign': random.choice(CAMPAIGNS) if utm_source != 'direct' else ''
        })
    
    df = pd.DataFrame(sessions)
    df.to_csv(os.path.join(OUTPUT_DIR, 'session_table.csv'), index=False)
    print(f"  ✓ Created {len(df)} sessions")
    return df


def generate_pageview_table(sessions_df):
    """Generate pageview_table.csv"""
    print("\nGenerating pageview_table.csv...")
    
    pageviews = []
    event_id = 1
    
    for _, session in sessions_df.iterrows():
        # Each session has 2-8 pageviews
        num_pages = random.randint(2, 8)
        session_start = pd.to_datetime(session['time'])
        
        for page_num in range(num_pages):
            page_time = session_start + timedelta(minutes=page_num * random.randint(1, 3))
            
            pageviews.append({
                'event_id': f'pv_{event_id:06d}',
                'user_id': session['user_id'],
                'session_id': session['session_id'],
                'time': page_time.strftime('%Y-%m-%d %H:%M:%S'),
                'domain': 'myshop.com',
                'path': random.choice(PAGES),
                'hash': '',
                'query': '',
                'previous_page': PAGES[page_num-1] if page_num > 0 else session['landing_page']
            })
            event_id += 1
    
    df = pd.DataFrame(pageviews)
    df.to_csv(os.path.join(OUTPUT_DIR, 'pageview_table.csv'), index=False)
    print(f"  ✓ Created {len(df)} pageviews")
    return df


def generate_scroll_table(pageviews_df):
    """Generate scroll_table.csv"""
    print("\nGenerating scroll_table.csv...")
    
    # 70% of pageviews have scroll data
    sample_pageviews = pageviews_df.sample(frac=0.7)
    
    scrolls = []
    for _, pv in sample_pageviews.iterrows():
        pv_time = pd.to_datetime(pv['time'])
        scroll_time = pv_time + timedelta(seconds=random.randint(5, 30))
        
        scrolls.append({
            'event_id': f'sc_{pv["event_id"]}',
            'user_id': pv['user_id'],
            'session_id': pv['session_id'],
            'time': scroll_time.strftime('%Y-%m-%d %H:%M:%S'),
            'scroll_percent': random.choice([25, 50, 75, 100]),
            'domain': 'myshop.com',
            'path': pv['path'],
            'hash': '',
            'query': '',
            'previous_page': pv['previous_page']
        })
    
    df = pd.DataFrame(scrolls)
    df.to_csv(os.path.join(OUTPUT_DIR, 'scroll_table.csv'), index=False)
    print(f"  ✓ Created {len(df)} scroll events")


def generate_click_table(pageviews_df):
    """Generate click_table.csv"""
    print("\nGenerating click_table.csv...")
    
    # 50% of pageviews have clicks
    sample_pageviews = pageviews_df.sample(frac=0.5)
    
    clicks = []
    for _, pv in sample_pageviews.iterrows():
        pv_time = pd.to_datetime(pv['time'])
        click_time = pv_time + timedelta(seconds=random.randint(10, 60))
        
        clicks.append({
            'event_id': f'cl_{pv["event_id"]}',
            'user_id': pv['user_id'],
            'session_id': pv['session_id'],
            'time': click_time.strftime('%Y-%m-%d %H:%M:%S'),
            'domain': 'myshop.com',
            'path': pv['path'],
            'hash': '',
            'query': '',
            'href': random.choice(PAGES),
            'target_id': random.choice(['btn-primary', 'nav-link', 'product-card']),
            'target_tag': random.choice(['button', 'a', 'div']),
            'target_text': random.choice(['Add to Cart', 'View Details', 'Shop Now']),
            'previous_page': pv['previous_page']
        })
    
    df = pd.DataFrame(clicks)
    df.to_csv(os.path.join(OUTPUT_DIR, 'click_table.csv'), index=False)
    print(f"  ✓ Created {len(df)} click events")


def generate_add_to_cart_table(sessions_df):
    """Generate add_to_cart_table.csv"""
    print("\nGenerating add_to_cart_table.csv...")
    
    # 40% of sessions add to cart
    cart_sessions = sessions_df.sample(frac=0.4)
    
    cart_adds = []
    event_id = 1
    
    for _, session in cart_sessions.iterrows():
        # Each session adds 1-3 items
        num_items = random.randint(1, 3)
        session_start = pd.to_datetime(session['time'])
        
        for item_num in range(num_items):
            product = random.choice(PRODUCTS)
            add_time = session_start + timedelta(minutes=random.randint(5, 15))
            
            cart_adds.append({
                'event_id': f'cart_{event_id:05d}',
                'user_id': session['user_id'],
                'session_id': session['session_id'],
                'time': add_time.strftime('%Y-%m-%d %H:%M:%S'),
                'domain': 'myshop.com',
                'path': f'/product/{product[0].lower().replace(" ", "-")}',
                'hash': '',
                'query': '',
                'previous_page': '/category/clothing',
                'product_name': product[0],
                'product_price': product[1],
                'product_qty': random.choice([1, 1, 1, 2])
            })
            event_id += 1
    
    df = pd.DataFrame(cart_adds)
    df.to_csv(os.path.join(OUTPUT_DIR, 'add_to_cart_table.csv'), index=False)
    print(f"  ✓ Created {len(df)} cart additions")
    return df


def generate_order_table(sessions_df):
    """Generate order_table.csv"""
    print("\nGenerating order_table.csv...")
    
    # Select sessions that will result in orders
    # 30% conversion rate from sessions
    order_sessions = sessions_df.sample(n=NUM_ORDERS)
    
    orders = []
    for i, (_, session) in enumerate(order_sessions.iterrows(), 1):
        session_time = pd.to_datetime(session['time'])
        order_time = session_time + timedelta(minutes=random.randint(10, 30))
        
        # Random order values
        num_items = random.randint(1, 4)
        total_price = sum([random.choice(PRODUCTS)[1] for _ in range(num_items)])
        shipping_price = random.choice([0, 5.99, 9.99, 14.99])
        
        # 30% use coupons
        coupon = random.choice(COUPON_CODES) if random.random() < 0.3 else None
        discount = 0
        if coupon:
            if 'SAVE10' in str(coupon):
                discount = total_price * 0.10
            elif 'SAVE20' in str(coupon):
                discount = total_price * 0.20
            elif 'SAVE25' in str(coupon):
                discount = total_price * 0.25
            else:
                discount = 15.00
        
        orders.append({
            'event_id': f'ord_{i:05d}',
            'user_id': session['user_id'],
            'session_id': session['session_id'],
            'order_id': f'ORD-{i:06d}',
            'time': order_time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_price': round(total_price + shipping_price - discount, 2),
            'shipping_price': shipping_price,
            'discount': round(discount, 2),
            'discount_coupon_code': coupon if coupon else '',
            'total_items': num_items,
            'total_qty': num_items + random.randint(0, 2)
        })
    
    df = pd.DataFrame(orders)
    df.to_csv(os.path.join(OUTPUT_DIR, 'order_table.csv'), index=False)
    print(f"  ✓ Created {len(df)} orders")
    return df


def generate_order_line_item_table(orders_df):
    """Generate order_line_item_table.csv"""
    print("\nGenerating order_line_item_table.csv...")
    
    line_items = []
    event_id = 1
    
    for _, order in orders_df.iterrows():
        # Each order has 1-4 line items
        num_items = order['total_items']
        
        for item_num in range(num_items):
            product = random.choice(PRODUCTS)
            qty = random.choice([1, 1, 1, 2])
            
            line_items.append({
                'event_id': f'oli_{event_id:06d}',
                'user_id': order['user_id'],
                'session_id': order['session_id'],
                'order_id': order['order_id'],
                'time': order['time'],
                'product_name': product[0],
                'product_price': product[1],
                'product_qty': qty
            })
            event_id += 1
    
    df = pd.DataFrame(line_items)
    df.to_csv(os.path.join(OUTPUT_DIR, 'order_line_item_table.csv'), index=False)
    print(f"  ✓ Created {len(df)} order line items")


def main():
    """Generate all sample data files"""
    print("="*60)
    print("SAMPLE DATA GENERATOR")
    print("="*60)
    print(f"Creating sample e-commerce data...")
    print(f"Users: {NUM_USERS}")
    print(f"Sessions: {NUM_SESSIONS}")
    print(f"Orders: {NUM_ORDERS}")
    print("="*60)
    
    # Create output directory if needed
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Created directory: {OUTPUT_DIR}")
    
    # Generate all tables
    generate_user_table()
    sessions_df = generate_session_table()
    pageviews_df = generate_pageview_table(sessions_df)
    generate_scroll_table(pageviews_df)
    generate_click_table(pageviews_df)
    generate_add_to_cart_table(sessions_df)
    orders_df = generate_order_table(sessions_df)
    generate_order_line_item_table(orders_df)
    
    print("\n" + "="*60)
    print("SAMPLE DATA GENERATION COMPLETE!")
    print("="*60)
    print(f"Files created in: {OUTPUT_DIR}")
    print("\nNext steps:")
    print("1. Review the CSV files in raw_data/")
    print("2. Run: python ecommerce_data_processor.py")
    print("3. Check aggregated_data/ for results")
    print("="*60)


if __name__ == "__main__":
    main()
