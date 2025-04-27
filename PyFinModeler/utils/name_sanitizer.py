# PyFinModeler/utils/name_sanitizer.py

import re

def sanitize_item_name(name: str) -> str:
    """
    Convert a FinancialItem name into a safe Python variable name:
    - Replace spaces and hyphens with underscores
    - Remove any other invalid characters
    - Ensure it starts with a letter or underscore
    """
    # Replace spaces and hyphens with underscores
    name = name.replace(" ", "_").replace("-", "_")
    # Remove invalid characters (only allow letters, digits, underscores)
    name = re.sub(r"[^A-Za-z0-9_]", "", name)
    # If the name starts with a number, prefix it with an underscore
    if name and name[0].isdigit():
        name = "_" + name
    return name
