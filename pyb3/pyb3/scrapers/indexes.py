"""Indexes scraper for B3 data.

This module provides functions to retrieve and process index data from B3.
"""

import os
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.dataset as ds

from .. import get_cache_dir

def indexes_get():
    """Get available indexes.
    
    Returns:
        list: List of available indexes
    """
    cache_dir = Path(get_cache_dir())
    template_id = "b3-indexes-composition"
    db_dir = cache_dir / 'db' / template_id / 'indexes'
    
    if not db_dir.exists():
        raise ValueError(f"Indexes data not found. Please download it first using fetch_marketdata().")
    
    dataset = ds.dataset(str(db_dir), format='parquet')
    df = dataset.to_table().to_pandas()
    
    return df['index'].unique().tolist()

def indexes_composition_get(index_name=None):
    """Get index composition.
    
    Args:
        index_name (str): Index name (e.g., 'IBOV', 'IBXX', 'SMLL')
        
    Returns:
        pyarrow.dataset.Dataset: Dataset with index composition
    """
    cache_dir = Path(get_cache_dir())
    template_id = "b3-indexes-composition"
    db_dir = cache_dir / 'db' / template_id / 'indexes'
    
    if not db_dir.exists():
        raise ValueError(f"Indexes data not found. Please download it first using fetch_marketdata().")
    
    dataset = ds.dataset(str(db_dir), format='parquet')
    
    if index_name:
        return dataset.filter(ds.field('index') == index_name)
    
    return dataset

def indexes_portfolio_get(index_name=None):
    """Get index portfolio.
    
    Args:
        index_name (str): Index name (e.g., 'IBOV', 'IBXX', 'SMLL')
        
    Returns:
        pyarrow.dataset.Dataset: Dataset with index portfolio
    """
    cache_dir = Path(get_cache_dir())
    template_id = "b3-indexes-current-portfolio"
    db_dir = cache_dir / 'db' / template_id / 'portfolio'
    
    if not db_dir.exists():
        raise ValueError(f"Index portfolio data not found. Please download it first using fetch_marketdata().")
    
    dataset = ds.dataset(str(db_dir), format='parquet')
    
    if index_name:
        return dataset.filter(ds.field('index') == index_name)
    
    return dataset

def indexes_historical_get(index_name=None):
    """Get historical index data.
    
    Args:
        index_name (str): Index name (e.g., 'IBOV', 'IBXX', 'SMLL')
        
    Returns:
        pyarrow.dataset.Dataset: Dataset with historical index data
    """
    cache_dir = Path(get_cache_dir())
    template_id = "b3-indexes-historical-data"
    db_dir = cache_dir / 'db' / template_id / 'historical'
    
    if not db_dir.exists():
        raise ValueError(f"Historical index data not found. Please download it first using fetch_marketdata().")
    
    dataset = ds.dataset(str(db_dir), format='parquet')
    
    if index_name:
        return dataset.filter(ds.field('index') == index_name)
    
    return dataset