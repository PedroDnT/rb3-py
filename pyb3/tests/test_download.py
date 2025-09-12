"""Tests for download functionality of pyb3 package."""

import os
import unittest
from unittest.mock import patch, MagicMock
import tempfile
import shutil
import json
from datetime import date, datetime

import pandas as pd
import numpy as np

from pyb3 import get_cache_dir, set_cache_dir
from pyb3.download import (
    download_file, save_metadata, load_metadata,
    download_marketdata, fetch_marketdata
)


class TestDownload(unittest.TestCase):
    """Test download functionality of pyb3 package."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()
        # Store original cache directory
        self.original_cache_dir = get_cache_dir()
        # Set cache directory to temporary directory
        set_cache_dir(self.temp_dir)
    
    def tearDown(self):
        """Clean up test environment."""
        # Restore original cache directory
        set_cache_dir(self.original_cache_dir)
        # Remove temporary directory
        shutil.rmtree(self.temp_dir)
    
    @patch('pyb3.download.requests.get')
    def test_download_file(self, mock_get):
        """Test downloading a file."""
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'test content'
        mock_response.headers = {'Content-Length': '12'}
        mock_get.return_value = mock_response
        
        # Download file
        output_path = os.path.join(self.temp_dir, 'test_file.txt')
        result = download_file('http://example.com/test', output_path)
        
        # Check result
        self.assertTrue(result)
        self.assertTrue(os.path.exists(output_path))
        with open(output_path, 'rb') as f:
            self.assertEqual(f.read(), b'test content')
        
        # Check that requests.get was called with the correct URL
        mock_get.assert_called_once_with(
            'http://example.com/test',
            stream=True,
            headers={'User-Agent': unittest.mock.ANY}
        )
    
    @patch('pyb3.download.requests.get')
    def test_download_file_error(self, mock_get):
        """Test downloading a file with an error."""
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        # Download file
        output_path = os.path.join(self.temp_dir, 'test_file.txt')
        result = download_file('http://example.com/test', output_path)
        
        # Check result
        self.assertFalse(result)
        self.assertFalse(os.path.exists(output_path))
    
    def test_metadata(self):
        """Test saving and loading metadata."""
        # Create metadata
        metadata = {
            'template': 'test_template',
            'date': '2020-01-01',
            'url': 'http://example.com/test',
            'file_path': 'test_file.txt',
            'download_date': datetime.now().isoformat()
        }
        
        # Save metadata
        metadata_path = os.path.join(self.temp_dir, 'metadata.json')
        save_metadata(metadata, metadata_path)
        
        # Check that metadata file exists
        self.assertTrue(os.path.exists(metadata_path))
        
        # Load metadata
        loaded_metadata = load_metadata(metadata_path)
        
        # Check loaded metadata
        self.assertEqual(loaded_metadata['template'], 'test_template')
        self.assertEqual(loaded_metadata['date'], '2020-01-01')
        self.assertEqual(loaded_metadata['url'], 'http://example.com/test')
        self.assertEqual(loaded_metadata['file_path'], 'test_file.txt')
    
    @patch('pyb3.download.download_file')
    @patch('pyb3.template.load_template_from_file')
    def test_download_marketdata(self, mock_load_template, mock_download_file):
        """Test downloading market data."""
        # Mock template
        mock_template = MagicMock()
        mock_template.name = 'test_template'
        mock_template.downloaders = [{
            'name': 'test_downloader',
            'url': 'http://example.com/test/{date}',
            'method': 'GET'
        }]
        mock_load_template.return_value = mock_template
        
        # Mock download_file
        mock_download_file.return_value = True
        
        # Download market data
        result = download_marketdata('test_template', date='2020-01-01')
        
        # Check result
        self.assertTrue(result)
        
        # Check that download_file was called with the correct URL
        mock_download_file.assert_called_once_with(
            'http://example.com/test/2020-01-01',
            unittest.mock.ANY,
            progress=True
        )
    
    @patch('pyb3.download.download_marketdata')
    @patch('pyb3.read.read_marketdata')
    def test_fetch_marketdata(self, mock_read_marketdata, mock_download_marketdata):
        """Test fetching market data."""
        # Mock download_marketdata
        mock_download_marketdata.return_value = True
        
        # Mock read_marketdata
        mock_df = pd.DataFrame({'col1': [1, 2, 3], 'col2': ['a', 'b', 'c']})
        mock_read_marketdata.return_value = mock_df
        
        # Fetch market data
        result = fetch_marketdata('test_template', date='2020-01-01')
        
        # Check result
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 3)
        self.assertEqual(list(result.columns), ['col1', 'col2'])
        
        # Check that download_marketdata and read_marketdata were called
        mock_download_marketdata.assert_called_once_with(
            'test_template',
            date='2020-01-01',
            force_download=False,
            progress=True
        )
        mock_read_marketdata.assert_called_once_with(
            'test_template',
            date='2020-01-01'
        )


if __name__ == '__main__':
    unittest.main()