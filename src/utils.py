import pandas as pd

def safe_extract_indicator_value(series_or_value, default_display="N/A"):
    try:
        if hasattr(series_or_value, 'iloc'):
            if len(series_or_value) > 0:
                value = series_or_value.iloc[0]
            else:
                return default_display
        else:
            value = series_or_value
        if pd.isna(value):
            return default_display
        return float(value)
    except (IndexError, TypeError, ValueError):
        return default_display
