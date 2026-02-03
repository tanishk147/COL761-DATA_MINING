#!/bin/bash
# generate_candidates.sh - Two-Stage Filtering (Histogram + VF2)
# Usage: bash generate_candidates.sh <db_vecs> <query_vecs> <output_file>

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/env.sh"

if [ "$#" -lt 3 ]; then
    echo "Usage: bash generate_candidates.sh <db_features> <query_features> <output_file>"
    exit 1
fi

DB_FEATS=$1
QUERY_FEATS=$2
OUTPUT_FILE=$3


MUTA_DB="$SCRIPT_DIR/q3_datasets/Mutagenicity/graphs.txt"
MUTA_QUERY="$SCRIPT_DIR/query_dataset/muta_final_visible"
NCI_DB="$SCRIPT_DIR/q3_datasets/NCI-H23/graphs.txt"
NCI_QUERY="$SCRIPT_DIR/query_dataset/nci_final_visible"

if [ -n "$DB_GRAPHS" ]; then
   REAL_DB="$DB_GRAPHS"
   REAL_QUERY="$QUERY_GRAPHS"
   echo "Using paths from environment variables."
elif [ -f "$MUTA_DB" ]; then
   echo "Auto-detected Dataset: Mutagenicity"
   REAL_DB="$MUTA_DB"
   REAL_QUERY="$MUTA_QUERY"
elif [ -f "$NCI_DB" ]; then
   echo "Auto-detected Dataset: NCI-H23"
   REAL_DB="$NCI_DB"
   REAL_QUERY="$NCI_QUERY"
else
   echo "Error: Could not locate raw graph files. Ensure 'q3_datasets' is in the script directory or set DB_GRAPHS/QUERY_GRAPHS env vars."
   exit 1
fi

echo "Running Two-Stage Filter..."
# Arguments: <db_vecs> <q_vecs> <db_raw> <q_raw> <output>
python3 "$SCRIPT_DIR/smart_filter.py" "$DB_FEATS" "$QUERY_FEATS" "$REAL_DB" "$REAL_QUERY" "$OUTPUT_FILE"