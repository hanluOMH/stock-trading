import sqlite3
import json
from datetime import datetime, date, timedelta
import os

DB_NAME = 'stock_cache.db'

def init_database():
    """Initialize SQLite database and create tables"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stock_data (
            ticker TEXT NOT NULL,
            date DATE NOT NULL,
            data_json TEXT NOT NULL,
            cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (ticker, date)
        )
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_ticker_date 
        ON stock_data(ticker, date)
    ''')
    
    conn.commit()
    conn.close()

def get_cached_data(ticker, target_date):
    """Retrieve cached stock data from database"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT data_json, cached_at 
        FROM stock_data 
        WHERE ticker = ? AND date = ?
    ''', (ticker, target_date))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return json.loads(result[0])
    return None

def cache_stock_data(ticker, target_date, data):
    """Store stock data in database"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    data_json = json.dumps(data)
    
    cursor.execute('''
        INSERT OR REPLACE INTO stock_data (ticker, date, data_json, cached_at)
        VALUES (?, ?, ?, ?)
    ''', (ticker, target_date, data_json, datetime.now()))
    
    conn.commit()
    conn.close()

def is_data_fresh(ticker, target_date):
    """Check if cached data is still valid (same day)"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT cached_at 
        FROM stock_data 
        WHERE ticker = ? AND date = ?
    ''', (ticker, target_date))
    
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        return False
    
    cached_at = datetime.fromisoformat(result[0])
    today = datetime.now().date()
    
    # Data is fresh if cached today
    return cached_at.date() == today

def clear_old_cache(days=7):
    """Remove cache entries older than specified days"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cutoff_date = datetime.now().date() - timedelta(days=days)
    
    cursor.execute('''
        DELETE FROM stock_data 
        WHERE date < ?
    ''', (cutoff_date,))
    
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    
    return deleted

