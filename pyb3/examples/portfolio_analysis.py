"""Example of portfolio analysis using pyb3 package."""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import date, timedelta

import pyb3

# Bootstrap the package
pyb3.bootstrap()

# Function to get historical data for a list of stocks
def get_historical_data(symbols, start_date, end_date):
    """Get historical data for a list of stocks.
    
    Args:
        symbols (list): List of stock symbols
        start_date (datetime.date): Start date
        end_date (datetime.date): End date
        
    Returns:
        dict: Dictionary with stock symbols as keys and DataFrames as values
    """
    stock_data = {}
    
    for symbol in symbols:
        data = []
        for d in [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]:
            try:
                df = pyb3.cotahist_get(date=d, symbol=symbol)
                if not df.empty:
                    data.append(df)
            except Exception:
                pass
        
        if data:
            stock_data[symbol] = pd.concat(data).sort_values('refdate')
    
    return stock_data

# Function to calculate portfolio statistics
def calculate_portfolio_stats(stock_data, weights=None):
    """Calculate portfolio statistics.
    
    Args:
        stock_data (dict): Dictionary with stock symbols as keys and DataFrames as values
        weights (dict, optional): Dictionary with stock symbols as keys and weights as values
        
    Returns:
        tuple: (returns_df, stats_dict)
    """
    # Calculate daily returns
    returns = {}
    for symbol, df in stock_data.items():
        if len(df) > 1:
            # Calculate daily returns
            df = df.sort_values('refdate')
            df['return'] = df['close'].pct_change()
            returns[symbol] = df
    
    # Create a DataFrame with all returns
    returns_df = pd.DataFrame({
        symbol: df['return'] for symbol, df in returns.items()
    })
    
    # Fill NaN values with 0
    returns_df = returns_df.fillna(0)
    
    # If weights are not provided, use equal weights
    if weights is None:
        weights = {symbol: 1/len(returns) for symbol in returns}
    
    # Calculate portfolio returns
    portfolio_returns = pd.Series(0, index=returns_df.index)
    for symbol in returns_df.columns:
        portfolio_returns += returns_df[symbol] * weights.get(symbol, 0)
    
    # Calculate statistics
    stats = {
        'mean_return': returns_df.mean() * 252,  # Annualized mean return
        'volatility': returns_df.std() * np.sqrt(252),  # Annualized volatility
        'sharpe_ratio': returns_df.mean() / returns_df.std() * np.sqrt(252),  # Annualized Sharpe ratio
        'correlation': returns_df.corr(),
        'portfolio_return': portfolio_returns.mean() * 252,  # Annualized portfolio return
        'portfolio_volatility': portfolio_returns.std() * np.sqrt(252),  # Annualized portfolio volatility
        'portfolio_sharpe_ratio': portfolio_returns.mean() / portfolio_returns.std() * np.sqrt(252) if portfolio_returns.std() > 0 else 0  # Annualized portfolio Sharpe ratio
    }
    
    return returns_df, stats

# Main script
print("Portfolio Analysis Example")

# Define portfolio
portfolio = {
    'PETR4': 0.2,  # 20% weight
    'VALE3': 0.2,  # 20% weight
    'ITUB4': 0.2,  # 20% weight
    'BBDC4': 0.2,  # 20% weight
    'ABEV3': 0.2   # 20% weight
}

# Define date range (last 60 days)
end_date = date.today() - timedelta(days=1)
start_date = end_date - timedelta(days=60)

print(f"\nAnalyzing portfolio from {start_date} to {end_date}")
print(f"Portfolio: {portfolio}")

# Get historical data
print("\nGetting historical data...")
stock_data = get_historical_data(list(portfolio.keys()), start_date, end_date)

# Calculate portfolio statistics
print("\nCalculating portfolio statistics...")
returns_df, stats = calculate_portfolio_stats(stock_data, portfolio)

# Print statistics
print("\nPortfolio Statistics:")
print(f"Annualized Return: {stats['portfolio_return']*100:.2f}%")
print(f"Annualized Volatility: {stats['portfolio_volatility']*100:.2f}%")
print(f"Annualized Sharpe Ratio: {stats['portfolio_sharpe_ratio']:.2f}")

print("\nIndividual Stock Statistics:")
for symbol in portfolio.keys():
    if symbol in stats['mean_return']:
        print(f"{symbol}:")
        print(f"  Annualized Return: {stats['mean_return'][symbol]*100:.2f}%")
        print(f"  Annualized Volatility: {stats['volatility'][symbol]*100:.2f}%")
        print(f"  Annualized Sharpe Ratio: {stats['sharpe_ratio'][symbol]:.2f}")

# Plot cumulative returns
plt.figure(figsize=(12, 8))

# Calculate cumulative returns
cumulative_returns = (1 + returns_df).cumprod()

# Add portfolio cumulative return
portfolio_returns = pd.Series(0, index=returns_df.index)
for symbol in returns_df.columns:
    portfolio_returns += returns_df[symbol] * portfolio.get(symbol, 0)
cumulative_returns['Portfolio'] = (1 + portfolio_returns).cumprod()

# Plot
plt.plot(cumulative_returns)
plt.title('Cumulative Returns')
plt.xlabel('Date')
plt.ylabel('Cumulative Return')
plt.legend(cumulative_returns.columns)
plt.grid(True)

# Save the figure
output_path = os.path.join(pyb3.get_cache_dir(), 'portfolio_analysis.png')
plt.savefig(output_path)
print(f"\nFigure saved to: {output_path}")

# Plot correlation matrix
plt.figure(figsize=(10, 8))
plt.imshow(stats['correlation'], cmap='coolwarm', vmin=-1, vmax=1)
plt.colorbar()
plt.xticks(range(len(stats['correlation'].columns)), stats['correlation'].columns, rotation=45)
plt.yticks(range(len(stats['correlation'].columns)), stats['correlation'].columns)
plt.title('Correlation Matrix')

# Add correlation values
for i in range(len(stats['correlation'].columns)):
    for j in range(len(stats['correlation'].columns)):
        plt.text(j, i, f"{stats['correlation'].iloc[i, j]:.2f}", ha='center', va='center', color='black')

# Save the correlation matrix figure
corr_output_path = os.path.join(pyb3.get_cache_dir(), 'correlation_matrix.png')
plt.savefig(corr_output_path)
print(f"Correlation matrix saved to: {corr_output_path}")

# Show the figures (comment out if running in a non-interactive environment)
# plt.show()

print("\nExample completed.")