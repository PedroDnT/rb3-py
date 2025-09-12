"""Field definitions for pyb3.

This module defines the field classes used to parse and validate data from B3 files.
"""

from .types import TYPE_CONVERTERS

class Field:
    """Base field class for data parsing.
    
    Attributes:
        name (str): Field name
        type (str): Field type
        converter (callable): Function to convert the field value
    """
    
    def __init__(self, name, type_name):
        """Initialize a field.
        
        Args:
            name (str): Field name
            type_name (str): Field type name
        """
        self.name = name
        self.type = type_name
        self.converter = TYPE_CONVERTERS.get(type_name, lambda x: x)
    
    def convert(self, value):
        """Convert a value to the field type.
        
        Args:
            value: Value to convert
            
        Returns:
            Converted value
        """
        return self.converter(value)

class Fields:
    """Collection of fields for data parsing.
    
    Attributes:
        fields (list): List of Field objects
    """
    
    def __init__(self, fields=None):
        """Initialize a collection of fields.
        
        Args:
            fields (list): List of Field objects
        """
        self.fields = fields or []
    
    def add(self, field):
        """Add a field to the collection.
        
        Args:
            field (Field): Field to add
        """
        self.fields.append(field)
    
    def get(self, name):
        """Get a field by name.
        
        Args:
            name (str): Field name
            
        Returns:
            Field: Field object
        """
        for field in self.fields:
            if field.name == name:
                return field
        return None
    
    def names(self):
        """Get the names of all fields.
        
        Returns:
            list: List of field names
        """
        return [field.name for field in self.fields]
    
    def types(self):
        """Get the types of all fields.
        
        Returns:
            list: List of field types
        """
        return [field.type for field in self.fields]
    
    def convert(self, values):
        """Convert values according to field types.
        
        Args:
            values (dict): Dictionary of values
            
        Returns:
            dict: Dictionary of converted values
        """
        result = {}
        for field in self.fields:
            if field.name in values:
                result[field.name] = field.convert(values[field.name])
        return result

def create_field(name, type_name):
    """Create a new field.
    
    Args:
        name (str): Field name
        type_name (str): Field type name
        
    Returns:
        Field: Field object
    """
    return Field(name, type_name)

def create_fields(field_defs):
    """Create a collection of fields.
    
    Args:
        field_defs (list): List of field definitions
        
    Returns:
        Fields: Fields object
    """
    fields = Fields()
    for field_def in field_defs:
        fields.add(create_field(field_def["name"], field_def["type"]))
    return fields