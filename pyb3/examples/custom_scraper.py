"""Example of creating a custom scraper in pyb3 package."""

import os
import pandas as pd
from datetime import date, timedelta

import pyb3
from pyb3.download import download_marketdata, fetch_marketdata
from pyb3.read import read_marketdata

# Set cache directory (optional)
# pyb3.set_cache_dir('/path/to/cache')

# Bootstrap the package
pyb3.bootstrap()

# Define a custom scraper function
def custom_stock_get(date=None, symbol=None):
    """Custom scraper for stock data.
    
    Args:
        date (str or datetime.date, optional): Date to filter by
        symbol (str, optional): Symbol to filter by
        
    Returns:
        pandas.DataFrame: Filtered stock data
    """
    # Get COTAHIST data
    if date is None:
        date = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
    elif isinstance(date, date):
        date = date.strftime('%Y-%m-%d')
    
    # Fetch COTAHIST data
    df = pyb3.fetch_marketdata('cotahist_daily', date=date)
    
    # Filter for equities
    df = pyb3.scrapers.cotahist_filter_equity(df)
    
    # Filter by symbol if provided
    if symbol is not None:
        df = df[df['symbol'] == symbol.upper()]
    
    # Select relevant columns
    columns = ['refdate', 'symbol', 'name', 'open', 'high', 'low', 'close', 'volume']
    df = df[columns]
    
    return df

# Define a function to calculate moving averages
def calculate_moving_averages(df, window=5):
    """Calculate moving averages for stock data.
    
    Args:
        df (pandas.DataFrame): Stock data
        window (int, optional): Window size for moving average
        
    Returns:
        pandas.DataFrame: Stock data with moving averages
    """
    # Sort by date
    df = df.sort_values('refdate')
    
    # Calculate moving averages
    df[f'ma_{window}'] = df.groupby('symbol')['close'].transform(lambda x: x.rolling(window=window).mean())
    
    return df

# Use the custom scraper
print("Using custom stock scraper:")
yesterday = date.today() - timedelta(days=1)
stocks_df = custom_stock_get(date=yesterday)
print(f"\nStock data shape: {stocks_df.shape}")

# Print top 5 stocks by volume
top_stocks = stocks_df.sort_values('volume', ascending=False).head(5)
print("\nTop 5 stocks by volume:")
print(top_stocks[['symbol', 'name', 'close', 'volume']])

# Get data for a specific stock
print("\nGetting data for a specific stock:")
petr4_df = custom_stock_get(date=yesterday, symbol='PETR4')
print(petr4_df)

# Example of using the custom scraper with historical data
print("\nGetting historical data for a stock:")

# Create a list of dates (last 30 days)
end_date = date.today() - timedelta(days=1)
start_date = end_date - timedelta(days=30)
dates = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]

# Get data for each date
historical_data = []
for d in dates:
    try:
        df = custom_stock_get(date=d, symbol='PETR4')
        if not df.empty:
            historical_data.append(df)
    except Exception as e:
        print(f"Error getting data for {d}: {e}")

# Combine data
if historical_data:
    historical_df = pd.concat(historical_data)
    historical_df = historical_df.sort_values('refdate')
    
    # Calculate moving averages
    historical_df = calculate_moving_averages(historical_df, window=5)
    
    print("\nHistorical data with moving averages:")
    print(historical_df[['refdate', 'symbol', 'close', 'ma_5']].tail(10))
    
    # Save to CSV
    output_path = os.path.join(pyb3.get_cache_dir(), 'petr4_historical.csv')
    historical_df.to_csv(output_path, index=False)
    print(f"\nHistorical data saved to: {output_path}")
else:
    print("No historical data found.")

print("\nExample completed.")