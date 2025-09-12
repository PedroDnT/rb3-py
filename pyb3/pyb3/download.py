"""Download functionality for B3 data.

This module provides functions to download data from B3 website.
"""

import os
import hashlib
import json
import gzip
import shutil
import datetime
from pathlib import Path

import requests
from tqdm import tqdm

from . import get_cache_dir
from .template import template_retrieve

class DownloadMeta:
    """Metadata for downloaded files.
    
    Attributes:
        template (str): Template ID
        download_checksum (str): Checksum of the download arguments
        download_args (dict): Download arguments
        downloaded (str): Path to the downloaded file
        created (datetime): Creation timestamp
        is_downloaded (bool): Whether the file was downloaded
        is_processed (bool): Whether the file was processed
        is_valid (bool): Whether the file is valid
    """
    
    def __init__(self, template, download_args=None):
        """Initialize download metadata.
        
        Args:
            template (str): Template ID
            download_args (dict): Download arguments
        """
        self.template = template
        self.download_args = download_args or {}
        self.download_checksum = self._calculate_checksum()
        self.downloaded = None
        self.created = datetime.datetime.now()
        self.is_downloaded = False
        self.is_processed = False
        self.is_valid = False
    
    def _calculate_checksum(self):
        """Calculate a checksum for the download arguments.
        
        Returns:
            str: Checksum
        """
        args_str = json.dumps(self.download_args, sort_keys=True)
        return hashlib.md5(args_str.encode()).hexdigest()
    
    def to_dict(self):
        """Convert metadata to dictionary.
        
        Returns:
            dict: Metadata as dictionary
        """
        return {
            'template': self.template,
            'download_checksum': self.download_checksum,
            'download_args': self.download_args,
            'downloaded': self.downloaded,
            'created': self.created.isoformat(),
            'is_downloaded': self.is_downloaded,
            'is_processed': self.is_processed,
            'is_valid': self.is_valid
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create metadata from dictionary.
        
        Args:
            data (dict): Metadata as dictionary
            
        Returns:
            DownloadMeta: Metadata object
        """
        meta = cls(data['template'], data['download_args'])
        meta.download_checksum = data['download_checksum']
        meta.downloaded = data['downloaded']
        meta.created = datetime.datetime.fromisoformat(data['created'])
        meta.is_downloaded = data['is_downloaded']
        meta.is_processed = data['is_processed']
        meta.is_valid = data['is_valid']
        return meta

def get_meta_path(meta):
    """Get the path to the metadata file.
    
    Args:
        meta (DownloadMeta): Metadata object
        
    Returns:
        Path: Path to the metadata file
    """
    cache_dir = Path(get_cache_dir())
    return cache_dir / 'raw' / f"{meta.download_checksum}.meta.json"

def save_meta(meta):
    """Save metadata to file.
    
    Args:
        meta (DownloadMeta): Metadata object
    """
    meta_path = get_meta_path(meta)
    with open(meta_path, 'w') as f:
        json.dump(meta.to_dict(), f)

def load_meta(meta_path):
    """Load metadata from file.
    
    Args:
        meta_path (Path): Path to the metadata file
        
    Returns:
        DownloadMeta: Metadata object
    """
    with open(meta_path, 'r') as f:
        data = json.load(f)
    return DownloadMeta.from_dict(data)

def download_file(url, output_path, progress=True):
    """Download a file from a URL.
    
    Args:
        url (str): URL to download
        output_path (Path): Path to save the file
        progress (bool): Whether to show a progress bar
        
    Returns:
        bool: Whether the download was successful
    """
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024  # 1 KB
        
        with open(output_path, 'wb') as f:
            if progress and total_size > 0:
                with tqdm(total=total_size, unit='B', unit_scale=True, desc=url) as pbar:
                    for data in response.iter_content(block_size):
                        f.write(data)
                        pbar.update(len(data))
            else:
                for data in response.iter_content(block_size):
                    f.write(data)
        
        return True
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False

def download_marketdata(template_id, **kwargs):
    """Download market data using a template.
    
    Args:
        template_id (str): Template ID
        **kwargs: Download arguments
        
    Returns:
        DownloadMeta: Metadata object
    """
    # Create metadata
    meta = DownloadMeta(template_id, kwargs)
    
    # Check if file already exists
    meta_path = get_meta_path(meta)
    if meta_path.exists():
        return load_meta(meta_path)
    
    # Get template
    template = template_retrieve(template_id)
    
    # Get downloader function
    downloader_config = template.downloader
    downloader_function = downloader_config.get('function')
    
    if not downloader_function:
        raise ValueError(f"No downloader function specified for template {template_id}")
    
    # Import the downloader function
    module_name, function_name = downloader_function.rsplit('.', 1)
    module = __import__(module_name, fromlist=[function_name])
    downloader = getattr(module, function_name)
    
    # Download the file
    cache_dir = Path(get_cache_dir())
    raw_dir = cache_dir / 'raw'
    raw_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = raw_dir / f"{meta.download_checksum}.raw"
    compressed_path = raw_dir / f"{meta.download_checksum}.gz"
    
    try:
        # Call the downloader function
        result = downloader(output_path, **kwargs)
        
        if result:
            # Compress the file
            with open(output_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Update metadata
            meta.downloaded = str(compressed_path)
            meta.is_downloaded = True
            
            # Save metadata
            save_meta(meta)
            
            # Remove the raw file
            os.remove(output_path)
        
        return meta
    except Exception as e:
        print(f"Error downloading data for template {template_id}: {e}")
        return meta

def fetch_marketdata(template_id, **kwargs):
    """Download and process market data using a template.
    
    This function downloads the data and processes it according to the template.
    
    Args:
        template_id (str): Template ID
        **kwargs: Download arguments
        
    Returns:
        DownloadMeta: Metadata object
    """
    # Download the data
    meta = download_marketdata(template_id, **kwargs)
    
    # Process the data
    if meta.is_downloaded and not meta.is_processed:
        from .read import read_marketdata
        meta = read_marketdata(meta)
    
    return meta