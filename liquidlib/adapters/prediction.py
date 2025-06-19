"""
Prediction utilities for liquid handling parameters.

This module provides functions to predict liquid handling parameters based on
fitted curves from experimental data.
"""

import pandas as pd
import numpy as np
from typing import Union, Optional
import re
import os

# Global data storage
_df: Optional[pd.DataFrame] = None
_numeric_cols: list = []
_boolean_cols: list = []

def _load_data(csv_path: str = 'data/opentrons_pippetting_recommendations.csv') -> None:
    """Load and prepare the CSV data for predictions."""
    global _df, _numeric_cols, _boolean_cols
    
    if _df is not None:
        return  # Data already loaded
    
    # Ensure the csv_path is relative to the package root if using the default
    if csv_path == 'data/opentrons_pippetting_recommendations.csv':
        csv_path = os.path.join(os.path.dirname(__file__), '..', csv_path)
        csv_path = os.path.normpath(csv_path)
    _df = pd.read_csv(csv_path)
    
    # Extract base liquid name and percentage
    liquid_info = _df['Liquid'].str.extract(r'(?P<base>.+?)\s+(?P<percent>\d+)%')
    _df['BaseLiquid'] = liquid_info['base'].str.strip()
    _df['Percent'] = liquid_info['percent'].astype(float)
    
    # Identify numeric columns
    _numeric_cols = [col for col in _df.columns if _df[col].dtype in [float, int] or col in [
        'Aspiration Rate (µL/s)','Aspiration Delay (s)','Aspiration Withdrawal Rate (mm/s)',
        'Dispense Rate (µL/s)','Dispense Delay (s)','Blowout Rate (µL/s)'
    ]]
    
    # Identify boolean columns (object dtype, contains 'yes' or 'no' case-insensitive)
    _boolean_cols = []
    for col in _df.columns:
        if _df[col].dtype == object:
            lowered = _df[col].astype(str).str.lower()
            if lowered.isin(['yes', 'no']).any():
                _boolean_cols.append(col)

def predict_property(base_liquid: str, pipette: str, percent: float, property_name: str) -> Union[float, str]:
    """
    Predict the value of a property for a given base liquid, pipette, and percent concentration.
    
    Uses a polynomial fit (degree 2 if >2 points, else degree 1) on the available data.
    For boolean properties, returns 'Yes' or 'No' based on thresholding the fit at 0.5.

    Args:
        base_liquid: The base liquid name (e.g., 'Glycerol')
        pipette: The pipette type (e.g., 'P20', 'P300', 'P1000')
        percent: The concentration percentage (e.g., 90)
        property_name: The property to predict (column name)

    Returns:
        Predicted value (float for numeric, 'Yes'/'No' for boolean)
        
    Raises:
        ValueError: If no data is available for the specified combination
        ValueError: If the property is not recognized as numeric or boolean
    """
    # Load data if not already loaded
    _load_data()
    
    if _df is None:
        raise ValueError("Failed to load prediction data")
    
    sub = _df[(_df['BaseLiquid'] == base_liquid) & (_df['Pipette'] == pipette)]
    if sub.empty:
        raise ValueError(f"No data for {base_liquid} with pipette {pipette}")
    
    x = sub['Percent']
    y = sub[property_name]

    # Debug print to trace prediction inputs and outputs
    print(f"[DEBUG] predict_property: base_liquid={base_liquid}, pipette={pipette}, percent={percent}, property_name={property_name}")
    print(f"[DEBUG] Data used for fit: x={list(x)}, y={list(y)}")

    if property_name in _boolean_cols:
        y = y.astype(str).str.lower().map({'yes': 1, 'no': 0})
        deg = 2 if len(sub) > 2 else 1
        coeffs = np.polyfit(x, y, deg)
        fit_fn = np.poly1d(coeffs)
        pred = fit_fn(percent)
        result = 'Yes' if pred >= 0.5 else 'No'
        print(f"[DEBUG] Predicted boolean value: {result} (raw={pred})")
        return result
    elif property_name in _numeric_cols:
        deg = 2 if len(sub) > 2 else 1
        coeffs = np.polyfit(x, y, deg)
        fit_fn = np.poly1d(coeffs)
        pred = float(fit_fn(percent))
        print(f"[DEBUG] Predicted numeric value: {pred}")
        return pred
    else:
        raise ValueError(f"Property {property_name} not recognized as numeric or boolean.")

def get_available_combinations() -> list[tuple[str, str]]:
    """
    Get all available base liquid and pipette combinations in the dataset.
    
    Returns:
        List of (base_liquid, pipette) tuples
    """
    _load_data()
    
    if _df is None:
        return []
    
    return _df[['BaseLiquid', 'Pipette']].drop_duplicates().itertuples(index=False)

def get_available_properties() -> dict[str, list[str]]:
    """
    Get all available properties categorized by type.
    
    Returns:
        Dictionary with 'numeric' and 'boolean' keys containing lists of property names
    """
    _load_data()
    
    return {
        'numeric': _numeric_cols.copy(),
        'boolean': _boolean_cols.copy()
    } 