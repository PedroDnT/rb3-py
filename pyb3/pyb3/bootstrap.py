"""Bootstrap functions for pyb3 package.

This module provides functions to initialize the package directory structure.
"""

import os
import shutil
from pathlib import Path
import pkg_resources

def create_directory_structure(base_dir=None):
    """Create the directory structure for pyb3 package.
    
    Args:
        base_dir (str, optional): Base directory for the package. If None, use the default cache directory.
        
    Returns:
        str: Path to the created directory structure
    """
    from pyb3 import get_cache_dir
    
    # Use default cache directory if not specified
    if base_dir is None:
        base_dir = get_cache_dir()
    
    # Create base directory if it doesn't exist
    os.makedirs(base_dir, exist_ok=True)
    
    # Create subdirectories
    subdirs = [
        'cotahist',
        'futures',
        'yc',
        'indexes',
        'templates',
        'metadata'
    ]
    
    for subdir in subdirs:
        os.makedirs(os.path.join(base_dir, subdir), exist_ok=True)
    
    # Copy template files to templates directory
    templates_dir = os.path.join(base_dir, 'templates')
    package_templates_dir = pkg_resources.resource_filename('pyb3', 'templates')
    
    # Copy all template files
    for template_file in os.listdir(package_templates_dir):
        if template_file.endswith('.yaml'):
            src = os.path.join(package_templates_dir, template_file)
            dst = os.path.join(templates_dir, template_file)
            shutil.copy2(src, dst)
    
    return base_dir

def bootstrap(base_dir=None):
    """Bootstrap the pyb3 package.
    
    This function initializes the package directory structure and copies template files.
    
    Args:
        base_dir (str, optional): Base directory for the package. If None, use the default cache directory.
        
    Returns:
        str: Path to the created directory structure
    """
    return create_directory_structure(base_dir)