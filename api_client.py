import yfinance as yf
from datetime import datetime, timedelta, date
import pandas as pd
from db_cache import get_cached_data, cache_stock_data, is_data_fresh

def get_yesterday_date():
    """Get yesterday's date (accounting for weekends)"""
    yesterday = datetime.now() - timedelta(days=1)
    # If yesterday is Saturday, use Friday; if Sunday, use Friday
    if yesterday.weekday() == 5:  # Saturday
        yesterday -= timedelta(days=1)
    elif yesterday.weekday() == 6:  # Sunday
        yesterday -= timedelta(days=2)
    return yesterday.date()

def get_today_date():
    """Get today's date"""
    return datetime.now().date()

def get_trading_days_before(target_date, days=1):
    """Get previous trading day accounting for weekends"""
    result_date = target_date - timedelta(days=days)
    
    # Adjust for weekends
    while result_date.weekday() >= 5:  # Saturday or Sunday
        result_date -= timedelta(days=1)
    
    return result_date

def get_stock_data(ticker, start_date=None, end_date=None, use_cache=True):
    """
    Fetch historical stock data for a given ticker
    
    Args:
        ticker: Stock ticker symbol
        start_date: Start date (default: Jan 1 of current year)
        end_date: End date (default: today)
        use_cache: Whether to check cache first
    
    Returns:
        DataFrame with stock data or None if error
    """
    if start_date is None:
        start_date = datetime(datetime.now().year, 1, 1)
    if end_date is None:
        end_date = datetime.now()
    
    # Check cache first if enabled
    if use_cache:
        cache_key_date = end_date.date() if isinstance(end_date, datetime) else end_date
        cached_data = get_cached_data(ticker, cache_key_date)
        if cached_data and is_data_fresh(ticker, cache_key_date):
            # Return cached data as DataFrame
            if 'data_dict' in cached_data and 'index' in cached_data:
                try:
                    df = pd.DataFrame(cached_data['data_dict'])
                    df.index = pd.to_datetime(cached_data['index'])
                    return df
                except Exception as e:
                    print(f"Warning: Could not reconstruct cached data for {ticker}: {e}")
    
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(start=start_date, end=end_date)
        
        # Cache the data if successful
        if use_cache and not data.empty:
            cache_key_date = end_date.date() if isinstance(end_date, datetime) else end_date
            # Store DataFrame in a way that can be reconstructed
            cache_data = {
                'data_dict': data.to_dict('list'),  # Store as dict of lists
                'index': [str(idx) for idx in data.index],  # Store index as strings
                'start_date': start_date.isoformat() if isinstance(start_date, datetime) else str(start_date),
                'end_date': end_date.isoformat() if isinstance(end_date, datetime) else str(end_date)
            }
            cache_stock_data(ticker, cache_key_date, cache_data)
        
        return data
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return None

def get_price_data(ticker):
    """
    Get price data for a stock
    
    Returns:
        dict with:
        - yesterday_price: Closing price yesterday
        - today_price: Closing price today
        - ytd_high: Highest price from Jan 1 to yesterday (or earliest available)
        - data_start_date: Actual start date of available data
        - success: Boolean indicating if data was fetched successfully
        - error_message: String describing any issues
    """
    try:
        # Get data from start of year to today
        start_date = datetime(datetime.now().year, 1, 1)
        end_date = datetime.now()
        
        data = get_stock_data(ticker, start_date, end_date)
        
        if data is None or data.empty:
            return {
                'success': False, 
                'error_message': 'No data available from API'
            }
        
        # Get yesterday and today dates
        yesterday = get_yesterday_date()
        today = get_today_date()
        
        # Convert index to date if it's datetime
        if len(data) > 0 and isinstance(data.index[0], pd.Timestamp):
            data.index = data.index.date
        
        # Get yesterday's closing price
        yesterday_data = data[data.index == yesterday] if yesterday in data.index else pd.DataFrame()
        
        if yesterday_data.empty:
            # Try to get the most recent trading day before today
            trading_days = data[data.index < today] if today in data.index else data
            if trading_days.empty:
                return {
                    'success': False, 
                    'error_message': 'No historical data available'
                }
            yesterday_price = trading_days['Close'].iloc[-1]
            yesterday = trading_days.index[-1]
        else:
            yesterday_price = yesterday_data['Close'].iloc[0]
        
        # Get today's closing price
        today_data = data[data.index == today] if today in data.index else pd.DataFrame()
        if today_data.empty:
            # Use the most recent available price
            today_price = data['Close'].iloc[-1]
            today = data.index[-1]
        else:
            today_price = today_data['Close'].iloc[0]
        
        # Calculate YTD high (from data start to yesterday)
        ytd_data = data[data.index <= yesterday] if yesterday in data.index else data
        if ytd_data.empty:
            ytd_high = yesterday_price
        else:
            ytd_high = ytd_data['High'].max()
        
        # Get actual data start date
        data_start_date = data.index[0] if len(data) > 0 else start_date.date()
        
        # Check if we have full year of data
        full_year_data = data_start_date <= date(datetime.now().year, 1, 1)
        
        return {
            'success': True,
            'yesterday_price': float(yesterday_price),
            'today_price': float(today_price),
            'ytd_high': float(ytd_high),
            'yesterday_date': yesterday,
            'today_date': today,
            'data_start_date': data_start_date,
            'full_year_data': full_year_data
        }
    except Exception as e:
        return {
            'success': False, 
            'error_message': f'Error processing data: {str(e)}'
        }

