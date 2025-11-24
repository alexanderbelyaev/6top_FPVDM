#!/usr/bin/env bash
set -euo pipefail

TEMPLATE_FILE="FPVDM_TOP.dat"
PYTHIA_TEMPLATE="pythia8card.in"
LHE_SOURCE_DIR="./batch_results"
CHECKMATE_EXEC="$HOME/packages/CHECKMATE/checkmate2/bin/CM"
MAX_PARALLEL=4

[[ -f "$TEMPLATE_FILE" ]] || { echo "ERROR: '$TEMPLATE_FILE' missing"; exit 1; }
[[ -f "$PYTHIA_TEMPLATE" ]] || { echo "ERROR: '$PYTHIA_TEMPLATE' missing"; exit 1; }
[[ -x "$CHECKMATE_EXEC" ]] || { echo "ERROR: CheckMATE binary not found at $CHECKMATE_EXEC"; exit 1; }

mapfile -t combos < <(find "$LHE_SOURCE_DIR" -name "pp_TpTp_FPVDM-Mtp*DMV*DM*.lhe.gz" \
  | grep -oP "Mtp\d+DMV\d+" | sort -u)

job_pids=()

for combo in "${combos[@]}"; do
    Mtp=${combo#Mtp}; Mtp=${Mtp%DMV*}
    DMV=${combo#*DMV}
    tag="$combo"
    model_name="fpvdm_${combo}"

    echo "-> Processing $tag"

    lhe_file=$(find "$LHE_SOURCE_DIR" -name "pp_TpTp_FPVDM-${combo}DM*.lhe.gz" | head -n1)
    if [[ -z "$lhe_file" || ! -f "$lhe_file" ]]; then
        echo "WARNING: LHE file not found for $combo - skipping."
        continue
    fi

    run_file="run_${tag}.dat"
    cp "$TEMPLATE_FILE" "$run_file"
    sed -i "s/^Name:.*/Name: $model_name/" "$run_file"
    sed -i "s|pythia8card\.in|pythia8card_1.in|" "$run_file"

    scratch_dir=$(mktemp -d -p . tmp_run_${tag}_XXXX)
    cp "$PYTHIA_TEMPLATE" "$scratch_dir/pythia8card_1.in"
    sed -i "s|Beams:LHEF *= *file\.lhe\.gz|Beams:LHEF = file1.lhe.gz|" "$scratch_dir/pythia8card_1.in"
    ln -s "$(realpath "$lhe_file")" "$scratch_dir/file1.lhe.gz"
    cp "$run_file" "$scratch_dir/"

    (
        cd "$scratch_dir"
        "$CHECKMATE_EXEC" "$run_file" > "../log_${tag}.txt" 2>&1 </dev/null
        cd ..
        rm -rf "$scratch_dir" "$run_file"
        echo "-> Finished $tag"
    ) &

    job_pids+=( $! )

    # Throttle parallelism
    while (( $(jobs -rp | wc -l) >= MAX_PARALLEL )); do
        sleep 1
    done
done

# Wait for all jobs to complete
wait

echo "All runs completed."
