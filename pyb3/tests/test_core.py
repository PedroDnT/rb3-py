"""Tests for core functionality of pyb3 package."""

import os
import unittest
from unittest.mock import patch, MagicMock
import tempfile
import shutil

import pandas as pd
import numpy as np

from pyb3 import get_cache_dir, set_cache_dir
from pyb3.template import load_template_from_file, get_templates_dir
from pyb3.types import to_date, to_float, to_int, month_code_to_number


class TestCore(unittest.TestCase):
    """Test core functionality of pyb3 package."""
    
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
    
    def test_cache_dir(self):
        """Test cache directory functions."""
        # Test that cache directory is set correctly
        self.assertEqual(get_cache_dir(), self.temp_dir)
        
        # Test setting a new cache directory
        new_dir = os.path.join(self.temp_dir, 'new_cache')
        set_cache_dir(new_dir)
        self.assertEqual(get_cache_dir(), new_dir)
        self.assertTrue(os.path.exists(new_dir))
    
    def test_templates_dir(self):
        """Test templates directory function."""
        # Test that templates directory exists
        templates_dir = get_templates_dir()
        self.assertTrue(os.path.exists(templates_dir))
        self.assertTrue(os.path.isdir(templates_dir))
    
    def test_type_conversions(self):
        """Test type conversion functions."""
        # Test to_int
        self.assertEqual(to_int('123'), 123)
        self.assertEqual(to_int('123.45'), 123)
        self.assertEqual(to_int(''), None)
        self.assertEqual(to_int(None), None)
        
        # Test to_float
        self.assertEqual(to_float('123.45'), 123.45)
        self.assertEqual(to_float('123'), 123.0)
        self.assertEqual(to_float(''), None)
        self.assertEqual(to_float(None), None)
        
        # Test to_date
        self.assertEqual(to_date('2020-01-01'), pd.Timestamp('2020-01-01').date())
        self.assertEqual(to_date('20200101'), pd.Timestamp('2020-01-01').date())
        self.assertEqual(to_date(''), None)
        self.assertEqual(to_date(None), None)
    
    def test_month_code_conversion(self):
        """Test month code conversion functions."""
        # Test month_code_to_number
        self.assertEqual(month_code_to_number('F'), 1)  # January
        self.assertEqual(month_code_to_number('G'), 2)  # February
        self.assertEqual(month_code_to_number('H'), 3)  # March
        self.assertEqual(month_code_to_number('J'), 4)  # April
        self.assertEqual(month_code_to_number('K'), 5)  # May
        self.assertEqual(month_code_to_number('M'), 6)  # June
        self.assertEqual(month_code_to_number('N'), 7)  # July
        self.assertEqual(month_code_to_number('Q'), 8)  # August
        self.assertEqual(month_code_to_number('U'), 9)  # September
        self.assertEqual(month_code_to_number('V'), 10)  # October
        self.assertEqual(month_code_to_number('X'), 11)  # November
        self.assertEqual(month_code_to_number('Z'), 12)  # December
        self.assertIsNone(month_code_to_number('A'))  # Invalid code


class TestTemplate(unittest.TestCase):
    """Test template functionality."""
    
    def test_load_template(self):
        """Test loading a template from file."""
        # Get templates directory
        templates_dir = get_templates_dir()
        
        # Create a simple test template
        test_template_content = """
        name: test_template
        description: Test template
        fields:
          - name: field1
            type: string
          - name: field2
            type: int
        parts:
          - name: part1
            fields: [field1, field2]
        """
        
        # Write test template to file
        with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False) as f:
            f.write(test_template_content.encode('utf-8'))
            template_path = f.name
        
        try:
            # Load template from file
            template = load_template_from_file(template_path)
            
            # Check template properties
            self.assertEqual(template.name, 'test_template')
            self.assertEqual(template.description, 'Test template')
            self.assertEqual(len(template.fields), 2)
            self.assertEqual(template.fields[0].name, 'field1')
            self.assertEqual(template.fields[0].type, 'string')
            self.assertEqual(template.fields[1].name, 'field2')
            self.assertEqual(template.fields[1].type, 'int')
            self.assertEqual(len(template.parts), 1)
            self.assertEqual(template.parts[0].name, 'part1')
            self.assertEqual(template.parts[0].fields, ['field1', 'field2'])
        finally:
            # Clean up
            os.unlink(template_path)


if __name__ == '__main__':
    unittest.main()