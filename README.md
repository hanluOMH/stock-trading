# Stock Analysis Tool

A Python tool to identify stocks that:
1. Dropped 40% or more from their year-to-date high (as of yesterday)
2. Increased 5% or more today (compared to yesterday)

Available as both a command-line tool and a web application!

## Setup

### Command Line Usage

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the program:
```bash
python main.py
```

### Web Application

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the FastAPI web server:
```bash
python app.py
# Or use uvicorn directly:
# uvicorn app:app --reload
```

3. Open your browser and visit:
```
http://localhost:8000
```

**FastAPI Features:**
- Interactive API documentation at `http://localhost:8000/docs` (Swagger UI)
- Alternative API docs at `http://localhost:8000/redoc` (ReDoc)
- Automatic request/response validation

The web interface allows you to:
- Adjust analysis parameters (drop threshold, increase threshold)
- View results in a beautiful table format
- Analyze stocks interactively

## Deployment

To deploy this application to a website, see [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions on deploying to:
- Replit (Easiest for beginners)
- Railway
- Render
- Heroku
- PythonAnywhere
- Fly.io
- DigitalOcean App Platform

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
- fastapi>=0.104.0 (for web application)
- uvicorn[standard]>=0.24.0 (for production deployment)
- jinja2>=3.1.0 (for templates)

