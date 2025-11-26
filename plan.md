# Stock Analysis Tool Implementation Plan

## Overview

Build a Python tool that identifies stocks from S&P 500 and NASDAQ 100 that:

1. Dropped 40% or more from their year-to-date high (as of yesterday)
2. Increased 5% or more today (compared to yesterday)

## File Structure

```
StockCheckTool/
├── main.py              # Entry point and orchestration
├── api_client.py         # Yahoo Finance API wrapper (yfinance)
├── stock_lists.py        # Functions to fetch S&P 500 and NASDAQ 100 tickers
├── stock_analyzer.py     # Core analysis logic
├── db_cache.py          # SQLite database for caching stock data
├── requirements.txt      # Python dependencies
└── README.md            # Documentation
```

## Implementation Details

### 1. requirements.txt

- yfinance>=0.2.0 (Yahoo Finance API)
- pandas>=1.5.0 (Data manipulation)
- requests>=2.28.0 (Web scraping for ticker lists)
- beautifulsoup4>=4.11.0 (HTML parsing)
- sqlite3 (built-in Python module, no install needed)

### 2. stock_lists.py

- `get_sp500_tickers()`: Scrape S&P 500 tickers from Wikipedia
- `get_nasdaq100_tickers()`: Scrape NASDAQ 100 tickers from Wikipedia
- `get_all_tickers()`: Combine both lists, remove duplicates

### 3. db_cache.py

- `init_database()`: Initialize SQLite database and create tables
- `get_cached_data(ticker, date)`: Retrieve cached stock data from database
- `cache_stock_data(ticker, date, data)`: Store stock data in database
- `is_data_fresh(ticker, date)`: Check if cached data is still valid (same day)
- `clear_old_cache(days=7)`: Remove cache entries older than specified days
- Database schema:
  - Table: stock_data
  - Columns: ticker (TEXT), date (DATE), data_json (TEXT), cached_at (TIMESTAMP)
  - Index on (ticker, date) for fast lookups

### 4. api_client.py

- `get_stock_data(ticker, start_date, end_date)`: Fetch historical data using yfinance (check cache first)
- `get_yesterday_date()`: Get most recent trading day (handle weekends and holidays)
- `get_price_data(ticker)`: Returns dict with:
  - yesterday_price: Closing price from most recent trading day
  - today_price: Current/latest closing price
  - ytd_high: Max high price from available data (Jan 1→yesterday, or earliest available)
  - success: Boolean flag for error handling
  - error_message: String if missing/insufficient data
- Error handling:
  - Market holidays: Use previous trading day when no data
  - Missing data points: Skip if critical data missing
  - Insufficient history: Use available range and log warning
  - Cache integration: Read from cache before API call; write after success

### 5. stock_analyzer.py

- `calculate_drop_from_high(year_high, current_price)`: Percentage drop
- `calculate_daily_increase(yesterday_price, today_price)`: Daily percentage change
- `analyze_stocks(drop_threshold=0.40, increase_threshold=0.05, max_stocks=None)`:
  - Initialize database cache
  - Fetch S&P 500 and NASDAQ 100 tickers
  - For each ticker: use cache or fetch data, then validate
  - Filter: drop >= 40% from YTD high
  - Filter: increase >= 5% today
  - Return matches with metrics

### 6. main.py

- `format_results(results)`: Pretty print and CSV export
- `main()`: Orchestrate thresholds, run analysis, output results

### 7. README.md

- Setup, usage, criteria description, and cache behavior

## Key Implementation Notes

- Handle weekends/holidays by using the most recent trading day
- Robust error handling for API failures and invalid/missing data
- Progress indicators for long runs
- CSV export with timestamp
- Database caching (SQLite `stock_cache.db`):
  - Cache key: (ticker, date)
  - Check cache before API to reduce calls/rate limits
  - Cache expires end-of-day; refresh next trading day
  - Cleanup routine to remove entries older than N days (default 7)

## Algorithm Flow

1. Initialize SQLite cache
2. Fetch S&P 500 and NASDAQ 100 tickers
3. For each ticker:

   - Try cache for today's context; if stale/missing, fetch with yfinance and cache
   - If no trading today (holiday/weekend), use previous trading day
   - Validate presence of yesterday and today prices; skip if missing
   - Compute YTD high from available data range
   - Compute drop; if >= 40%, keep as candidate

4. For candidates, compute today's increase; if >= 5%, keep
5. Print and save results; optional cache cleanup