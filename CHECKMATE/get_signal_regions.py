import os
import pandas as pd

base_dir =  os.path.expandvars('$HOME/packages/CHECKMATE/checkmate2/results')
pattern_prefix = "fpvdm_Mtp"
txt_path_suffix = "evaluation/best_signal_regions.txt"

all_top = []
top_number=5

# Go through each relevant folder
for folder in os.listdir(base_dir):
    if folder.startswith(pattern_prefix):
        txt_file_path = os.path.join(base_dir, folder, txt_path_suffix)
        if os.path.isfile(txt_file_path):
            try:
                df = pd.read_csv(txt_file_path, sep=r'\s+')
                df["source_folder"] = folder
                top_local = df.sort_values(by="rexpcons", ascending=False).head(top_number)
                all_top.append(top_local)
            except Exception as e:
                print(f"Failed to read {txt_file_path}: {e}")

# Combine all top-5s from all folders
if not all_top:
    print("No files found or parsed.")
    exit()

combined_df = pd.concat(all_top, ignore_index=True)

# Deduplicate by (analysis, sr), keeping row with highest rexpcons
unique_best = combined_df.sort_values(by="rexpcons", ascending=False).drop_duplicates(subset=["analysis", "sr"])

# Display or save results
print("\nFinal deduplicated list of top (analysis, sr) pairs:")
print(unique_best[["source_folder", "analysis", "sr", "rexpcons"]])

# Optional: Save
unique_best.to_csv("top_analysis_signal_regions_combined.csv", index=False)
