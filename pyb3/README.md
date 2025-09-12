# pyb3

## Overview

[B3](https://www.b3.com.br) is the main financial exchange in Brazil, offering access to trading systems for stocks, futures, options, and other financial instruments. The `pyb3` package provides tools for downloading, processing, and analyzing market data from B3, including:

- **Stocks & Equities**: Historical price data through COTAHIST files
- **Futures Contracts**: Settlement prices for futures contracts
- **Yield Curves**: Historical yield curves calculated from futures contracts
- **ETFs & BDRs**: Data for Exchange Traded Funds and Brazilian Depositary Receipts
- **REITs (FIIs)**: Data for Brazilian Real Estate Investment Trusts
- **Options**: Equity and index options contracts
- **Market Indices**: B3 indices composition and historical data

The package uses webscraping tools to obtain data directly from [B3's website](https://www.b3.com.br), making it accessible in Python as structured datasets. These datasets are valuable for financial analysis, academic research, and investment decision-making.

## Installation

```bash
# From PyPI (once published)
pip install pyb3

# Development version from GitHub
pip install git+https://github.com/PedroDnT/ybovevespa.git
```
## Basic Usage

### Bootstrapping

Start by bootstrapping the package to create the necessary directory structure and copy template files:

```python
import pyb3

# Bootstrap the package
pyb3.bootstrap()

# Set the cache directory (optional)
pyb3.set_cache_dir("/path/to/your/custom/folder")
```

### Downloading Data

Execute the following code to download data you need to start working with `pyb3`:

```python
import pyb3
import pandas as pd
from datetime import date

# Download COTAHIST data for a specific date
pyb3.download_marketdata('cotahist_daily', date='2023-01-10')

# Fetch COTAHIST data (download + read)
df = pyb3.fetch_marketdata('cotahist_daily', date='2023-01-10')

# Download yearly COTAHIST data
pyb3.download_marketdata('cotahist_yearly', year='2022')
```

### Using Specialized Scrapers

```python
# Get equity data from COTAHIST
equity_df = pyb3.cotahist_get(date='2023-01-10')

# Get futures data
futures_df = pyb3.futures_get()

# Get yield curve data
yc_df = pyb3.yc_brl_get()

# Get indexes data
indexes_df = pyb3.indexes_get()

# Get indexes composition
indexes_comp_df = pyb3.indexes_composition_get()
```

### Working with Templates

```python
# List available templates
templates = pyb3.list_templates()

# Retrieve a template
template = pyb3.template_retrieve('cotahist_daily')

# Print template information
print(f"Template name: {template.name}")
print(f"Template description: {template.description}")
print(f"Number of fields: {len(template.fields)}")
```

## Examples

The package includes several example scripts in the `examples` directory:

- `basic_usage.py`: Basic usage of the package
- `template_usage.py`: Working with templates
- `custom_template.py`: Creating custom templates
- `custom_scraper.py`: Creating custom scrapers

## Advanced Usage
business_days = calendar.bizdays("2018-01-01", date.today().strftime("%Y-%m-%d"))
pyb3.fetch_marketdata("b3-reference-rates", refdate=business_days, curve_name=["DIC", "DOC", "PRE"])

# Download indexes composition data
pyb3.fetch_marketdata("b3-indexes-composition")

# Download current portfolio for all indexes
pyb3.fetch_marketdata("b3-indexes-current-portfolio", index=pyb3.indexes_get(), throttle=True)

# Download theoretical portfolio for all indexes
pyb3.fetch_marketdata("b3-indexes-theoretical-portfolio", index=pyb3.indexes_get(), throttle=True)

# Download historical data for all indexes
pyb3.fetch_marketdata("b3-indexes-historical-data", index=pyb3.indexes_get(), year=range(2000, date.today().year + 1), throttle=True)
```

## License

MIT License