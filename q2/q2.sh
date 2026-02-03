#!/bin/bash

if [ "$#" -ne 5 ]; then
    echo "Usage: bash q2.sh <gspan_binary> <fsg_binary> <gaston_binary> <dataset_file> <output_dir>"
    exit 1
fi

GSPAN_BINARY=$1
FSG_BINARY=$2
GASTON_BINARY=$3
DATASET_FILE=$4
OUTPUT_DIR=$5

# Run the benchmark
python3 benchmark.py "$GSPAN_BINARY" "$FSG_BINARY" "$GASTON_BINARY" "$DATASET_FILE" "$OUTPUT_DIR"

echo "Pipeline execution complete!"