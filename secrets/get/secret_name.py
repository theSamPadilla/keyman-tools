"""Fetches the key from secret manager that matches the provided name"""
import os
import re
import sys
import json

import secrets.utilities as util
import secrets.get.utilities as get_util

from cli.pretty.colors import green, end, red
from cli.utilities import print_usage_string_for_command_subcommand_and_flag


def get_secrets_from_name(project_id: str, output_dir: str, secret_name: str):
    """
    Gets a Google Cloud Secret Manager and fetches the secret that matches the provided name.
    
    Args:
        project_id: Google Cloud project id where to look for secrets.
        output_dir: Output directory defined in .env
        target_secret: The name of the secret to be read
    """

    # Get secret manager client
    client = util.create_sm_client()
    
    # Check the secret name is in the valid format
    pattern = r'^keystore-m_12381_3600_\d+_0_0-\d+$'
    if not re.match(pattern, secret_name):
        print(f"[{red}ERROR{end}] Can only get secrets by name with 'keystore-m_12381_3600_*_0_0-*' secrets.",
              "\n\tTo get secrets by index range run:",
              f"\n\t{print_usage_string_for_command_subcommand_and_flag('secrets', 'get', '--index-range=<value>')}")
        sys.exit(1)

    # Get secret and load it into a dictionary
    raw_secret_payload = get_util.read_secret(client, project_id, secret_name)

    if not raw_secret_payload:
        print(f"[{red}ERROR{end}] Could not find secret with name {secret_name}")
        sys.exit(1)

    print (f"[INFO] Found {secret_name} in Google Cloud Secret Manager.")

    # Write keys
    print (f"\n[INFO] Writing {secret_name}",
           f"to '{os.path.join(output_dir, 'imported_validator_keys')}'.")

    timestamp = secret_name.split("-")[-1]
    get_util.write_secrets([f"{timestamp}:{raw_secret_payload}"],os.path.join(output_dir, "imported_validator_keys"))

    print(f"\n\n[{green}SUCCESS{end}] Key import succesful.",
          f"Check {os.path.join(output_dir, 'imported_validator_keys')}.\n")
    return
