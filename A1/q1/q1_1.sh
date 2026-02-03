#!/bin/bash
if [ "$#" -ne 4 ]; then
    echo "Usage: bash q1_1.sh <apriori_exe> <fp_exe> <dataset> <output_dir>"
    exit 1
fi

APRIORI="$1"
FP="$2"
DATASET="$3"
OUT="$4"

mkdir -p "$OUT"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Execute experiments
python3 "$SCRIPT_DIR/run_experiments.py" "$APRIORI" "$FP" "$DATASET" "$OUT"
