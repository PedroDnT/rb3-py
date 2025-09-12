"""Yield curve scraper for B3 data.

This module provides functions to retrieve and process yield curve data from B3.
"""

import os
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.dataset as ds

from .. import get_cache_dir

def yc_get(curve_name):
    """Get yield curve data.
    
    Args:
        curve_name (str): Curve name (e.g., 'PRE', 'DIC', 'DOC')
        
    Returns:
        pyarrow.dataset.Dataset: Dataset with yield curve data
    """
    cache_dir = Path(get_cache_dir())
    template_id = "b3-reference-rates"
    db_dir = cache_dir / 'db' / template_id / 'yc'
    
    if not db_dir.exists():
        raise ValueError(f"Yield curve data not found. Please download it first using fetch_marketdata().")
    
    dataset = ds.dataset(str(db_dir), format='parquet')
    
    return dataset.filter(ds.field('curve_name') == curve_name)

def yc_brl_get():
    """Get Brazilian yield curve data (PRE).
    
    Returns:
        pyarrow.dataset.Dataset: Dataset with Brazilian yield curve data
    """
    return yc_get('PRE')