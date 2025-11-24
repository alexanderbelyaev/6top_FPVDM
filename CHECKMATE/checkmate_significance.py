import pandas as pd
import numpy as np
import os

def asimov_significance(s, b):
    if b <= 0:
        return 0.0
    if s <= 0:
        return 0.0
    return np.sqrt(2 * ((s + b) * np.log(1 + s / b) - s))

def cowan_significance(s, b, db):
    if b <= 0 or db <= 0 or s <= 0:
        return 0.0
    sb2 = db**2
    term1 = (s + b) * np.log(((s + b) * (b + sb2)) / (b**2 + (s + b) * sb2))
    term2 = (b**2 / sb2) * np.log(1 + (sb2 * s) / (b * (b + sb2)))
    return np.sqrt(2 * (term1 - term2))

def main():
    # Update the path if needed
    file_path = os.path.expanduser('~/packages/CHECKMATE/checkmate2/results/fpvdm_Mtp1500DMV300/evaluation/best_signal_regions.txt')
    
    try:
        df = pd.read_csv(file_path, sep=r'\s+')
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return

    # Find the row with highest expected r-value
    best_row = df.loc[df['rexpcons'].idxmax()]
    s = best_row['s']
    b = best_row['b']
    db = best_row['db']
    s95exp = best_row['s95exp']
    rexp = best_row['rexpcons']

    z_asimov = asimov_significance(s, b)
    z_cowan = cowan_significance(s, b, db)

    # Print results
    print("Best Signal Region (based on expected r-value):")
    print(f"  Analysis:             {best_row['analysis']}")
    print(f"  Signal Region:        {best_row['sr']}")
    print(f"  Signal (s):           {s:.4f}")
    print(f"  Background (b):       {b:.4f}")
    print(f"  Uncertainty on b:     {db:.4f}")
    print(f"  s95exp:               {s95exp:.4f}")
    print(f"  rexpcons (CheckMATE): {rexp:.5f}")
    print("")
    print("Derived Significance:")
    print(f"  Asimov Significance (no db):       {z_asimov:.4f}")
    print(f"  Cowan Profile Likelihood (with db): {z_cowan:.4f}")

if __name__ == "__main__":
    main()
