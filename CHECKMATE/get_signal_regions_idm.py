import os
import pandas as pd

base_dir =  os.path.expandvars('$HOME/packages/CHECKMATE/checkmate2/results')
pattern_prefix = "i2hdm_100k_mh"
txt_path_suffix = "evaluation/best_signal_regions.txt"

all_idm = []
idm_number=10

# Go through each relevant folder
for folder in os.listdir(base_dir):
    if folder.startswith(pattern_prefix):
        txt_file_path = os.path.join(base_dir, folder, txt_path_suffix)
        if os.path.isfile(txt_file_path):
            try:
                df = pd.read_csv(txt_file_path, sep=r'\s+')
                df["source_folder"] = folder
                idm_local = df.sort_values(by="rexpcons", ascending=False).head(idm_number)
                all_idm.append(idm_local)
            except Exception as e:
                print(f"Failed to read {txt_file_path}: {e}")

# Combine all idm-5s from all folders
if not all_idm:
    print("No files found or parsed.")
    exit()

combined_df = pd.concat(all_idm, ignore_index=True)

# Deduplicate by (analysis, sr), keeping row with highest rexpcons
unique_best = combined_df.sort_values(by="rexpcons", ascending=False).drop_duplicates(subset=["analysis", "sr"])

# Display or save results
print("\nFinal deduplicated list of idm (analysis, sr) pairs:")
print(unique_best[["source_folder", "analysis", "sr", "rexpcons"]])

# Optional: Save
unique_best.to_csv("idm_100k_analysis_signal_regions_combined.csv", index=False)
