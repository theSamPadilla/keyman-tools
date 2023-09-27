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
# Iterate through files in ascending order of "i"
for file in "$directory"/keystore-m_12381_3600_*.json; do
    i=$(basename "$file" | awk -F'_' '{print $4}' | awk -F'-' '{print $1}')
    echo "Calculating hash for keystore $file with index = $i"
    
    hash=$(sha256sum "$file")
    hash="${hash/\/\//\/}"  # Replace double slashes with a single slash in the hash output
    
    echo "$hash" >> "$output_file"
    
done
echo "SHA-256 hashes for individual files saved to $output_file."
