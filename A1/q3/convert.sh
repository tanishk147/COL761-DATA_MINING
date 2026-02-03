#!/bin/bash
# convert.sh - Map graphs to histogram vectors
# Usage: bash convert.sh <graphs_file> <schema_file> <output_npy>

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/env.sh"

if [ "$#" -lt 3 ]; then
    echo "Usage: bash convert.sh <graphs_file> <discriminative_subgraphs> <output_features>"
    exit 1
fi

INPUT_GRAPHS=$1
SCHEMA_FILE=$2   
OUTPUT_FILE=$3

echo "Converting graphs to histogram vectors..."

python3 "$SCRIPT_DIR/convert_to_histogram.py" "$INPUT_GRAPHS" "$SCHEMA_FILE" "$OUTPUT_FILE"