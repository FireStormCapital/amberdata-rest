import functools
from typing import Callable

import pandas as pd


def convert_timestamp(func: Callable) -> Callable:
    """
    Decorator to convert timestamp columns to datetime format in DataFrame results.

    This decorator should be applied to processed functions (non-raw functions) that return
    DataFrames with timestamp columns. It automatically converts timestamp columns to
    datetime format based on the time_format parameter.

    Handles the following columns:
    - timestamp: Converted based on time_format parameter
    - startDate, endDate, date, lastUpdated, startTime, endTime: Auto-detects format

    Args:
        func: The function to decorate

    Returns:
        Wrapped function that processes timestamps in the result DataFrame
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Get the result DataFrame from the original function
        df = func(*args, **kwargs)

        # Check if the result is a DataFrame
        if isinstance(df, pd.DataFrame):
            # Get time_format from kwargs if it exists, otherwise use default
            time_format = kwargs.get('time_format')

            # Convert timestamp column based on time_format
            if 'timestamp' in df.columns:
                if time_format in ['milliseconds', 'ms']:
                    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                elif time_format in ['iso', 'iso8601']:
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                else:
                    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

            # Helper function to convert date columns with auto-detection
            def convert_date_column(column_name):
                if column_name in df.columns:
                    try:
                        # First, try to convert as numeric (milliseconds)
                        numeric_values = pd.to_numeric(df[column_name], errors='coerce')
                        if not numeric_values.isna().all():
                            # If successfully converted to numeric, treat as milliseconds
                            df[column_name] = pd.to_datetime(numeric_values, unit='ms', errors='coerce')
                        else:
                            # If not numeric, treat as ISO string format
                            df[column_name] = pd.to_datetime(df[column_name], errors='coerce')
                    except Exception:
                        # Fallback: treat as ISO string format
                        df[column_name] = pd.to_datetime(df[column_name], errors='coerce')

            # Convert all date-related columns using auto-detection
            date_columns = ['startDate', 'endDate', 'date', 'lastUpdated', 'startTime', 'endTime']
            for column in date_columns:
                convert_date_column(column)

        return df

    return wrapper