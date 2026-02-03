#!/bin/bash
if [ "$#" -ne 2 ]; then
    echo "Usage: bash q1_2.sh <uni_items> <txns>"
    exit 1
fi

UNI="$1"
TXNS="$2"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT="$SCRIPT_DIR/generated_transactions.dat"

python3 "$SCRIPT_DIR/generate_dataset.py" "$UNI" "$TXNS" "$OUTPUT"

echo "Dataset generated: $OUTPUT"
