#!/bin/bash

# Use this script to copy a range of key from the key source machine to a different directory.
# Then use the other scripts in this directory to compute the hash of all the
# contents in that directory. You can use this hash to compare against the hash on the 
# machine that is importing the keys.

# Function to check if a directory exists
check_directory_exists() {
    if [ ! -d "$1" ]; then
        echo "Error: Directory '$1' does not exist."
        exit 1
    fi
}

# Check for the correct number of arguments
if [ "$#" -ne 4 ]; then
    echo "Usage: $0 <source_directory> <destination_directory> <start_range> <end_range>"
    exit 1
fi

# Source directory
source_dir="$1"
check_directory_exists "$source_dir"

# Destination directory
destination_dir="$2"
check_directory_exists "$destination_dir"

# Range start and end
start_range="$3"
end_range="$4"

# Loop through the specified range and copy files
for i in $(seq "$start_range" "$end_range"); do
    file_to_copy=$(find "$source_dir" -name "keystore-m_12381_3600_${i}_0_0-*.json")
    
    # Check if the file exists
    if [ -e "$file_to_copy" ]; then
        cp "$file_to_copy" "$destination_dir"
        echo "Copied: $file_to_copy"
    else
        echo "File not found: $file_to_copy"
    fi
done