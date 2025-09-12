"""Template system for data retrieval.

This module defines the template system used to retrieve and parse data from B3 files.
"""

import os
import yaml
from pathlib import Path
from importlib import resources

from .fields import create_fields

class Template:
    """Template for data retrieval and parsing.
    
    Attributes:
        id (str): Template ID
        description (str): Template description
        fields (Fields): Fields collection
        downloader (dict): Downloader configuration
        reader (dict): Reader configuration
        writers (dict): Writers configuration
    """
    
    def __init__(self, id, description=""):
        """Initialize a template.
        
        Args:
            id (str): Template ID
            description (str): Template description
        """
        self.id = id
        self.description = description
        self.fields = None
        self.downloader = None
        self.reader = None
        self.writers = {}
        self.parts = []
        self.filetype = None
    
    def __repr__(self):
        return f"Template(id={self.id}, description={self.description})"

def load_template_from_file(filename):
    """Load a template from a YAML file.
    
    Args:
        filename (str): Path to the YAML file
        
    Returns:
        Template: Template object
    """
    with open(filename, 'r') as f:
        data = yaml.safe_load(f)
    
    template = Template(data.get('id'))
    template.description = data.get('description', '')
    
    # Load fields
    if 'fields' in data:
        field_defs = [{'name': name, 'type': type_name} for name, type_name in data['fields'].items()]
        template.fields = create_fields(field_defs)
    
    # Load parts
    if 'parts' in data:
        template.parts = data['parts']
    
    # Load reader
    if 'reader' in data:
        template.reader = data['reader']
    
    # Load writers
    if 'writers' in data:
        template.writers = data['writers']
    
    # Load downloader
    if 'downloader' in data:
        template.downloader = data['downloader']
    
    # Load filetype
    template.filetype = data.get('filetype')
    
    return template

def get_templates_dir():
    """Get the directory containing template files.
    
    Returns:
        Path: Path to the templates directory
    """
    # First check if templates are in the package
    try:
        with resources.path('pyb3', 'templates') as path:
            return path
    except ImportError:
        # If not, check if they're in the current directory
        current_dir = Path(os.getcwd())
        templates_dir = current_dir / 'templates'
        if templates_dir.exists():
            return templates_dir
        
        # If not, check if they're in the package directory
        package_dir = Path(__file__).parent
        templates_dir = package_dir / 'templates'
        if templates_dir.exists():
            return templates_dir
        
        # If not found, create the directory
        templates_dir.mkdir(parents=True, exist_ok=True)
        return templates_dir

def list_templates():
    """List available templates.
    
    Returns:
        list: List of template IDs and descriptions
    """
    templates_dir = get_templates_dir()
    templates = []
    
    for file in templates_dir.glob('*.yaml'):
        try:
            template = load_template_from_file(file)
            templates.append({
                'Template': template.id,
                'Description': template.description
            })
        except Exception as e:
            print(f"Error loading template {file}: {e}")
    
    return templates

def template_retrieve(template_id):
    """Retrieve a template by ID.
    
    Args:
        template_id (str): Template ID
        
    Returns:
        Template: Template object
    """
    templates_dir = get_templates_dir()
    template_file = templates_dir / f"{template_id}.yaml"
    
    if not template_file.exists():
        raise ValueError(f"Template {template_id} not found")
    
    return load_template_from_file(template_file)