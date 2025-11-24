import os
import pandas as pd
import numpy as np
from pathlib import Path
import importlib.util
import sys
import re

# Load combine_signal_regions module
module_path = Path("combine_signal_regions.py").resolve()
spec = importlib.util.spec_from_file_location("combine_signal_regions", module_path)
combine_signal_regions = importlib.util.module_from_spec(spec)
sys.modules["combine_signal_regions"] = combine_signal_regions
spec.loader.exec_module(combine_signal_regions)


def load_signal_regions_from_file(file_path):
    return pd.read_csv(file_path, sep="\t")


def extract_mtp_dmv(folder_name):
    match = re.match(r"fpvdm_(\d+)DMV([0-9]+(?:\.[0-9]+)?)", folder_name)
#    print(match)
#    print(folder_name)
    if match:
        return int(match.group(1)), float(match.group(2))
    return None, None


def process_all_filtered_regions(root_dir="filtered_regions", lumi_factor=1):
    results = []
    header = ["Mtp", "DMV", "Lumi", "Best_Individual", "Best_ATLAS", "Best_CMS", "Best_Combined", "Overall_Best"]
    print("\t".join(header))
    for path in Path("filtered_regions").glob("*/filtered_regions.txt"):
        df = load_signal_regions_from_file(path)
        if df.empty:
            continue

        def combo_r(sr_list):
            payload = [
                {'s0': row['s'], 'ds0': row['ds'], 'b0': row['b'], 'db0': row['db']} for _, row in sr_list.iterrows()
            ]
            return combine_signal_regions.combine_signal_regions(payload, [lumi_factor])[0]['r_exp_cons']

#        best_single_row = df.loc[df['rexpcons'].idxmax()]
#        global_max_r = best_single_row['rexpcons']

        best_single_r = -1
        for _, row in df.iterrows():
    	    payload = [{'s0': row['s'], 'ds0': row['ds'], 'b0': row['b'], 'db0': row['db']}]
    	    r_val = combine_signal_regions.combine_signal_regions(payload, [lumi_factor])[0]['r_exp_cons']
    	    if r_val > best_single_r:
                best_single_r = r_val
        global_max_r = best_single_r





        best_atlas_r = -1
        best_atlas_combo = pd.DataFrame()
        atlas_2004 = df[df['analysis'] == 'atlas_2004_14060']
        atlas_2101 = df[df['analysis'] == 'atlas_2101_01629']
        atlas_2211 = df[df['analysis'] == 'atlas_2211_08028']
        atlas_2211_0lep = atlas_2211[atlas_2211['sr'].isin(['SR-Gtb-C','SR-Gtb-M','SR-Gtb-B','SR-Gbb-C','SR-Gbb-M','SR-Gtt-0L-B'])]
        atlas_2211_1lep = atlas_2211[atlas_2211['sr'].str.startswith('SR-Gtt-1L')]
        atlas_combos = []
        if not atlas_2004.empty: atlas_combos.append(atlas_2004)
        if not atlas_2101.empty: atlas_combos.append(atlas_2101)
        if not atlas_2211_0lep.empty and not atlas_2211_1lep.empty:
            for i in atlas_2211_0lep.index:
                for j in atlas_2211_1lep.index:
                    atlas_combos.append(df.loc[[i, j]])
        grouped_atlas = set(atlas_2004.index).union(atlas_2101.index).union(atlas_2211.index)
        for i in df[(df['analysis'].str.startswith('atlas_')) & (~df.index.isin(grouped_atlas))].index:
            atlas_combos.append(df.loc[[i]])
        for combo in atlas_combos:
            r = combo_r(combo)
            if r > best_atlas_r:
                best_atlas_r = r
                best_atlas_combo = combo

        best_cms_r = -1
        best_cms_combo = pd.DataFrame()
        cms_1908 = df[df['analysis'] == 'cms_1908_04722']
        cms_sus = df[df['analysis'] == 'cms_sus_19_005']
        cms_combos = []
        if not cms_1908.empty: cms_combos.append(cms_1908)
        if not cms_sus.empty: cms_combos.append(cms_sus)
        grouped_cms = set(cms_1908.index).union(cms_sus.index)
        for i in df[(df['analysis'].str.startswith('cms_')) & (~df.index.isin(grouped_cms))].index:
            cms_combos.append(df.loc[[i]])
        for combo in cms_combos:
            r = combo_r(combo)
            if r > best_cms_r:
                best_cms_r = r
                best_cms_combo = combo

        combined = pd.concat([best_atlas_combo, best_cms_combo])
        best_comb_r = combo_r(combined)
        overall_best = max(global_max_r, best_atlas_r, best_cms_r, best_comb_r)

        mtp, dmv = extract_mtp_dmv(path.parent.name)
        row = [mtp, dmv, lumi_factor, global_max_r, best_atlas_r, best_cms_r, best_comb_r, overall_best]
        formatted_row = [f"{x:.4g}" if isinstance(x, float) else str(x) for x in row]
        print("\t".join(formatted_row))
        results.append(formatted_row)

    df_out = pd.DataFrame(results, columns=header)
    df_out.sort_values(["Mtp", "DMV"], inplace=True)
    df_out.to_csv("summary_results_HL_LHC.txt", sep="\t", index=False)
    print("\nResults written to summary_results_HL_LHC.txt")


if __name__ == "__main__":
    process_all_filtered_regions("filtered_regions", lumi_factor=3000./139.)
