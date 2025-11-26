from api_client import get_price_data
from stock_lists import get_all_tickers
from db_cache import init_database, clear_old_cache

def calculate_drop_from_high(year_high, current_price):
    """
    Calculate percentage drop from year high
    
    Args:
        year_high: Highest price of the year
        current_price: Current price (yesterday's price)
    
    Returns:
        Drop percentage (0.0 to 1.0)
    """
    if year_high == 0 or year_high is None:
        return 0.0
    return (year_high - current_price) / year_high

def calculate_daily_increase(yesterday_price, today_price):
    """
    Calculate percentage increase from yesterday to today
    
    Args:
        yesterday_price: Yesterday's closing price
        today_price: Today's closing price
    
    Returns:
        Increase percentage (can be negative)
    """
    if yesterday_price == 0 or yesterday_price is None:
        return 0.0
    return (today_price - yesterday_price) / yesterday_price

def validate_stock_data(price_data):
    """
    Validate data completeness
    
    Args:
        price_data: Dictionary from get_price_data()
    
    Returns:
        tuple: (is_valid: bool, error_message: str)
    """
    if not price_data.get('success', False):
        return False, price_data.get('error_message', 'Unknown error')
    
    # Check for critical data points
    if price_data.get('yesterday_price') is None:
        return False, 'Missing yesterday price'
    
    if price_data.get('today_price') is None:
        return False, 'Missing today price'
    
    if price_data.get('ytd_high') is None:
        return False, 'Missing YTD high'
    
    # Check if we have minimum required history (warn if < 6 months)
    data_start = price_data.get('data_start_date')
    if data_start:
        from datetime import datetime, date
        today = date.today()
        months_diff = (today.year - data_start.year) * 12 + (today.month - data_start.month)
        if months_diff < 6:
            return True, f'Warning: Only {months_diff} months of data available (less than 6 months)'
    
    return True, 'OK'

def analyze_stocks(drop_threshold=0.40, increase_threshold=0.05, max_stocks=None):
    """
    Main analysis function
    
    Args:
        drop_threshold: Minimum drop from year high (default: 0.40 = 40%)
        increase_threshold: Minimum increase today (default: 0.05 = 5%)
        max_stocks: Limit number of stocks to analyze (None for all)
    
    Returns:
        List of stocks matching criteria
    """
    # Initialize database cache
    init_database()
    
    print("Fetching stock ticker lists...")
    all_tickers = get_all_tickers()
    
    if not all_tickers:
        print("Error: Could not fetch ticker lists")
        return []
    
    if max_stocks:
        all_tickers = all_tickers[:max_stocks]
    
    print(f"Analyzing {len(all_tickers)} stocks...")
    print("=" * 80)
    
    # Step 1: Find stocks that dropped 40% from year high
    candidates = []
    processed = 0
    errors = 0
    warnings = 0
    
    for ticker in all_tickers:
        processed += 1
        if processed % 50 == 0:
            print(f"Processed {processed}/{len(all_tickers)} stocks...")
        
        price_data = get_price_data(ticker)
        
        # Validate data
        is_valid, validation_msg = validate_stock_data(price_data)
        
        if not is_valid:
            errors += 1
            if processed <= 10:  # Only log first few errors to avoid spam
                print(f"  Skipping {ticker}: {validation_msg}")
            continue
        
        if validation_msg.startswith('Warning'):
            warnings += 1
        
        drop_pct = calculate_drop_from_high(
            price_data['ytd_high'],
            price_data['yesterday_price']
        )
        
        if drop_pct >= drop_threshold:
            candidates.append({
                'ticker': ticker,
                'yesterday_price': price_data['yesterday_price'],
                'today_price': price_data['today_price'],
                'ytd_high': price_data['ytd_high'],
                'drop_from_high': drop_pct,
                'yesterday_date': price_data['yesterday_date'],
                'today_date': price_data['today_date'],
                'data_start_date': price_data.get('data_start_date'),
                'full_year_data': price_data.get('full_year_data', True),
                'warning': validation_msg if validation_msg.startswith('Warning') else None
            })
    
    print(f"\nFound {len(candidates)} stocks that dropped >= {drop_threshold*100}% from year high")
    if errors > 0:
        print(f"Skipped {errors} stocks due to missing data")
    if warnings > 0:
        print(f"Found {warnings} stocks with limited data history")
    print("=" * 80)
    
    # Step 2: Filter stocks with 5%+ increase today
    results = []
    
    for stock in candidates:
        increase_pct = calculate_daily_increase(
            stock['yesterday_price'],
            stock['today_price']
        )
        
        if increase_pct >= increase_threshold:
            stock['increase_today'] = increase_pct
            results.append(stock)
    
    print(f"\nFound {len(results)} stocks matching all criteria:")
    print(f"- Dropped >= {drop_threshold*100}% from year high")
    print(f"- Increased >= {increase_threshold*100}% today")
    print("=" * 80)
    
    # Optional: Clean up old cache entries
    # clear_old_cache(days=7)
    
    return results

