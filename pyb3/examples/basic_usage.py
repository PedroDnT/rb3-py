"""Basic usage examples for pyb3 package."""

import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date, timedelta

import pyb3
from pyb3.scrapers import (
    cotahist_get, cotahist_filter_equity,
    futures_get,
    yc_brl_get,
    indexes_get
)

# Set cache directory (optional)
# pyb3.set_cache_dir('/path/to/cache')

# Get current cache directory
print(f"Cache directory: {pyb3.get_cache_dir()}")

# Example of using the cache directory
print("\nExample of using the cache directory")
cache_dir = pyb3.get_cache_dir()
print(f"Cache directory: {cache_dir}")

# Bootstrap the package
print("\nBootstrapping the package...")
bootstrap_dir = pyb3.bootstrap()
print(f"Bootstrap directory: {bootstrap_dir}")

# List available templates
print("\nAvailable templates:")
templates = pyb3.list_templates()
for template in templates:
    print(f"- {template}")

# Example of template retrieval
print("\nTemplate retrieval example:")
template = pyb3.template_retrieve('cotahist_daily')
print(f"Template ID: {template.id}")
print(f"Template description: {template.description}")

# Print template parts
if template.parts:
    print("\nTemplate parts:")
    for part in template.parts:
        print(f"- {part.get('name', 'Unknown')}")

# Example of directory structure
print("\nDirectory structure:")
cache_dir = pyb3.get_cache_dir()
directories = [
    'cotahist',
    'futures',
    'yc',
    'indexes',
    'templates',
    'metadata'
]

for directory in directories:
    dir_path = os.path.join(cache_dir, directory)
    exists = os.path.exists(dir_path)
    print(f"- {directory}: {'exists' if exists else 'does not exist'}")

# Create a simple plot
print("\nCreating a simple plot...")
x = range(10)
y = [i**2 for i in x]

plt.figure(figsize=(8, 5))
plt.plot(x, y, marker='o')
plt.title('Sample Plot')
plt.xlabel('X')
plt.ylabel('Y')
plt.grid(True)

# Save plot to cache directory
plot_file = os.path.join(pyb3.get_cache_dir(), 'sample_plot.png')
plt.savefig(plot_file)
print(f"Plot saved to {plot_file}")

print("\nBasic usage example completed successfully!")

print("\nExamples completed. Check the current directory for generated plots.")