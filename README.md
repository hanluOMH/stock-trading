# Stock Check Tool

A Python tool to identify stocks that:
1. Dropped 40% or more from their year-to-date high (as of yesterday)
2. Increased 5% or more today (compared to yesterday)

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the program:
```bash
python main.py
```

## How it works

1. Fetches S&P 500 and NASDAQ 100 stock ticker lists from Wikipedia
2. For each stock, retrieves historical data from Yahoo Finance (using yfinance)
3. Uses SQLite database cache to avoid repeated API calls
4. Calculates the drop from year-to-date high
5. Filters stocks that dropped >= 40% from high
6. Checks today's price increase
7. Filters stocks that increased >= 5% today
8. Displays results and saves to CSV

## Database Caching

The tool uses SQLite database (`stock_cache.db`) to cache stock data and avoid repeated API calls:

- **Cache Key**: (ticker, date) combination
- **Cache Expiry**: Data is considered fresh if cached on the same day
- **Automatic Cleanup**: Old cache entries (default: 7 days) can be cleaned up
- **Benefits**: 
  - Reduces API rate limiting issues
  - Faster subsequent runs
  - Lower network usage

The cache is automatically checked before making API calls and updated after successful data retrieval.

## Edge Case Handling

- **Market Holidays**: Automatically skips non-trading days, uses previous trading day
- **Stocks without full year of data**: Uses available data range, calculates YTD high from earliest available date, logs warning
- **Missing data points**: Skips stocks with missing critical data (yesterday/today prices), logs error
- **Insufficient history**: Warns if stock has less than 6 months of data, but still processes if minimum data available
- **Invalid tickers**: Skips gracefully, logs error

## Output

Results are displayed in the console and saved to a CSV file with timestamp (e.g., `stock_results_20240101_120000.csv`).

The CSV includes:
- Ticker symbol
- Yesterday's price
- Today's price
- Year-to-date high
- Drop percentage from high
- Increase percentage today
- Data quality indicators (full year data availability)

## Testing

To test with a smaller subset of stocks, modify `main.py`:

```python
results = analyze_stocks(
    drop_threshold=0.40,
    increase_threshold=0.05,
    max_stocks=50  # Test with first 50 stocks
)
```

## Requirements

- Python 3.7+
- yfinance>=0.2.0
- pandas>=1.5.0
- requests>=2.28.0
- beautifulsoup4>=4.11.0

