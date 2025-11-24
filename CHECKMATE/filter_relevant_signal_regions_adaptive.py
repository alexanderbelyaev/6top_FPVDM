
import os
import pandas as pd

def filter_signal_regions(base_path, output_base,
                          prefix="fpvdm_",
                          min_threshold=0.05, min_keep=4, max_keep=20):
    """
    Parse total_results.txt in each 'evaluation/' subfolder of base_path and extract
    top SRs by rexpcons, keeping between min_keep and max_keep entries per point.

    Saves output to output_base/folder/filtered_regions.txt

    Args:
        base_path (str): Path containing model result folders
        output_base (str): Where to save filtered files
        prefix (str): Only process folders starting with this prefix
        min_threshold (float): Minimum rexpcons value to keep
        min_keep (int): Minimum number of SRs to retain
        max_keep (int): Maximum number of SRs to retain
    """
    summary = []

    for folder in sorted(os.listdir(base_path)):
        if not folder.startswith(prefix):
            continue

        input_path = os.path.join(base_path, folder, "evaluation", "total_results.txt")
        output_folder = os.path.join(output_base, folder)
        output_path = os.path.join(output_folder, "filtered_regions.txt")

        if not os.path.isfile(input_path):
            continue

        try:
            df = pd.read_csv(input_path, sep='\s+', comment="#")

            # Sort by rexpcons descending
            df = df.sort_values("rexpcons", ascending=False)

            # Apply minimum threshold
            df_filtered = df[df["rexpcons"] > min_threshold]

            # Ensure between min_keep and max_keep
            if len(df_filtered) < min_keep:
                df_filtered = df.head(min_keep)
            elif len(df_filtered) > max_keep:
                df_filtered = df_filtered.head(max_keep)

            # Final columns to keep
            df_filtered = df_filtered[["analysis", "sr", "b", "db", "s", "ds", "rexpcons"]]

            os.makedirs(output_folder, exist_ok=True)
            df_filtered.to_csv(output_path, index=False, sep="\t", float_format="%.5g")

            summary.append((folder, len(df_filtered)))

        except Exception as e:
            summary.append((folder, f"Error: {e}"))

    return summary


if __name__ == "__main__":
    # Hardcoded settings
    base_path = "/home/belyaev/packages/CHECKMATE/checkmate2/results"
    output_base = "./filtered_regions"

    # Folder prefix and filtering config
    folder_prefix = "fpvdm_"
    min_threshold = 0.01
    min_keep = 10
    max_keep = 10

    results = filter_signal_regions(
        base_path,
        output_base,
        prefix=folder_prefix,
        min_threshold=min_threshold,
        min_keep=min_keep,
        max_keep=max_keep
    )

    print("\nSummary:")
    for folder, status in results:
        print(f"{folder}: {status}")
