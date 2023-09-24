"""Fetches all keys from secret manager present in the provided file"""
import os
import re
import sys
import json

import secrets.utilities as util
import secrets.get.utilities as get_util

from cli.pretty.colors import green, end, yellow, bold, blue, red
from cli.utilities import print_usage_string_for_command_subcommand_and_flag

def get_secrets_from_file(file_name: str, project_id: str, output_dir: str):
    """
    Scans the provided file and fetches all the secrets contained in that file.
    It then creates the appropriate keystore for those keys.
    Caller should pre-validate file_name.
    
    Args:
        file_name: A path to a .txt file containing the names of all the secrets to get.
        project_id: Google Cloud project id where to look for secrets.
        output_dir: Output directory defined in .env
    """
    # Get secret manager client and set pattern
    client = util.create_sm_client()
    
    # Open the file and read the contents
    with open(file_name, "r", encoding="utf-8") as file:
        secrets_to_read = file.readlines()
        file.close()

    print(f"\n[INFO] Found {yellow}{bold}{len(secrets_to_read)}{end} secret names in {blue}{file_name}{end}.")
    counter = 1

    #? This is a list of strings in the format <timestamp>:<secret>, where <secret>
    #? is a JSON string
    read_secrets = []

    pattern = r'^keystore-m_12381_3600_\d+_0_0-\d+$'

    print ("\n[INFO] Reading secrets...")
    # Iterate through the secret names and read them
    for secret_name in secrets_to_read:
        # Get rid of the extra newline at the end
        secret_name = secret_name.strip()

        # Check that the secret name matches
        if not re.match(pattern, secret_name):
            print(f"\n[{red}ERROR{end}] Can only get secrets by name with 'keystore-m_12381_3600_*_0_0-*' secrets.",
                "\n\tTo get secrets by index range run:",
                f"\n\t{print_usage_string_for_command_subcommand_and_flag('secrets', 'get', '--index-range=<value>')}\n")
            sys.exit(1)

        # Get secret and load it into a dictionary
        raw_secret_string = get_util.read_secret(client, project_id, secret_name)
        secret_payload = json.loads(raw_secret_string)

        if not secret_payload or "path" not in secret_payload:
            print(f"\t[{yellow}-{end}] Could not fetch secret {secret_name}.\n\tIngoring secret.")
            continue

        # Else add it to the read_secrets
        print (f"\t[{green}✓{end}] Found {secret_name} in Google Cloud Secret Manager - {counter}/{len(secrets_to_read)}")
        
        # Get timestamp from key name
        #? The timestamp is in the secret name keystore-m_12381_3600_i_0_0-timestamp
        timestamp = secret_name.split("-")[-1]
        
        read_secrets.append(f"{timestamp}:{raw_secret_string}")
        counter += 1


    # Write keys
    print (f"\n[INFO] Writing {bold}{yellow}{len(read_secrets)}{end} secrets",
           f"to '{blue}{output_dir}/imported_validator_keys/'{end}.")

    get_util.write_secrets(read_secrets, os.path.join(output_dir, "imported_validator_keys"))

    print(f"\n\n[{green}SUCCESS{end}] Key import succesful.",
          f"Check {green}{os.path.join(output_dir, 'imported_validator_keys')}{end}.\n")

    return
