"""Read and parse market data files.

This module provides functions to read and parse market data files downloaded from B3.
"""

import os
import gzip
import json
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from . import get_cache_dir
from .template import template_retrieve
from .download import load_meta, save_meta

def read_csv_file(file_path, **kwargs):
    """Read a CSV file.
    
    Args:
        file_path (str): Path to the file
        **kwargs: Additional arguments for pandas.read_csv
        
    Returns:
        pandas.DataFrame: Data frame
    """
    return pd.read_csv(file_path, **kwargs)

def read_fwf_file(file_path, **kwargs):
    """Read a fixed-width file.
    
    Args:
        file_path (str): Path to the file
        **kwargs: Additional arguments for pandas.read_fwf
        
    Returns:
        pandas.DataFrame: Data frame
    """
    return pd.read_fwf(file_path, **kwargs)

def read_json_file(file_path, **kwargs):
    """Read a JSON file.
    
    Args:
        file_path (str): Path to the file
        **kwargs: Additional arguments for pandas.read_json
        
    Returns:
        pandas.DataFrame: Data frame
    """
    return pd.read_json(file_path, **kwargs)

def read_xml_file(file_path, **kwargs):
    """Read an XML file.
    
    Args:
        file_path (str): Path to the file
        **kwargs: Additional arguments for pandas.read_xml
        
    Returns:
        pandas.DataFrame: Data frame
    """
    return pd.read_xml(file_path, **kwargs)

def read_marketdata(meta):
    """Read and parse market data files.
    
    Args:
        meta: Metadata object or path to metadata file
        
    Returns:
        meta: Updated metadata object
    """
    # Load metadata if necessary
    if isinstance(meta, (str, Path)):
        meta = load_meta(meta)
    
    # Check if file exists
    if not meta.is_downloaded or not meta.downloaded or not os.path.exists(meta.downloaded):
        print(f"File not downloaded: {meta.template}")
        return meta
    
    # Get template
    template = template_retrieve(meta.template)
    
    # Get reader function
    reader_config = template.reader
    reader_function = reader_config.get('function')
    
    if not reader_function:
        # Use default reader based on filetype
        filetype = template.filetype.lower()
        if filetype == 'csv':
            reader = read_csv_file
        elif filetype == 'fwf':
            reader = read_fwf_file
        elif filetype == 'json':
            reader = read_json_file
        elif filetype == 'xml':
            reader = read_xml_file
        else:
            raise ValueError(f"Unsupported filetype: {filetype}")
    else:
        # Import the reader function
        module_name, function_name = reader_function.rsplit('.', 1)
        module = __import__(module_name, fromlist=[function_name])
        reader = getattr(module, function_name)
    
    try:
        # Decompress the file
        cache_dir = Path(get_cache_dir())
        temp_file = cache_dir / 'raw' / f"{meta.download_checksum}.tmp"
        
        with gzip.open(meta.downloaded, 'rb') as f_in:
            with open(temp_file, 'wb') as f_out:
                f_out.write(f_in.read())
        
        # Read the file
        reader_args = reader_config.get('args', {})
        data = reader(temp_file, **reader_args)
        
        # Process the data
        for writer_name, writer_config in template.writers.items():
            # Get processor function
            processor_function = writer_config.get('function')
            if processor_function:
                # Import the processor function
                module_name, function_name = processor_function.rsplit('.', 1)
                module = __import__(module_name, fromlist=[function_name])
                processor = getattr(module, function_name)
                
                # Process the data
                processed_data = processor(data)
            else:
                processed_data = data
            
            # Write the data
            db_dir = cache_dir / 'db' / template.id / writer_name
            db_dir.mkdir(parents=True, exist_ok=True)
            
            # Convert to Arrow table
            table = pa.Table.from_pandas(processed_data)
            
            # Write to Parquet
            pq.write_to_dataset(
                table,
                root_path=str(db_dir),
                partition_cols=writer_config.get('partition_by', []),
                existing_data_behavior='overwrite_or_ignore'
            )
        
        # Update metadata
        meta.is_processed = True
        meta.is_valid = True
        save_meta(meta)
        
        # Remove temporary file
        os.remove(temp_file)
        
        return meta
    except Exception as e:
        print(f"Error processing file: {e}")
        meta.is_processed = False
        meta.is_valid = False
        save_meta(meta)
        return meta