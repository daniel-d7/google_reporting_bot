import pandas as pd
import numpy as np
from datetime import datetime

def pivot_kpi(data):
    data['month'] = pd.to_datetime(data['month'])
    data['realsales'] = pd.to_numeric(data['realsales'], errors='coerce')
    data['gmv'] = pd.to_numeric(data['gmv'], errors='coerce')
    current_month = pd.Timestamp.now().replace(day=1).strftime('%Y-%m-%d')
    filtered = data[data['month'] == current_month]
    result = filtered.groupby('country', as_index=False)[['realsales', 'gmv']].sum()
    return result

def calc_achievement_vs_target(data: pd.DataFrame, target: pd.DataFrame) -> pd.DataFrame:
    merged = (
        pd.merge(data, target, on='country', how='left', suffixes=('_actual', '_target'))
          .fillna(0)
    )

    # Move conversions here to ensure numerics before calculations (fix potential string issues in target)
    cols_to_convert = ['gmv_actual', 'gmv_target', 'realsales_actual', 'realsales_target']
    for col in cols_to_convert:
        if col in merged.columns:
            merged[col] = merged[col].astype(str).str.replace(',', '').astype(float)

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

    for col in ['realsales_achievement', 'gmv_achievement']:
        merged[col] = pd.to_numeric(merged[col], errors='coerce').round(2)

    total_row = merged.select_dtypes('number').sum()           # sums only numeric cols
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

    new_order = [
    'country', 'gmv_achievement', 'gmv_actual', 'gmv_gap', 
    'realsales_achievement', 'realsales_actual', 'realsales_gap'
    ]

    merged = merged[new_order]

    merged = merged.rename(columns={
        'country': ' Country ',
        'gmv_achievement': ' %GMV vs KPI ',
        'gmv_actual': ' GMV Actual ',
        'gmv_gap': ' GMV Gap ',
        'realsales_achievement': ' %RS vs KPI ',
        'realsales_actual': ' RS Actual ',
        'realsales_gap': '  RS Gap  '
    })

    int_cols = [' GMV Actual ', ' GMV Gap ', ' RS Actual ', '  RS Gap  ']
    pct_cols = [' %GMV vs KPI ', ' %RS vs KPI ']

    for col in int_cols:
        merged[col] = merged[col].apply(
            lambda x: f'{x:,.0f}' if pd.notna(x) else ''
        )

    # Format 57.26 → '57.3%' (blank if NaN)
    for col in pct_cols:
        merged[col] = merged[col].apply(
            lambda x: f'{x:,.1f}%' if pd.notna(x) else ''
        )
    return merged

def formatter(data_frame):
    int_cols = ['GMV Actual', 'GMV Gap', 'RS Actual', 'RS Gap']
    pct_cols = ['%Ads', '%Promo', '%GMV vs KPI', '%RS vs KPI']

    for col in int_cols:
        data_frame[col] = data_frame[col].apply(
            lambda x: f'{x:,.0f}' if pd.notna(x) else ''
        )

    # Format 57.26 → '57.3%' (blank if NaN)
    for col in pct_cols:
        data_frame[col] = data_frame[col].apply(
            lambda x: f'{x:,.1f}%' if pd.notna(x) else ''
        )
    return data_frame