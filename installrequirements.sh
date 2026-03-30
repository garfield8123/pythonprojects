#!/bin/bash

ROOT_DIR="${1:-.}"
OUTPUT_FILE="requirements.txt"

> "$OUTPUT_FILE"  # clear file

find "$ROOT_DIR" -type f -name "requirements.txt" | while read -r file; do
    echo "# From $file" >> "$OUTPUT_FILE"
    cat "$file" >> "$OUTPUT_FILE"
    echo -e "\n" >> "$OUTPUT_FILE"
done

echo "Combined requirements saved to $OUTPUT_FILE"