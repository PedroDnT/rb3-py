"""Basic usage examples for pyb3 package."""

import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date, timedelta

import pyb3
from pyb3.scrapers import (
    cotahist_get, cotahist_filter_equity,
    futures_get,
    yc_brl_get,
    indexes_get
)

# Set cache directory (optional)
# pyb3.set_cache_dir('/path/to/cache')

# Get current cache directory
print(f"Cache directory: {pyb3.get_cache_dir()}")

# Download and get COTAHIST data for a specific date
print("\nDownloading COTAHIST data...")
today = date.today()
yesterday = today - timedelta(days=1)

# Get COTAHIST data for yesterday
cotahist_df = pyb3.fetch_marketdata('cotahist_daily', date=yesterday.strftime('%Y-%m-%d'))
print(f"COTAHIST data shape: {cotahist_df.shape}")

# Filter for equities only
equities_df = cotahist_filter_equity(cotahist_df)
print(f"Equities data shape: {equities_df.shape}")

# Get top 10 equities by volume
top_equities = equities_df.sort_values('volume', ascending=False).head(10)
print("\nTop 10 equities by volume:")
print(top_equities[['symbol', 'name', 'close', 'volume']])

# Get futures data
print("\nDownloading futures data...")
futures_df = pyb3.fetch_marketdata('futures_settlement_prices', date=yesterday.strftime('%Y-%m-%d'))
print(f"Futures data shape: {futures_df.shape}")

# Get DOL futures
dol_futures = futures_get(date=yesterday, ticker='DOL')
print("\nDOL futures:")
print(dol_futures[['maturity', 'settlement_price', 'variation']])

# Get yield curve data
print("\nDownloading yield curve data...")
yc_df = pyb3.fetch_marketdata('reference_rates', date=yesterday.strftime('%Y-%m-%d'))
print(f"Yield curve data shape: {yc_df.shape}")

# Get BRL yield curve
brl_yc = yc_brl_get(date=yesterday)
print("\nBRL yield curve:")
print(brl_yc[['days', 'r_252']])

# Plot yield curve
plt.figure(figsize=(10, 6))
plt.plot(brl_yc['days'], brl_yc['r_252'] * 100, marker='o')
plt.title(f'BRL Yield Curve - {yesterday}')
plt.xlabel('Days')
plt.ylabel('Rate (% p.a.)')
plt.grid(True)
plt.savefig('brl_yield_curve.png')
plt.close()

# Get indexes data
print("\nDownloading indexes data...")
indexes_df = pyb3.fetch_marketdata('indexes_historical_data', date=yesterday.strftime('%Y-%m-%d'))
print(f"Indexes data shape: {indexes_df.shape}")

# Get IBOV index
ibov = indexes_get(date=yesterday, index='IBOV')
print("\nIBOV index:")
print(ibov[['date', 'open', 'high', 'low', 'close']])

# Get indexes composition
print("\nDownloading indexes composition data...")
composition_df = pyb3.fetch_marketdata('indexes_composition', date=yesterday.strftime('%Y-%m-%d'))
print(f"Indexes composition data shape: {composition_df.shape}")

# Get IBOV composition
ibov_composition = pyb3.scrapers.indexes_composition_get(index='IBOV')
print("\nIBOV composition (top 10 by weight):")
print(ibov_composition.sort_values('weight', ascending=False).head(10)[['code', 'company', 'weight']])

# Plot IBOV composition (top 10 by weight)
top_ibov = ibov_composition.sort_values('weight', ascending=False).head(10)
plt.figure(figsize=(12, 6))
plt.bar(top_ibov['code'], top_ibov['weight'] * 100)
plt.title('IBOV Composition - Top 10 by Weight')
plt.xlabel('Stock')
plt.ylabel('Weight (%)')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('ibov_composition.png')
plt.close()

print("\nExamples completed. Check the current directory for generated plots.")