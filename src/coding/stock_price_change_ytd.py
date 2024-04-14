# filename: stock_price_change_ytd.py
import yfinance as yf
from datetime import datetime

def get_ytd_price_change(ticker):
    # Get the current year
    current_year = datetime.now().year
    # Create a date string for the start of the year
    start_date = f"{current_year}-01-01"
    # Get the current date in the appropriate format
    end_date = datetime.now().strftime('%Y-%m-%d')
    
    # Fetch data from Yahoo Finance
    data = yf.download(ticker, start=start_date, end=end_date)
    
    # Calculate the percentage change from the first available closing price to the latest
    if not data.empty:
        initial_price = data['Close'].iloc[0]
        final_price = data['Close'].iloc[-1]
        return ((final_price - initial_price) / initial_price) * 100
    else:
        return "No data available"

# Tickers for NVIDIA and Tesla
tickers = ["NVDA", "TSLA"]

# Get YTD price change for each ticker
for ticker in tickers:
    change = get_ytd_price_change(ticker)
    print(f"{ticker} YTD price change: {change:.2f}%")
