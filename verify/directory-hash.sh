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

# Calculate the hash of the hases only.
# the 'sha25sum <path-to-a-file> command outputs the following: <hash> <path-to-a-file>
# Piping everything to sha256sum causes issues if the path is different.
# The '| cut -d' ' -f1' command filters the output and grabs only the hash
# Effectively calculating only the sum of the hashes.
hash_output=$(find "$source_directory" -type f -exec sha256sum {} \; -type f | sort | cut -d' ' -f1 | sha256sum)

echo "SHA-256 of provided key directory is:" 
echo -e "\033[0m\033[33m$hash_output\033[0m"
echo $hash_output > $output_file
echo -e "\n\nAlso saved hash to $output_file."
