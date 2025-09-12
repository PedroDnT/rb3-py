"""Example of using templates in pyb3 package."""

import os
import pandas as pd
from datetime import date, timedelta

import pyb3
from pyb3.template import list_templates, template_retrieve, load_template_from_file

# Set cache directory (optional)
# pyb3.set_cache_dir('/path/to/cache')

# Bootstrap the package (creates directory structure and copies templates)
pyb3.bootstrap()

# Get current cache directory
print(f"Cache directory: {pyb3.get_cache_dir()}")

# List available templates
print("\nAvailable templates:")
templates = list_templates()
for template in templates:
    print(f"- {template}")

# Retrieve a template
print("\nRetrieving cotahist_daily template:")
template = template_retrieve('cotahist_daily')
print(f"Template name: {template.name}")
print(f"Template description: {template.description}")
print(f"Number of fields: {len(template.fields)}")
print(f"Number of parts: {len(template.parts)}")
print(f"Number of downloaders: {len(template.downloaders)}")

# Print fields
print("\nFields:")
for field in template.fields[:5]:  # Print first 5 fields
    print(f"- {field.name} ({field.type}): {field.description}")
print("...")

# Print parts
print("\nParts:")
for part in template.parts:
    print(f"- {part.name}: {len(part.fields)} fields")

# Print downloaders
print("\nDownloaders:")
for downloader in template.downloaders:
    print(f"- {downloader.name}: {downloader.url}")

# Load a template from file
print("\nLoading template from file:")
template_path = os.path.join(pyb3.get_cache_dir(), 'templates', 'cotahist_daily.yaml')
template = load_template_from_file(template_path)
print(f"Loaded template: {template.name}")

# Download data using a template
print("\nDownloading data using template:")
yesterday = date.today() - timedelta(days=1)
result = pyb3.download_marketdata('cotahist_daily', date=yesterday.strftime('%Y-%m-%d'))
print(f"Download result: {result}")

# Fetch data using a template (download + read)
print("\nFetching data using template:")
df = pyb3.fetch_marketdata('cotahist_daily', date=yesterday.strftime('%Y-%m-%d'))
print(f"Data shape: {df.shape if df is not None else None}")
if df is not None and not df.empty:
    print("\nSample data:")
    print(df.head())