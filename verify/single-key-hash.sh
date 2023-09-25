#!/bin/bash

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 /path/to/your/key/directory"
    exit 1
fi

directory="$1"

if [ ! -d "$directory" ]; then
    echo "Error: Directory does not exist."
    exit 1
fi

output_file="single-key-hashes.txt"

echo "Generating SHA-256 hashes for all key files in '$directory'..."
find "$directory" -type f -exec sha256sum {} \; > "$output_file"
echo "SHA-256 hashes for individual files saved to $output_file."
