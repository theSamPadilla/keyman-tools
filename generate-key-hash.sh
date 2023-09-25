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

echo "Calculating SHA-256 hashes for files in '$source_directory'..."
find "$source_directory" -type f -exec sha256sum {} \; | sha256sum > key_directory_hash.txt
echo "SHA-256 hashes aggregated and saved to key_directory_hash.txt."
