"""Example of creating and using custom templates in pyb3 package."""

import os
import yaml
import pandas as pd
from datetime import date

import pyb3
from pyb3.template import Template, load_template_from_file

# Set cache directory (optional)
# pyb3.set_cache_dir('/path/to/cache')

# Bootstrap the package
pyb3.bootstrap()

# Define a custom template
custom_template = {
    'name': 'custom_template',
    'description': 'Custom template for demonstration',
    'fields': [
        {'name': 'date', 'type': 'date', 'description': 'Date'},
        {'name': 'symbol', 'type': 'string', 'description': 'Symbol'},
        {'name': 'price', 'type': 'float', 'description': 'Price'},
        {'name': 'volume', 'type': 'int', 'description': 'Volume'}
    ],
    'parts': [
        {'name': 'data', 'fields': ['date', 'symbol', 'price', 'volume']}
    ],
    'readers': [
        {'name': 'custom_reader', 'function': 'read_csv'}
    ],
    'downloaders': [
        {
            'name': 'custom_downloader',
            'function': 'download_file',
            'url': 'https://example.com/data.csv',
            'method': 'GET'
        }
    ]
}

# Save the custom template to a file
template_dir = os.path.join(pyb3.get_cache_dir(), 'templates')
os.makedirs(template_dir, exist_ok=True)
template_path = os.path.join(template_dir, 'custom_template.yaml')

with open(template_path, 'w') as f:
    yaml.dump(custom_template, f, default_flow_style=False)

print(f"Custom template saved to: {template_path}")

# Load the custom template
template = load_template_from_file(template_path)
print(f"\nLoaded template: {template.name}")
print(f"Template description: {template.description}")
print(f"Number of fields: {len(template.fields)}")

# Create a Template object directly
print("\nCreating a Template object directly:")

# Create sample data
sample_data = pd.DataFrame({
    'date': [date.today()] * 3,
    'symbol': ['AAPL', 'MSFT', 'GOOG'],
    'price': [150.25, 300.75, 2500.50],
    'volume': [1000000, 500000, 200000]
})

# Save sample data to CSV
sample_data_path = os.path.join(pyb3.get_cache_dir(), 'custom_data.csv')
sample_data.to_csv(sample_data_path, index=False)
print(f"Sample data saved to: {sample_data_path}")

# Define a custom reader function
def custom_reader(file_path):
    """Custom reader function for demonstration."""
    df = pd.read_csv(file_path)
    # Convert date column to datetime
    df['date'] = pd.to_datetime(df['date'])
    return df

# Use the custom reader to read the data
print("\nReading data with custom reader:")
data = custom_reader(sample_data_path)
print(data)

# Example of extending the Template class
class CustomTemplate(Template):
    """Custom template class with additional functionality."""
    
    def __init__(self, name, description, fields, parts, readers=None, downloaders=None):
        super().__init__(name, description, fields, parts, readers, downloaders)
        self.metadata = {}
    
    def add_metadata(self, key, value):
        """Add metadata to the template."""
        self.metadata[key] = value
    
    def get_metadata(self, key):
        """Get metadata from the template."""
        return self.metadata.get(key)

# Create a custom template instance
print("\nCreating a custom template instance:")
custom_template_instance = CustomTemplate(
    name='custom_template_instance',
    description='Custom template instance for demonstration',
    fields=template.fields,
    parts=template.parts,
    readers=template.readers,
    downloaders=template.downloaders
)

# Add metadata
custom_template_instance.add_metadata('created_by', 'user')
custom_template_instance.add_metadata('created_at', date.today().isoformat())

# Print template information
print(f"Template name: {custom_template_instance.name}")
print(f"Template description: {custom_template_instance.description}")
print(f"Template metadata: {custom_template_instance.metadata}")

print("\nExample completed.")