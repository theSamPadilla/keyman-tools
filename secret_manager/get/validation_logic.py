"""Handles validation logic for get subcommand of secret-manager command"""
from sys import exit

from cli.pretty.colors import bg_black, yellow, end, bold

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
        print(f"[ERROR] Invalid flag value '{bg_black}{range_str}{end}' for",
              f"flag '{yellow}{flag_head}{end}'.")
        exit(1)

    # Get low and high ranges and check they are numbers
    low, high = split_range[0], split_range[1]
    if not low.isnumeric():
        print(f"[ERROR] Invalid low index {bold}{low}{end}. Please enter a valid positive integer.")
        exit(1)
    if not high.isnumeric():
        print(f"[ERROR] Invalid high index {bold}{high}{end}.",
              "Please enter a valid positive integer.")
        exit(1)

    # Transform to numbers and check low < high
    low, high = int(low), int(high)
    if low >= high:
        print(f"[ERROR] Low index {low} greater than or equal to high index {high}.")
        exit(1)

    #!TODO: Check that the indices provided are in range in Secret manager.

    return (low, high)
