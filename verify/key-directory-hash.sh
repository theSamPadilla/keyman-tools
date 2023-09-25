#!/bin/bash

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 /path/to/your/key/directory"
    exit 1
fi

source_directory="$1"

if [ ! -d "$source_directory" ]; then
    echo "Error: Directory does not exist."
    exit 1
fi

output_file="whole-directory-hash.txt"

echo "Calculating SHA-256 hashes for files in '$source_directory'..."
find "$source_directory" -type f -exec sha256sum {} \; | sha256sum > $output_file
echo "SHA-256 hashes aggregated and saved to $output_file."
