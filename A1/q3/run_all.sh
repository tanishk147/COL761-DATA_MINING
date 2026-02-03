#!/bin/bash
# run_all.sh - Run Complete Two-Stage Pipeline (Histogram + Neighborhood + VF2)
# Usage: bash run_all.sh <Mutagenicity|NCI-H23>

if [ "$#" -lt 1 ]; then
    echo "Usage: bash run_all.sh <dataset_name>"
    echo "  dataset_name: 'Mutagenicity' or 'NCI-H23'"
    exit 1
fi

DATASET=$1
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/env.sh"

OUTPUT_DIR="$SCRIPT_DIR/output_$DATASET"
mkdir -p "$OUTPUT_DIR"

if [ "$DATASET" == "Mutagenicity" ]; then
    GRAPHS_FILE="$SCRIPT_DIR/q3_datasets/Mutagenicity/graphs.txt"
    QUERY_FILE="$SCRIPT_DIR/query_dataset/muta_final_visible"
elif [ "$DATASET" == "NCI-H23" ]; then
    GRAPHS_FILE="$SCRIPT_DIR/q3_datasets/NCI-H23/graphs.txt"
    QUERY_FILE="$SCRIPT_DIR/query_dataset/nci_final_visible"
else
    echo "Error: Unknown dataset '$DATASET'. Use 'Mutagenicity' or 'NCI-H23'."
    exit 1
fi

export DB_GRAPHS="$GRAPHS_FILE"
export QUERY_GRAPHS="$QUERY_FILE"

SCHEMA_FILE="$OUTPUT_DIR/schema.json"
DB_VECS="$OUTPUT_DIR/db_vecs.npy"
QUERY_VECS="$OUTPUT_DIR/query_vecs.npy"
CANDIDATES="$OUTPUT_DIR/candidates.dat"
LOG_FILE="$OUTPUT_DIR/run_log.txt"

log() {
    echo "$1" | tee -a "$LOG_FILE"
}

> "$LOG_FILE"

log "========================================================"
log "STARTING PIPELINE FOR: $DATASET"
log "Input DB: $GRAPHS_FILE"
log "Input Query: $QUERY_FILE"
log "Output Dir: $OUTPUT_DIR"
log "========================================================"

log ""
log "[Step 1] Identify Schema (Atom Labels & Degrees)..."
bash "$SCRIPT_DIR/identify.sh" "$GRAPHS_FILE" "$SCHEMA_FILE" 2>&1 | tee -a "$LOG_FILE"

if [ ! -f "$SCHEMA_FILE" ]; then
    log "Error: Schema identification failed."
    exit 1
fi

log ""
log "[Step 2] Convert Database to Histogram Vectors..."
bash "$SCRIPT_DIR/convert.sh" "$GRAPHS_FILE" "$SCHEMA_FILE" "$DB_VECS" 2>&1 | tee -a "$LOG_FILE"

log ""
log "[Step 3] Convert Query to Histogram Vectors..."
bash "$SCRIPT_DIR/convert.sh" "$QUERY_FILE" "$SCHEMA_FILE" "$QUERY_VECS" 2>&1 | tee -a "$LOG_FILE"

log ""
log "[Step 4] Generate Candidates (Histogram -> Neighborhood -> VF2)..."
bash "$SCRIPT_DIR/generate_candidates.sh" "$DB_VECS" "$QUERY_VECS" "$CANDIDATES" 2>&1 | tee -a "$LOG_FILE"

log ""
log "========================================================"
log "PIPELINE COMPLETE"
log "Candidates saved to: $CANDIDATES"
log "========================================================"
log "Stats:"

python3 -c "
import sys
try:
    with open('$CANDIDATES', 'r') as f:
        lines = f.readlines()
    counts = []
    for line in lines:
        if line.startswith('c #'):
            parts = line.strip().split()[2:]
            counts.append(len(parts))
    if counts:
        print(f'  Total Queries: {len(counts)}')
        print(f'  Min Candidates: {min(counts)}')
        print(f'  Max Candidates: {max(counts)}')
        print(f'  Avg Candidates: {sum(counts)/len(counts):.2f}')
    else:
        print('  No candidates found.')
except Exception as e:
    print(f'  Error calculating stats: {e}')
" | tee -a "$LOG_FILE"