import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import re
from liquidlib.adapters.prediction import predict_property

# Helper to sanitize filenames
SAFE_FILENAME = lambda s: re.sub(r'[^A-Za-z0-9_.-]', '_', str(s))

# Load data
csv_path = 'data/opentrons_pippetting_recommendations.csv'
df = pd.read_csv(csv_path)

# Extract base liquid name and percentage
liquid_info = df['Liquid'].str.extract(r'(?P<base>.+?)\s+(?P<percent>\d+)%')
df['BaseLiquid'] = liquid_info['base'].str.strip()
df['Percent'] = liquid_info['percent'].astype(float)

# Identify numeric columns
numeric_cols = [col for col in df.columns if df[col].dtype in [float, int] or col in ['Aspiration Rate (µL/s)','Aspiration Delay (s)','Aspiration Withdrawal Rate (mm/s)','Dispense Rate (µL/s)','Dispense Delay (s)','Blowout Rate (µL/s)']]
# Identify boolean columns (object dtype, contains 'yes' or 'no' case-insensitive)
boolean_cols = []
for col in df.columns:
    if df[col].dtype == object:
        lowered = df[col].astype(str).str.lower()
        if lowered.isin(['yes', 'no']).any():
            boolean_cols.append(col)

# Output directory for plots
os.makedirs('analysis_plots', exist_ok=True)

for (base_liquid, pipette) in df[['BaseLiquid', 'Pipette']].drop_duplicates().itertuples(index=False):
    sub = df[(df['BaseLiquid'] == base_liquid) & (df['Pipette'] == pipette)]
    # Plot numeric properties
    for col in numeric_cols:
        if col not in sub: continue
        plt.figure()
        plt.scatter(sub['Percent'], sub[col], label='Data')
        # Fit a polynomial (degree 1 or 2 depending on points)
        if len(sub) > 2:
            deg = 2
        else:
            deg = 1
        try:
            coeffs = np.polyfit(sub['Percent'], sub[col], deg)
            fit_fn = np.poly1d(coeffs)
            x_fit = np.linspace(sub['Percent'].min(), sub['Percent'].max(), 100)
            plt.plot(x_fit, fit_fn(x_fit), '--', label=f'Poly{deg} fit')
        except Exception as e:
            pass
        plt.title(f'{base_liquid} ({pipette}): {col} vs. %')
        plt.xlabel('Percentage')
        plt.ylabel(col)
        plt.legend()
        plt.tight_layout()
        fname = f'analysis_plots/{SAFE_FILENAME(base_liquid)}_{SAFE_FILENAME(pipette)}_{SAFE_FILENAME(col)}_curve.png'
        plt.savefig(fname)
        plt.close()
    # Plot boolean properties
    for col in boolean_cols:
        if col not in sub: continue
        plt.figure()
        y = sub[col].astype(str).str.lower().map({'yes':1, 'no':0})
        plt.step(sub['Percent'], y, where='mid', label='Yes=1, No=0')
        plt.title(f'{base_liquid} ({pipette}): {col} classification vs. %')
        plt.xlabel('Percentage')
        plt.ylabel(col)
        plt.yticks([0,1], ['No','Yes'])
        plt.tight_layout()
        fname = f'analysis_plots/{SAFE_FILENAME(base_liquid)}_{SAFE_FILENAME(pipette)}_{SAFE_FILENAME(col)}_classification.png'
        plt.savefig(fname)
        plt.close()

# Example usage:
if __name__ == "__main__":
    print('Analysis complete. Plots saved in analysis_plots/.')
    # Example: Predict aspiration rate for Glycerol, P300, 90%
    try:
        val = predict_property('Glycerol', 'P300', 90, 'Aspiration Rate (µL/s)')
        print(f"Predicted Aspiration Rate (µL/s) for Glycerol, P300, 90%: {val:.2f}")
        val2 = predict_property('Glycerol', 'P300', 90, 'Touch tip')
        print(f"Predicted Touch tip for Glycerol, P300, 90%: {val2}")
        val3 = predict_property('Glycerol', 'P300', 54, 'Dispense Rate (µL/s)')
        print(f"Predicted Dispense Rate (µL/s) for Glycerol, P300, 54%: {val3:.2f}")
    except Exception as e:
        print(f"Prediction error: {e}") 