
import pandas as pd
from pathlib import Path
import importlib.util
import sys

# Load external module
module_path = Path("combine_signal_regions.py").resolve()
spec = importlib.util.spec_from_file_location("combine_signal_regions", module_path)
combine_signal_regions = importlib.util.module_from_spec(spec)
sys.modules["combine_signal_regions"] = combine_signal_regions
spec.loader.exec_module(combine_signal_regions)


def load_signal_regions_from_file(file_path):
    return pd.read_csv(file_path, sep="\t")


def combo_r(sr_list, lumi_factor):
    payload = [{'s0': row['s'], 'ds0': row['ds'], 'b0': row['b'], 'db0': row['db']} for _, row in sr_list.iterrows()]
    return combine_signal_regions.combine_signal_regions(payload, [lumi_factor])[0]['r_exp_cons']


def find_best_combination(df, lumi_factor):
    best_r = -1
    best_combo = pd.DataFrame()
    best_atlas_r = -1
    best_cms_r = -1

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
        r = combo_r(combo, lumi_factor)
        if r > best_atlas_r:
            best_atlas_r = r

    cms_1908 = df[df['analysis'] == 'cms_1908_04722']
    cms_sus = df[df['analysis'] == 'cms_sus_19_005']
    cms_combos = []
    if not cms_1908.empty: cms_combos.append(cms_1908)
    if not cms_sus.empty: cms_combos.append(cms_sus)
    grouped_cms = set(cms_1908.index).union(cms_sus.index)
    for i in df[(df['analysis'].str.startswith('cms_')) & (~df.index.isin(grouped_cms))].index:
        cms_combos.append(df.loc[[i]])
    for combo in cms_combos:
        r = combo_r(combo, lumi_factor)
        if r > best_cms_r:
            best_cms_r = r

    for combo_a in atlas_combos:
        for combo_c in cms_combos:
            combined = pd.concat([combo_a, combo_c])
            r = combo_r(combined, lumi_factor)
            if r > best_r:
                best_r = r
                best_combo = combined

    return best_r, best_combo, best_atlas_r, best_cms_r


def process_single_file(file_path, lumi_factor=1):
    df = load_signal_regions_from_file(file_path)
    if df.empty:
        return None

    # Recompute best individual SR using current lumi_factor
    best_single_r = -1
    best_single_label = ""
    for _, row in df.iterrows():
        payload = [{'s0': row['s'], 'ds0': row['ds'], 'b0': row['b'], 'db0': row['db']}]
        r_val = combine_signal_regions.combine_signal_regions(payload, [lumi_factor])[0]['r_exp_cons']
        if r_val > best_single_r:
            best_single_r = r_val
            best_single_label = f"{row['analysis']}:{row['sr']}"
    global_max_r = best_single_r
    global_max_label = best_single_label

    best_r, best_combo, best_atlas_r, best_cms_r = find_best_combination(df, lumi_factor)

    print("\n=== DEBUG for", file_path, "===")
    print("Best individual SR:", global_max_label, "r_exp_cons =", global_max_r)
    print("Best ATLAS-only r_exp_cons =", best_atlas_r)
    print("Best CMS-only r_exp_cons =", best_cms_r)
    print("Best ATLAS+CMS combination:")
    for _, sr in best_combo.iterrows():
        print(" -", sr['analysis'], sr['sr'], f"s={sr['s']}, ds={sr['ds']}, b={sr['b']}, db={sr['db']}")
    print("Combined r_exp_cons =", best_r)

    return {
        'model_point': file_path.parent.name,
        'global_max_label': global_max_label,
        'global_max_r': global_max_r,
        'best_atlas_r': best_atlas_r,
        'best_cms_r': best_cms_r,
        'best_comb_r': best_r,
        'best_comb_regions': [(row['analysis'], row['sr']) for _, row in best_combo.iterrows()]
    }


if __name__ == "__main__":
    test_file = Path("filtered_regions/fpvdm_Mtp2000DMV100/filtered_regions.txt")
    result = process_single_file(test_file, lumi_factor=22)
    if result:
        print("\nResult summary:", result)
