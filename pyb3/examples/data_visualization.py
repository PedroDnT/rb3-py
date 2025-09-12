"""Example of data visualization using pyb3 package."""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import date, timedelta

import pyb3

# Bootstrap the package
pyb3.bootstrap()

# Set up the figure size
plt.figure(figsize=(12, 8))

# Example 1: Plotting yield curves
print("Plotting yield curves...")
try:
    # Get yield curve data
    yc_df = pyb3.yc_brl_get()
    
    # Filter for specific dates (last 4 available dates)
    dates = sorted(yc_df['refdate'].unique())[-4:]
    
    # Create subplot
    plt.subplot(2, 2, 1)
    
    # Plot each date's curve
    for d in dates:
        curve_data = yc_df[yc_df['refdate'] == d]
        plt.plot(curve_data['days'], curve_data['r_252'] * 100, label=d.strftime('%Y-%m-%d'))
    
    plt.title('Brazilian Yield Curves (PRE)')
    plt.xlabel('Days')
    plt.ylabel('Rate (%)')
    plt.legend()
    plt.grid(True)
    
    print(f"Plotted yield curves for dates: {[d.strftime('%Y-%m-%d') for d in dates]}")
except Exception as e:
    print(f"Error plotting yield curves: {e}")

# Example 2: Plotting stock prices
print("\nPlotting stock prices...")
try:
    # Get dates for the last 30 days
    end_date = date.today() - timedelta(days=1)
    start_date = end_date - timedelta(days=30)
    
    # Get data for selected stocks
    stocks = ['PETR4', 'VALE3', 'ITUB4']
    stock_data = {}
    
    for stock in stocks:
        data = []
        for d in [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]:
            try:
                df = pyb3.cotahist_get(date=d, symbol=stock)
                if not df.empty:
                    data.append(df)
            except Exception:
                pass
        
        if data:
            stock_data[stock] = pd.concat(data).sort_values('refdate')
    
    # Create subplot
    plt.subplot(2, 2, 2)
    
    # Plot each stock's closing price
    for stock, df in stock_data.items():
        if not df.empty:
            # Normalize to the first day's price
            first_price = df['close'].iloc[0]
            normalized_prices = df['close'] / first_price * 100
            plt.plot(df['refdate'], normalized_prices, label=stock)
    
    plt.title('Stock Price Performance (Normalized)')
    plt.xlabel('Date')
    plt.ylabel('Price (Normalized to 100)')
    plt.legend()
    plt.grid(True)
    
    print(f"Plotted stock prices for: {list(stock_data.keys())}")
except Exception as e:
    print(f"Error plotting stock prices: {e}")

# Example 3: Plotting futures term structure
print("\nPlotting futures term structure...")
try:
    # Get futures data
    futures_df = pyb3.futures_get(ticker='DI1')
    
    # Get the latest date
    latest_date = futures_df['refdate'].max()
    
    # Filter for the latest date
    latest_df = futures_df[futures_df['refdate'] == latest_date]
    
    # Create subplot
    plt.subplot(2, 2, 3)
    
    # Plot the term structure
    plt.plot(latest_df['maturity'], latest_df['settlement_price'])
    plt.scatter(latest_df['maturity'], latest_df['settlement_price'], color='red')
    
    plt.title(f'DI1 Futures Term Structure ({latest_date.strftime("%Y-%m-%d")})')
    plt.xlabel('Maturity')
    plt.ylabel('Settlement Price')
    plt.grid(True)
    
    print(f"Plotted futures term structure for {latest_date.strftime('%Y-%m-%d')}")
except Exception as e:
    print(f"Error plotting futures term structure: {e}")

# Example 4: Plotting index performance
print("\nPlotting index performance...")
try:
    # Get indexes data
    indexes_df = pyb3.indexes_get()
    
    # Filter for main indexes
    main_indexes = ['IBOV', 'IBXX', 'SMLL']
    filtered_df = indexes_df[indexes_df['index'].isin(main_indexes)]
    
    # Create subplot
    plt.subplot(2, 2, 4)
    
    # Plot each index
    for idx in main_indexes:
        idx_data = filtered_df[filtered_df['index'] == idx]
        if not idx_data.empty:
            # Normalize to the first day's value
            idx_data = idx_data.sort_values('date')
            first_value = idx_data['close'].iloc[0]
            normalized_values = idx_data['close'] / first_value * 100
            plt.plot(idx_data['date'], normalized_values, label=idx)
    
    plt.title('Index Performance (Normalized)')
    plt.xlabel('Date')
    plt.ylabel('Value (Normalized to 100)')
    plt.legend()
    plt.grid(True)
    
    print(f"Plotted index performance for: {main_indexes}")
except Exception as e:
    print(f"Error plotting index performance: {e}")

# Adjust layout and save figure
plt.tight_layout()

# Save the figure
output_path = os.path.join(pyb3.get_cache_dir(), 'data_visualization.png')
plt.savefig(output_path)
print(f"\nFigure saved to: {output_path}")

# Show the figure (comment out if running in a non-interactive environment)
# plt.show()

print("\nExample completed.")