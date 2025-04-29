# PyFinModeler/utils/markdown_utils.py

def create_markdown_table(data: dict) -> str:
    """
    Creates a Markdown table from a dictionary.

    Args:
        data: Dictionary with key-value pairs

    Returns:
        Markdown-formatted table as a string
    """
    # Header
    table = "| Key | Value |\n"
    table += "|:----|:------|\n"

    # Rows
    for key, value in data.items():
        table += f"| {key} | {value} |\n"

    return table

def create_markdown_table_from_dicts(dicts: list, columns: list) -> str:
    """
    Create a Markdown table from a list of year:value dictionaries.

    Args:
        dicts: List of dictionaries (one dict per column, keys = years)
        columns: List of column names for each dict

    Returns:
        Markdown-formatted table as a string
    """
    # 1. Collect all unique years
    all_years = set()
    for d in dicts:
        all_years.update(d.keys())
    all_years = sorted(all_years, reverse=True)  # Sort years descending (optional)

    # 2. Create table header
    table = "| Year | " + " | ".join(columns) + " |\n"
    table += "|:----| " + " | ".join([":----:" for _ in columns]) + " |\n"

    # 3. Create rows
    for year in all_years:
        row = f"| {year} "
        for d in dicts:
            value = d.get(year, "")  # Empty cell if year missing
            if isinstance(value, float):
                value = f"{value:.2f}"  # Format floats nicely
            row += f"| {value} "
        row += "|\n"
        table += row

    return table