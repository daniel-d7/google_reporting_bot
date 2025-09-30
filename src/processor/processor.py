"""Data processing and formatting module."""
import pandas as pd
import numpy as np
from typing import List

from ..utils import get_logger


logger = get_logger(__name__)


def pivot_kpi(data: pd.DataFrame) -> pd.DataFrame:
    """
    Pivot KPI data by month and country.
    
    Args:
        data: DataFrame with month, country, realsales, and gmv columns
        
    Returns:
        Aggregated DataFrame for current month
    """
    data['month'] = pd.to_datetime(data['month'])
    data['realsales'] = pd.to_numeric(data['realsales'], errors='coerce')
    data['gmv'] = pd.to_numeric(data['gmv'], errors='coerce')
    
    current_month = pd.Timestamp.now().replace(day=1).strftime('%Y-%m-%d')
    filtered = data[data['month'] == current_month]
    
    result = filtered.groupby('country', as_index=False)[['realsales', 'gmv']].sum()
    
    logger.debug(f"Pivoted KPI data for {current_month}: {len(result)} countries")
    return result


def calc_achievement_vs_target(data: pd.DataFrame, target: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate achievement vs target with gap analysis.
    
    Args:
        data: Actual performance data DataFrame
        target: Target data DataFrame
        
    Returns:
        DataFrame with achievement percentages and gaps
    """
    merged = (
        pd.merge(data, target, on='country', how='left', suffixes=('_actual', '_target'))
          .fillna(0)
    )
    
    # Convert to numeric (handle potential string values in target)
    cols_to_convert = ['gmv_actual', 'gmv_target', 'realsales_actual', 'realsales_target']
    for col in cols_to_convert:
        if col in merged.columns:
            merged[col] = merged[col].astype(str).str.replace(',', '').astype(float)
    
    # Calculate achievement percentages
    merged['realsales_achievement'] = np.where(
        merged['realsales_target'] != 0,
        merged['realsales_actual'] / merged['realsales_target'] * 100,
        0
    )
    merged['gmv_achievement'] = np.where(
        merged['gmv_target'] != 0,
        merged['gmv_actual'] / merged['gmv_target'] * 100,
        0
    )
    
    # Calculate gaps
    merged['realsales_gap'] = np.where(
        merged['realsales_target'] != 0,
        merged['realsales_actual'] - merged['realsales_target'],
        0
    )
    merged['gmv_gap'] = np.where(
        merged['gmv_target'] != 0,
        merged['gmv_actual'] - merged['gmv_target'],
        0
    )
    
    # Round achievement percentages
    for col in ['realsales_achievement', 'gmv_achievement']:
        merged[col] = pd.to_numeric(merged[col], errors='coerce').round(2)
    
    # Calculate total row
    total_row = merged.select_dtypes('number').sum()
    total_row['country'] = 'Total'
    
    total_row['realsales_achievement'] = (
        total_row['realsales_actual'] / total_row['realsales_target'] * 100
        if total_row['realsales_target'] != 0 else np.nan
    )
    total_row['gmv_achievement'] = (
        total_row['gmv_actual'] / total_row['gmv_target'] * 100
        if total_row['gmv_target'] != 0 else np.nan
    )
    
    total_row['realsales_achievement'] = round(total_row['realsales_achievement'], 2)
    total_row['gmv_achievement'] = round(total_row['gmv_achievement'], 2)
    
    merged = pd.concat([merged, pd.DataFrame([total_row])], ignore_index=True)
    
    # Reorder columns
    new_order = [
        'country', 'gmv_achievement', 'gmv_actual', 'gmv_gap', 
        'realsales_achievement', 'realsales_actual', 'realsales_gap'
    ]
    merged = merged[new_order]
    
    # Rename columns with friendly names
    merged = merged.rename(columns={
        'country': ' Country ',
        'gmv_achievement': ' %GMV vs KPI ',
        'gmv_actual': ' GMV Actual ',
        'gmv_gap': ' GMV Gap ',
        'realsales_achievement': ' %RS vs KPI ',
        'realsales_actual': ' RS Actual ',
        'realsales_gap': '  RS Gap  '
    })
    
    # Format numbers
    merged = _format_dataframe(merged)
    
    logger.debug(f"Calculated achievement vs target for {len(merged)-1} countries")
    return merged


def formatter(data_frame: pd.DataFrame) -> pd.DataFrame:
    """
    Format DataFrame with proper number and percentage formatting.
    
    Args:
        data_frame: DataFrame to format
        
    Returns:
        Formatted DataFrame
    """
    return _format_dataframe(data_frame)


def _format_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Internal helper to format DataFrame columns.
    
    Args:
        df: DataFrame to format
        
    Returns:
        Formatted DataFrame
    """
    # Define column patterns
    int_col_patterns = ['Actual', 'Gap', 'RS Actual', 'RS Gap', 'GMV Actual', 'GMV Gap']
    pct_col_patterns = ['%Ads', '%Promo', '%GMV vs KPI', '%RS vs KPI']
    
    # Format integer columns
    for pattern in int_col_patterns:
        matching_cols = [col for col in df.columns if pattern in col]
        for col in matching_cols:
            df[col] = df[col].apply(
                lambda x: f'{x:,.0f}' if pd.notna(x) else ''
            )
    
    # Format percentage columns
    for pattern in pct_col_patterns:
        matching_cols = [col for col in df.columns if pattern in col]
        for col in matching_cols:
            df[col] = df[col].apply(
                lambda x: f'{x:,.1f}%' if pd.notna(x) else ''
            )
    
    return df
