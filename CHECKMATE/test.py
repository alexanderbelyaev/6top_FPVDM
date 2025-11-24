import pandas as pd
import numpy as np
from pathlib import Path
import importlib.util
import sys

# Load combine_signal_regions module from user-provided file
module_path = Path("combine_signal_regions.py").resolve()
spec = importlib.util.spec_from_file_location("combine_signal_regions", module_path)
combine_signal_regions = importlib.util.module_from_spec(spec)
sys.modules["combine_signal_regions"] = combine_signal_regions
spec.loader.exec_module(combine_signal_regions)

# Manually defined SRs for testing
manual_data = [
    {"analysis": "atlas_2004_14060", "sr": "SRA-TT", "s": 79.76064292003899, "ds": 6.556284566085885, "b": 3.2, "db": 0.5},
    {"analysis": "atlas_2004_14060", "sr": "SRA-TW", "s": 68.44325158003063, "ds": 6.073367683499853, "b": 5.6, "db": 0.7},
    {"analysis": "atlas_2004_14060", "sr": "SRA-T0", "s": 61.97627010012533, "ds": 5.779314219214005, "b": 17.3, "db": 1.7},
    {"analysis": "cms_sus_19_005", "sr": "3b_loose", "s": 57.8975223801565, "ds": 5.545581739745266, "b": 17.6, "db": 4.0},
    {"analysis": "cms_sus_19_005", "sr": "7j_3b_loose", "s": 43.02477942013958, "ds": 4.780522215247134, "b": 10.9, "db": 3.0}
]

# Convert to DataFrame
manual_df = pd.DataFrame(manual_data)

# Run combination logic directly
payload = [
    {'s0': row['s'], 'ds0': row['ds'], 'b0': row['b'], 'db0': row['db']} for _, row in manual_df.iterrows()
]

result = combine_signal_regions.combine_signal_regions(payload, [1])[0]

# Output results
print("\n=== Manual Cross Check ===")
print("Combined regions:")
for _, row in manual_df.iterrows():
    print(f" - {row['analysis']} {row['sr']}: s={row['s']}, ds={row['ds']}, b={row['b']}, db={row['db']}")
print(f"\nResulting r_exp_cons = {result['r_exp_cons']}")
print("s95exp =", result['s95exp'])
