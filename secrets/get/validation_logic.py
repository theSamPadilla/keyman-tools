"""Handles validation logic for get subcommand of secrets command"""
import sys
import os

from cli.pretty.colors import bg_black, yellow, end, bold, red

# Validate Functions
def validate_index_range(flag_head: str, range_str: str) -> tuple:
    """
    Validates the provided index range. Exists without returning upon invalid values.
        1. Checks for two indices
        2. Checks for valid integers
        3. Checks they exist within the bounds of existing secret manager secretes [TODO]

    Returns: (low_index, high_index)
    """
    split_range = range_str.split("_")

    # Check for only two indexes
    if len(split_range) != 2:
        print(f"\n{red}[ERROR]{end} Invalid flag value '{bg_black}{range_str}{end}' for",
              f"flag '{yellow}{flag_head}{end}'.")
        sys.exit(1)

    # Get low and high ranges and check they are numbers
    low, high = split_range[0], split_range[1]
    if not low.isnumeric():
        print(f"\n{red}[ERROR]{end} Invalid low index {bold}{low}{end}. Please enter a valid positive integer.")
        sys.exit(1)
    if not high.isnumeric():
        print(f"\n{red}[ERROR]{end} Invalid high index {bold}{high}{end}.",
              "Please enter a valid positive integer.")
        sys.exit(1)

    # Transform to numbers and check low < high
    low, high = int(low), int(high)
    if low >= high:
        print(f"\n{red}[ERROR]{end} Low index {low} greater than or equal to high index {high}.")
        sys.exit(1)

    #!TODO: Check that the indices provided are in range in Secret manager.

    return (low, high)

def validate_file_name(file_name: str) -> tuple:
    """
    Validates that the file exists and that it contains at least one secret.
        
    Returns: the path to the file if valid, else exits.
    """
    # Check if the file exists and is file
    if not os.path.exists(file_name) and not os.path.isfile(file_name):
        print(f"[{red}ERROR{end}] File {file_name} does not exist.")
        sys.exit(1)

    # Check if the file is not empty
    if os.path.getsize(file_name) == 0:
        print(f"[{red}ERROR{end}] File {file_name} is empty.")
        sys.exit(1)

    # Return the file name
    return file_name
