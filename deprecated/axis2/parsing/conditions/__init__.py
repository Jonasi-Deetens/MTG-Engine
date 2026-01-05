# axis2/parsing/conditions/__init__.py

"""
Condition parsing module for Axis2.

This package provides parsers for converting condition strings into structured condition objects.
All functions are defined in the parent conditions.py module and re-exported here.
"""

# Import from the parent conditions.py module
# We use importlib to load the module file directly to avoid the package/module conflict
import importlib.util
from pathlib import Path

# Get the path to conditions.py in the parent directory
_parent_dir = Path(__file__).parent.parent
_conditions_file = _parent_dir / "conditions.py"

# Load the module
spec = importlib.util.spec_from_file_location("_conditions_module", str(_conditions_file))
_conditions_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(_conditions_module)

# Re-export all public functions
parse_condition = _conditions_module.parse_condition
extract_condition_text = _conditions_module.extract_condition_text
normalize_condition_text = _conditions_module.normalize_condition_text
parse_control_condition = _conditions_module.parse_control_condition
parse_permanent_condition = _conditions_module.parse_permanent_condition

__all__ = [
    'parse_condition',
    'extract_condition_text',
    'normalize_condition_text',
    'parse_control_condition',
    'parse_permanent_condition',
]

