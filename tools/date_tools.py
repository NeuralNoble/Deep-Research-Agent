from agents import function_tool

@function_tool
def get_current_date() -> str:
    """
    Get the current date in ISO format (YYYY-MM-DD) to calculate video recency.
    """
    from datetime import datetime
    current_date = datetime.now().strftime("%Y-%m-%d")
    return f"Current date: {current_date}"