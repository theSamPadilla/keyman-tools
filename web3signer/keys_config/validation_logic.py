"""Functions for validation for the keys_config subcommand"""

import os
import sys

from cli.pretty.colors import red, end, yellow, bold

def get_and_validate_params(subcommand_flags: list) -> tuple:
    """
    Gets and validates the parameters passed via the subcommands.
    Returns keystore_path, password_path, output_path, key_type
    """
    # Set command variables
    password_path = ""
    output_path = ""
    keystore_path = ""
    key_type = "BLS"

    # Unpack subcommand flags
    while subcommand_flags:
        
        # Get only the flags with a value
        flag_head_to_val = subcommand_flags.pop().split("=")
        if len(flag_head_to_val) > 1:

            # Get the flag head
            flag = flag_head_to_val[0]
            flag_value = flag_head_to_val[1]

            # Check for flags
            if flag == "--keystore-path":
                keystore_path = flag_value
            if flag == "--password-file-path":
                password_path = flag_value
            if flag == "--output-file-path":
                output_path = flag_value
            if flag == "--key-type":
                key_type = flag_value

    # Check mandatory flags exist
    if not all([keystore_path, password_path, output_path]):
        if not keystore_path:
            print(f"[{red}ERROR{end}] Missing flag {yellow}--keystore-path=<value>{end}")
        if not password_path:
            print(f"[{red}ERROR{end}] Missing flag {yellow}--password-file-path=<value>{end}")
        if not output_path:
            print(f"[{red}ERROR{end}] Missing flag {yellow}--output-file-path=<value>{end}")
        
        sys.exit(1)
    
    # Check the key directory exists
    if not os.path.exists(keystore_path) and not os.path.isdir(keystore_path):
        print(f"[{red}ERROR{end}] The directory '{bold}{keystore_path}{end}' does not exist.")
        sys.exit(1)

    # Check the password file exists
    if not os.path.exists(password_path) and not os.path.isfile(password_path):
        print(f"[{red}ERROR{end}] The password file '{bold}{password_path}{end}' does not exist.",
              "\n\tEven if the keystores don't have an associated password, pass a path to an empty file.")
        sys.exit(1)

    # Check output directory exists
    output_directory = os.path.dirname(output_path)
    if not os.path.exists(output_directory):
        print(f"[{red}ERROR{end}] The directory for the file '{bold}{output_path}{end}' does not exist.")
        sys.exit(1)

    # Check output file is yaml
    if not output_path.endswith((".yaml", ".yml")):
        print(f"[{red}ERROR{end}] The file '{bold}{output_path}{end}' must be a valida yaml file.")
        sys.exit(1)

    # Else return flags
    return keystore_path, password_path, output_path, key_type