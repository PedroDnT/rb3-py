"""Tests for scrapers functionality of pyb3 package."""

import os
import unittest
from unittest.mock import patch, MagicMock
import tempfile
import shutil
from datetime import date, datetime

import pandas as pd
import numpy as np

from pyb3 import get_cache_dir, set_cache_dir
from pyb3.scrapers import (
    cotahist_get, cotahist_filter_equity, cotahist_filter_options, cotahist_filter_futures,
    futures_get,
    yc_get, yc_brl_get,
    indexes_get, indexes_composition_get
)


class TestScrapers(unittest.TestCase):
    """Test scrapers functionality of pyb3 package."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()
        # Store original cache directory
        self.original_cache_dir = get_cache_dir()
        # Set cache directory to temporary directory
        set_cache_dir(self.temp_dir)
        
        # Create mock data directories and files
        os.makedirs(os.path.join(self.temp_dir, 'cotahist'), exist_ok=True)
        os.makedirs(os.path.join(self.temp_dir, 'futures'), exist_ok=True)
        os.makedirs(os.path.join(self.temp_dir, 'yc'), exist_ok=True)
        os.makedirs(os.path.join(self.temp_dir, 'indexes'), exist_ok=True)
        
        # Create mock COTAHIST data
        self.cotahist_df = pd.DataFrame({
            'refdate': pd.date_range('2020-01-01', '2020-01-10'),
            'symbol': ['PETR4', 'VALE3', 'ITUB4', 'PETR4C100', 'DOLJ20', 'IBOV'] * 10,
            'type': ['EQUITY', 'EQUITY', 'EQUITY', 'OPTION', 'FUTURE', 'OTHER'] * 10,
            'close': np.random.rand(60) * 100,
            'volume': np.random.rand(60) * 1000000
        })
        self.cotahist_df.to_parquet(
            os.path.join(self.temp_dir, 'cotahist', 'cotahist.parquet'),
            index=False
        )
        
        # Create mock futures data
        self.futures_df = pd.DataFrame({
            'refdate': pd.date_range('2020-01-01', '2020-01-10').repeat(3),
            'ticker': ['DOL', 'IND', 'DI1'] * 10,
            'maturity': ['F20', 'G20', 'H20'] * 10,
            'settlement_price': np.random.rand(30) * 100
        })
        self.futures_df.to_parquet(
            os.path.join(self.temp_dir, 'futures', 'futures.parquet'),
            index=False
        )
        
        # Create mock yield curve data
        self.yc_df = pd.DataFrame({
            'refdate': pd.date_range('2020-01-01', '2020-01-10').repeat(5),
            'curve_name': ['PRE'] * 50,
            'days': [1, 30, 60, 90, 180] * 10,
            'r_252': np.random.rand(50) * 0.1
        })
        self.yc_df.to_parquet(
            os.path.join(self.temp_dir, 'yc', 'yc.parquet'),
            index=False
        )
        
        # Create mock indexes data
        self.indexes_df = pd.DataFrame({
            'index': ['IBOV', 'IBXX', 'SMLL'] * 10,
            'date': pd.date_range('2020-01-01', '2020-01-10').repeat(3),
            'close': np.random.rand(30) * 100000
        })
        self.indexes_df.to_parquet(
            os.path.join(self.temp_dir, 'indexes', 'indexes.parquet'),
            index=False
        )
        
        # Create mock indexes composition data
        self.indexes_composition_df = pd.DataFrame({
            'index': ['IBOV'] * 10 + ['IBXX'] * 5 + ['SMLL'] * 8,
            'code': ['PETR4', 'VALE3', 'ITUB4', 'BBDC4', 'ABEV3', 'B3SA3', 'BBAS3', 'JBSS3', 'LREN3', 'RENT3'] * 2 + ['MGLU3'],
            'weight': np.random.rand(23) * 0.1
        })
        self.indexes_composition_df.to_parquet(
            os.path.join(self.temp_dir, 'indexes', 'indexes_composition.parquet'),
            index=False
        )
    
    def tearDown(self):
        """Clean up test environment."""
        # Restore original cache directory
        set_cache_dir(self.original_cache_dir)
        # Remove temporary directory
        shutil.rmtree(self.temp_dir)
    
    def test_cotahist_get(self):
        """Test getting COTAHIST data."""
        # Get COTAHIST data
        df = cotahist_get(date='2020-01-01')
        
        # Check result
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 6)  # 6 rows for 2020-01-01
        self.assertIn('symbol', df.columns)
        self.assertIn('type', df.columns)
        self.assertIn('close', df.columns)
    
    def test_cotahist_filter(self):
        """Test filtering COTAHIST data."""
        # Get COTAHIST data
        df = cotahist_get(date='2020-01-01')
        
        # Filter for equity
        equity_df = cotahist_filter_equity(df)
        self.assertEqual(len(equity_df), 3)  # 3 equity rows
        self.assertTrue(all(equity_df['type'] == 'EQUITY'))
        
        # Filter for options
        options_df = cotahist_filter_options(df)
        self.assertEqual(len(options_df), 1)  # 1 option row
        self.assertTrue(all(options_df['type'] == 'OPTION'))
        
        # Filter for futures
        futures_df = cotahist_filter_futures(df)
        self.assertEqual(len(futures_df), 1)  # 1 future row
        self.assertTrue(all(futures_df['type'] == 'FUTURE'))
    
    def test_futures_get(self):
        """Test getting futures data."""
        # Get futures data
        df = futures_get(date='2020-01-01')
        
        # Check result
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 3)  # 3 rows for 2020-01-01
        self.assertIn('ticker', df.columns)
        self.assertIn('maturity', df.columns)
        self.assertIn('settlement_price', df.columns)
        
        # Get futures data for specific ticker
        df = futures_get(date='2020-01-01', ticker='DOL')
        self.assertEqual(len(df), 1)  # 1 row for DOL
        self.assertEqual(df.iloc[0]['ticker'], 'DOL')
    
    def test_yc_get(self):
        """Test getting yield curve data."""
        # Get yield curve data
        df = yc_get(date='2020-01-01', curve_name='PRE')
        
        # Check result
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 5)  # 5 rows for 2020-01-01
        self.assertIn('days', df.columns)
        self.assertIn('r_252', df.columns)
        self.assertTrue(all(df['curve_name'] == 'PRE'))
    
    def test_yc_brl_get(self):
        """Test getting BRL yield curve data."""
        # Get BRL yield curve data
        df = yc_brl_get(date='2020-01-01')
        
        # Check result
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 5)  # 5 rows for 2020-01-01
        self.assertIn('days', df.columns)
        self.assertIn('r_252', df.columns)
        self.assertTrue(all(df['curve_name'] == 'PRE'))
    
    def test_indexes_get(self):
        """Test getting indexes data."""
        # Get indexes data
        df = indexes_get(date='2020-01-01')
        
        # Check result
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 3)  # 3 rows for 2020-01-01
        self.assertIn('index', df.columns)
        self.assertIn('close', df.columns)
        
        # Get indexes data for specific index
        df = indexes_get(date='2020-01-01', index='IBOV')
        self.assertEqual(len(df), 1)  # 1 row for IBOV
        self.assertEqual(df.iloc[0]['index'], 'IBOV')
    
    def test_indexes_composition_get(self):
        """Test getting indexes composition data."""
        # Get indexes composition data
        df = indexes_composition_get(index='IBOV')
        
        # Check result
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 10)  # 10 rows for IBOV
        self.assertIn('code', df.columns)
        self.assertIn('weight', df.columns)
        self.assertTrue(all(df['index'] == 'IBOV'))


if __name__ == '__main__':
    unittest.main()