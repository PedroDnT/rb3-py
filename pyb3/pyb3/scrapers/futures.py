"""Futures scraper for B3 data.

This module provides functions to retrieve and process futures data from B3.
"""

import os
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.dataset as ds

from .. import get_cache_dir

def futures_get(ticker=None):
    """Get futures data.
    
    Args:
        ticker (str): Futures ticker (e.g., 'DI1', 'DOL', 'IND')
        
    Returns:
        pyarrow.dataset.Dataset: Dataset with futures data
    """
    cache_dir = Path(get_cache_dir())
    template_id = "b3-futures-settlement-prices"
    db_dir = cache_dir / 'db' / template_id / 'futures'
    
    if not db_dir.exists():
        raise ValueError(f"Futures data not found. Please download it first using fetch_marketdata().")
    
    dataset = ds.dataset(str(db_dir), format='parquet')
    
    if ticker:
        return dataset.filter(ds.field('ticker') == ticker)
    
    return dataset