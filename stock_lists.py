import requests
from bs4 import BeautifulSoup
import pandas as pd

# Headers to avoid 403 Forbidden errors
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def get_sp500_tickers():
    """Fetch S&P 500 ticker symbols from Wikipedia"""
    try:
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', {'id': 'constituents'})
        
        if table:
            df = pd.read_html(str(table))[0]
            return df['Symbol'].tolist()
        else:
            print("Warning: Could not find S&P 500 table on Wikipedia")
            return []
    except Exception as e:
        print(f"Error fetching S&P 500 tickers: {e}")
        return []

def get_nasdaq100_tickers():
    """Fetch NASDAQ 100 ticker symbols from Wikipedia"""
    try:
        url = 'https://en.wikipedia.org/wiki/NASDAQ-100'
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', {'id': 'constituents'})
        
        if table:
            df = pd.read_html(str(table))[0]
            # NASDAQ 100 table might have 'Ticker' or 'Symbol' column
            if 'Ticker' in df.columns:
                return df['Ticker'].tolist()
            elif 'Symbol' in df.columns:
                return df['Symbol'].tolist()
            else:
                print("Warning: Could not find ticker column in NASDAQ 100 table")
                return []
        else:
            print("Warning: Could not find NASDAQ 100 table on Wikipedia")
            return []
    except Exception as e:
        print(f"Error fetching NASDAQ 100 tickers: {e}")
        return []

def get_all_tickers():
    """Get combined list of S&P 500 and NASDAQ 100 tickers (no duplicates)"""
    sp500 = get_sp500_tickers()
    nasdaq100 = get_nasdaq100_tickers()
    
    # Combine and remove duplicates while preserving order
    all_tickers = list(dict.fromkeys(sp500 + nasdaq100))
    
    return all_tickers

