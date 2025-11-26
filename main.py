from stock_analyzer import analyze_stocks
import pandas as pd
from datetime import datetime

def format_results(results):
    """Format and display results"""
    if not results:
        print("\nNo stocks found matching the criteria.")
        return
    
    # Create DataFrame for better display
    df_data = []
    for stock in results:
        df_data.append({
            'Ticker': stock['ticker'],
            'Yesterday Price': f"${stock['yesterday_price']:.2f}",
            'Today Price': f"${stock['today_price']:.2f}",
            'YTD High': f"${stock['ytd_high']:.2f}",
            'Drop from High': f"{stock['drop_from_high']*100:.2f}%",
            'Increase Today': f"{stock['increase_today']*100:.2f}%",
            'Yesterday Date': stock['yesterday_date'],
            'Today Date': stock['today_date'],
            'Full Year Data': 'Yes' if stock.get('full_year_data', True) else 'No',
            'Data Start': stock.get('data_start_date', 'N/A')
        })
    
    df = pd.DataFrame(df_data)
    print("\n" + df.to_string(index=False))
    
    # Save to CSV
    filename = f"stock_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    df.to_csv(filename, index=False)
    print(f"\nResults saved to: {filename}")

def main():
    print("Stock Analysis Tool")
    print("=" * 80)
    print("Criteria:")
    print("1. Stock dropped >= 40% from year-to-date high (as of yesterday)")
    print("2. Stock increased >= 5% today (compared to yesterday)")
    print("=" * 80)
    print()
    
    # Run analysis
    # You can limit stocks for testing: max_stocks=100
    results = analyze_stocks(
        drop_threshold=0.40,
        increase_threshold=0.05,
        max_stocks=None  # Set to None for all stocks, or a number for testing
    )
    
    # Display and save results
    format_results(results)

if __name__ == "__main__":
    main()

