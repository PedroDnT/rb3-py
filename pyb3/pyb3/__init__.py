"""pyb3 - Download and parse public data released by B3 Exchange

This package provides tools for downloading, processing, and analyzing market data from B3,
including stocks, futures, options, yield curves, and market indices.
"""

import os
import tempfile
from pathlib import Path

__version__ = "0.1.0"

# Global cache directory
_CACHE_DIR = None

def get_cache_dir():
    """Get the cache directory for pyb3.
    
    Returns:
        str: Path to the cache directory
    """
    global _CACHE_DIR
    if _CACHE_DIR is None:
        _CACHE_DIR = os.environ.get("PYB3_CACHE_DIR", tempfile.gettempdir())
    return _CACHE_DIR

def set_cache_dir(directory):
    """Set the cache directory for pyb3.
    
    Args:
        directory (str): Path to the cache directory
    """
    global _CACHE_DIR
    directory_path = Path(directory)
    if not directory_path.exists():
        directory_path.mkdir(parents=True, exist_ok=True)
    _CACHE_DIR = str(directory_path)

# Import core functionality
from .download import download_marketdata, fetch_marketdata
from .read import read_marketdata
from .template import list_templates, template_retrieve
from .bootstrap import bootstrap
from .scrapers import (
    cotahist_get, 
    futures_get, 
    yc_brl_get, 
    indexes_get,
    indexes_composition_get
)

# Initialize the package
def bootstrap():
    """Initialize the pyb3 package.
    
    This function creates the necessary directory structure for the cache.
    """
    cache_dir = Path(get_cache_dir())
    raw_dir = cache_dir / "raw"
    db_dir = cache_dir / "db"
    
    # Create directories if they don't exist
    raw_dir.mkdir(parents=True, exist_ok=True)
    db_dir.mkdir(parents=True, exist_ok=True)
    
    return True