"""Writers for B3 data files.

This module provides functions for writing processed data to various formats.
"""

import os
import json
import datetime
from pathlib import Path

import pandas as pd
import numpy as np

def write_parquet(df, file_path, partition_cols=None):
    """Write DataFrame to Parquet file or partitioned dataset.
    
    Args:
        df (pandas.DataFrame): Data frame to write
        file_path (str): Path to the file or directory
        partition_cols (list, optional): Columns to partition by
        
    Returns:
        str: Path to the written file or directory
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Convert datetime columns to pandas datetime
    for col in df.columns:
        if isinstance(df[col].iloc[0] if not df.empty else None, (datetime.date, datetime.datetime)):
            df[col] = pd.to_datetime(df[col])
    
    # Write to Parquet
    if partition_cols:
        df.to_parquet(
            file_path,
            partition_cols=partition_cols,
            index=False,
            engine='pyarrow',
            compression='snappy'
        )
    else:
        df.to_parquet(
            file_path,
            index=False,
            engine='pyarrow',
            compression='snappy'
        )
    
    return file_path

def write_csv(df, file_path, **kwargs):
    """Write DataFrame to CSV file.
    
    Args:
        df (pandas.DataFrame): Data frame to write
        file_path (str): Path to the file
        **kwargs: Additional arguments to pass to pandas.DataFrame.to_csv
        
    Returns:
        str: Path to the written file
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Set default parameters
    params = {
        'index': False,
        'encoding': 'utf-8'
    }
    
    # Update with user parameters
    params.update(kwargs)
    
    # Write to CSV
    df.to_csv(file_path, **params)
    
    return file_path

def write_excel(df, file_path, sheet_name='Sheet1', **kwargs):
    """Write DataFrame to Excel file.
    
    Args:
        df (pandas.DataFrame): Data frame to write
        file_path (str): Path to the file
        sheet_name (str, optional): Name of the sheet
        **kwargs: Additional arguments to pass to pandas.DataFrame.to_excel
        
    Returns:
        str: Path to the written file
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Set default parameters
    params = {
        'index': False,
        'sheet_name': sheet_name
    }
    
    # Update with user parameters
    params.update(kwargs)
    
    # Write to Excel
    df.to_excel(file_path, **params)
    
    return file_path

def write_json(data, file_path, indent=2):
    """Write data to JSON file.
    
    Args:
        data (dict or list): Data to write
        file_path (str): Path to the file
        indent (int, optional): Indentation level
        
    Returns:
        str: Path to the written file
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Custom JSON encoder to handle datetime objects
    class DateTimeEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, (datetime.datetime, datetime.date)):
                return obj.isoformat()
            elif isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            return super().default(obj)
    
    # Write to JSON
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, cls=DateTimeEncoder, indent=indent)
    
    return file_path

def write_metadata(metadata, file_path):
    """Write metadata to JSON file.
    
    Args:
        metadata (dict): Metadata to write
        file_path (str): Path to the file
        
    Returns:
        str: Path to the written file
    """
    return write_json(metadata, file_path)

def write_dataset(df, base_path, dataset_name, partition_cols=None):
    """Write DataFrame to a partitioned Parquet dataset.
    
    Args:
        df (pandas.DataFrame): Data frame to write
        base_path (str): Base path for the dataset
        dataset_name (str): Name of the dataset
        partition_cols (list, optional): Columns to partition by
        
    Returns:
        str: Path to the dataset directory
    """
    # Create dataset path
    dataset_path = os.path.join(base_path, dataset_name)
    
    # Write to Parquet dataset
    return write_parquet(df, dataset_path, partition_cols=partition_cols)