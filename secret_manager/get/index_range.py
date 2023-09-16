"""Fetches all keys from secret manager within a provided index"""
import os

import secret_manager.utilities as util
import secret_manager.get.utilities as get_util

def get_secrets_from_index_range(low: int, high: int, project_id: str, output_dir: str):
    """
    Scans Google Cloud Secret Manager and fetches the keys that fall within the provided range.
    It then creates the appropriate keystore for those keys.
    Caller should pre-validate low and high.
    
    Args:
        low: the low index of the key to get.
        high: the high index of the key to get.
        project_id: Google Cloud project id where to look for secrets.
        output_dir: Output directory defined in .env
    """

    # Get secret manager client and set pattern
    client = util.create_sm_client()
    pattern = r"key-index_(0|[1-9]\d*)_to_(0|[1-9]\d*)"

    # Get all matching secret names and sort them
    secret_names = get_util.get_secret_names_matching_pattern(client, project_id, pattern)
    secret_names = sorted(secret_names, key=lambda x:int(x.split("_")[1])) # Sorts on the low index
    print (f"[INFO] Found {len(secret_names)} total 'fat' secrets.")

    # Set in range secret payload
    in_range_secrets = []

    # Find secret names within the low - high range
    print (f"\n[INFO] Searching for keys in the range {low} to {high}...")
    for secret in secret_names:

        # Process the secret and find index boundaries
        #? Both low index and high are inclusive.
        #? In 'key-index_0_to_5' key index 0 and 5 exist in the secret.
        s_low, s_high = secret.strip("key-index_").split("_to_")
        s_low, s_high = int(s_low), int(s_high)

        print (f"\t[-] Scanning secret containing keys in range {s_low} to {s_high}.")

        # Low index only is in this range, read from low to EOF
        if s_low <= low <= s_high <= high:
            in_range_secrets += get_util.read_secret_range(client, project_id, secret, low, s_high,
                                                         s_low, s_high)
           
        # Both low index and high are in this range, read from low to high
        elif s_low <= low <= high <= s_high:
            in_range_secrets += get_util.read_secret_range(client, project_id, secret, low, high,
                                                         s_low, s_high)

        # Both low index and high are outside of this range, read whole file
        elif low <= s_low <= s_high <= high:
            in_range_secrets += get_util.read_secret_range(client, project_id, secret, s_low, s_high,
                                                         s_low, s_high)

        # High index only is in this range, read from secret low to high
        elif low <= s_low <= high <= s_high:
            in_range_secrets += get_util.read_secret_range(client, project_id, secret, s_low, high,
                                                         s_low, s_high)
        # Check if all secrets found and break.
        if high < s_high:
            break
            
    print ("\t[✓] All keys found.")

    print (f"\n[INFO] Found {len(in_range_secrets)} keys in the range {low} to {high}.")
    low_found = util.get_key_index(in_range_secrets[0], "keystore")
    high_found = util.get_key_index(in_range_secrets[-1], "keystore")
    print (f"\t[-] From indexes {low_found} to {high_found}.")

    # Write keys
    print (f"\n[INFO] Writing {len(in_range_secrets)} keys",
           f"to '{output_dir}/imported_validator_keys/'...")
    get_util.write_secrets(in_range_secrets, os.path.join(output_dir, "imported_validator_keys"))
    print(f"\t[✓] Done. Check {os.path.join(output_dir, 'imported_validator_key')}\n")

    return
