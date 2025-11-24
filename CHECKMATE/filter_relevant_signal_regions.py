
import os
import pandas as pd

def filter_signal_regions(base_path, startname, output_base, r_threshold=0.15):
    """
    Parse total_results.txt in each 'evaluation/' subfolder of base_path and extract
    SRs with rexpcons > r_threshold.

    Saves output to output_base/folder/filtered_regions.txt

    Args:
        base_path (str): Path containing subfolders like fpvdm_Mtp*DMV*
        output_base (str): Path where output folders and files will be written
        r_threshold (float): Threshold on rexpcons to select relevant SRs
    """
    summary = []

    for folder in sorted(os.listdir(base_path)):
        if not folder.startswith(startname):
            continue

        input_path = os.path.join(base_path, folder, "evaluation", "total_results.txt")
        output_folder = os.path.join(output_base, folder)
        output_path = os.path.join(output_folder, "filtered_regions.txt")

        if not os.path.isfile(input_path):
            continue

        try:
            df = pd.read_csv(input_path, sep='\\s+', comment="#")
            df_filtered = df[df['rexpcons'] > r_threshold]

            if df_filtered.empty:
                continue

            df_filtered = df_filtered[["analysis", "sr", "b", "db", "s", "ds", "rexpcons"]]

            os.makedirs(output_folder, exist_ok=True)
            df_filtered.to_csv(output_path, index=False, sep="\t", float_format="%.5g")

            summary.append((folder, len(df_filtered)))

        except Exception as e:
            summary.append((folder, f"Error: {e}"))

    return summary


if __name__ == "__main__":
    # Hardcoded source and output paths
    base_path = "/home/belyaev/packages/CHECKMATE/checkmate2/results"
    output_base = "./filtered_regions"
    threshold = 0.15

    results = filter_signal_regions(base_path,"fpvdm_", output_base, r_threshold=threshold)

    print("\nSummary:")
    for folder, status in results:
        print(f"{folder}: {status}")
