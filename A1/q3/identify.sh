#!/bin/bash
# identify.sh - Identify global schema (Stage 1)
# Usage: bash identify.sh <database_graphs> <output_schema_file>

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/env.sh"

if [ "$#" -lt 2 ]; then
    echo "Usage: bash identify.sh <path_graph_dataset> <path_discriminative_subgraphs>"
    exit 1
fi

INPUT_GRAPHS=$1
OUTPUT_FILE=$2

echo "=============================================="
echo "Part 3: Identifying Features (Global Schema)"
echo "=============================================="
echo "Input: $INPUT_GRAPHS"
echo "Output: $OUTPUT_FILE"

python3 "$SCRIPT_DIR/identify_features.py" "$INPUT_GRAPHS" "$OUTPUT_FILE"

if [ $? -eq 0 ]; then
    echo "Success: Schema saved to $OUTPUT_FILE"
else
    echo "Error: Feature identification failed."
    exit 1
fi