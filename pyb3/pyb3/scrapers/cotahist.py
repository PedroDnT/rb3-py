"""COTAHIST scraper for B3 data.

This module provides functions to retrieve and process COTAHIST data from B3.
"""

import os
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.dataset as ds

from .. import get_cache_dir

def cotahist_get(frequency="yearly"):
    """Get COTAHIST data.
    
    Args:
        frequency (str): Data frequency ('yearly' or 'daily')
        
    Returns:
        pyarrow.dataset.Dataset: Dataset with COTAHIST data
    """
    cache_dir = Path(get_cache_dir())
    template_id = f"b3-cotahist-{frequency}"
    db_dir = cache_dir / 'db' / template_id / 'cotahist'
    
    if not db_dir.exists():
        raise ValueError(f"COTAHIST data not found for frequency '{frequency}'. Please download it first using fetch_marketdata().")
    
    return ds.dataset(str(db_dir), format='parquet')

def cotahist_filter_equity(dataset):
    """Filter COTAHIST data for equity instruments.
    
    Args:
        dataset: Dataset with COTAHIST data
        
    Returns:
        pyarrow.dataset.Dataset: Filtered dataset
    """
    return dataset.filter((ds.field('type') == 'EQUITY') | 
                         (ds.field('type') == 'ETF') | 
                         (ds.field('type') == 'BDR') | 
                         (ds.field('type') == 'UNIT'))

def cotahist_filter_options(dataset):
    """Filter COTAHIST data for options.
    
    Args:
        dataset: Dataset with COTAHIST data
        
    Returns:
        pyarrow.dataset.Dataset: Filtered dataset
    """
    return dataset.filter(ds.field('type') == 'OPTION')

def cotahist_filter_futures(dataset):
    """Filter COTAHIST data for futures.
    
    Args:
        dataset: Dataset with COTAHIST data
        
    Returns:
        pyarrow.dataset.Dataset: Filtered dataset
    """
    return dataset.filter(ds.field('type') == 'FUTURE')