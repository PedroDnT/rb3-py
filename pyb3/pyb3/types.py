"""Data types and field definitions for pyb3.

This module defines the data types and field definitions used in the pyb3 package.
These types are used to parse and validate data from B3 files.
"""

import re
import datetime
import pandas as pd
import numpy as np

# Type conversion functions
def to_int(value):
    """Convert a value to integer.
    
    Args:
        value: Value to convert
        
    Returns:
        int: Converted value
    """
    if pd.isna(value) or value == "":
        return None
    try:
        return int(value)
    except ValueError:
        # Try to convert to float first, then to int
        return int(float(value))

def to_float(value):
    """Convert a value to float.
    
    Args:
        value: Value to convert
        
    Returns:
        float: Converted value
    """
    if pd.isna(value) or value == "":
        return None
    return float(value)

def to_date(value, fmt="%Y-%m-%d"):
    """Convert a value to date.
    
    Args:
        value: Value to convert
        fmt (str): Date format
        
    Returns:
        datetime.date: Converted value
    """
    if pd.isna(value) or value == "":
        return None
    if isinstance(value, datetime.date):
        return value
    if isinstance(value, str):
        return datetime.datetime.strptime(value, fmt).date()
    return None

def to_datetime(value, fmt="%Y-%m-%d %H:%M:%S"):
    """Convert a value to datetime.
    
    Args:
        value: Value to convert
        fmt (str): Datetime format
        
    Returns:
        datetime.datetime: Converted value
    """
    if pd.isna(value) or value == "":
        return None
    if isinstance(value, datetime.datetime):
        return value
    if isinstance(value, str):
        return datetime.datetime.strptime(value, fmt)
    return None

def to_str(value):
    """Convert a value to string.
    
    Args:
        value: Value to convert
        
    Returns:
        str: Converted value
    """
    if pd.isna(value) or value == "":
        return None
    return str(value)

# Type definitions
TYPE_CONVERTERS = {
    "character": to_str,
    "integer": to_int,
    "numeric": to_float,
    "date": to_date,
    "datetime": to_datetime,
}

# Month code conversion
MONTH_CODES = {
    "F": 1,   # January
    "G": 2,   # February
    "H": 3,   # March
    "J": 4,   # April
    "K": 5,   # May
    "M": 6,   # June
    "N": 7,   # July
    "Q": 8,   # August
    "U": 9,   # September
    "V": 10,  # October
    "X": 11,  # November
    "Z": 12,  # December
}

def code2month(code):
    """Convert a month code to month number.
    
    Args:
        code (str): Month code
        
    Returns:
        int: Month number (1-12)
    """
    return MONTH_CODES.get(code.upper())

def maturitycode2date(code):
    """Convert a maturity code to date.
    
    Args:
        code (str): Maturity code (e.g., 'F21' for January 2021)
        
    Returns:
        datetime.date: First day of the month
    """
    if len(code) < 3:
        return None
    
    month_code = code[0]
    year_code = code[1:]
    
    month = code2month(month_code)
    if month is None:
        return None
    
    # Handle year (assuming 20xx for year codes)
    if len(year_code) == 1:
        year = 2000 + int(year_code)
    elif len(year_code) == 2:
        year = 2000 + int(year_code)
    else:
        year = int(year_code)
    
    return datetime.date(year, month, 1)