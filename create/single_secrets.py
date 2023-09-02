"""Puts all the keys into their own secret."""

import os
import json
import glob
from google.cloud import secretmanager
import create.utilities as util

def create_single_secrets(project_id: str, key_directory_path: str, output_dir: str,
                          optimistic: bool, skip: bool):
    """Creates secrets using the python library through the API.
    
    Args:
        project_id: Google cloud project ID where the secrets will live
        key_directory_path: Path to keystore files
        output_dir: Output path for txt files for local records
        optimistic: Boolean flag to skip checking checksums
        skip: Boolean flag to skip version overwrite
    """

    # Create client and storing dict
    client = secretmanager.SecretManagerServiceClient()
    pubkeys_names = {}

    # Set the filename desired format and filter with glob
    desired_format = "keystore-m_12381_3600_*_0_0-*.json"
    matching_files = glob.glob(os.path.join(key_directory_path, desired_format))

    # Verify that there exist keystore matching the format
    if len(matching_files) == 0:
        print("[ERROR] No keys matching the keystore naming format found.",
              f"\n\tExpected format is {desired_format}. See README.md for more details.")
        return

    # Get all filenames paths sorted by index and initialize counter
    file_names = sorted(matching_files, key=lambda x: int(x.split("_")[4]))
    i = 0

    # Iterate through all keystores
    for key_file_path in file_names:
        print(f"[INFO] Creating Secrets... {i}/{len(file_names)}", flush=True)
        
        #Get the name of the secret only
        key_file_name = key_file_path.split("/")[-1].strip(".json")
        
        # Create secret if does not exist
        exists = util.create_secret_if_not_exists(client, project_id, key_file_name)

        # Read contents of json into str and pass to bytes
        with open(f"{key_file_path}", 'r', encoding="us-ascii") as f:
            contents = f.read()
            f.close()
        payload_bytes = contents.encode("UTF-8")

        # Skip version update is skip is set
        if skip and exists:
            print("\t[-] Skipping version update of existing secret.")
            pubkeys_names[json.loads(contents)["pubkey"]] = key_file_name
            i += 1
            continue

        # Add secret version
        request={"parent": f"projects/{project_id}/secrets/{key_file_name}",
                "payload": {"data": payload_bytes}}
        version = client.add_secret_version(request=request)

        # Add secret and save keys and name to file if optimistic.
        if optimistic:
            pubkeys_names[json.loads(contents)["pubkey"]] = key_file_name

        # Else calculate string SHA256
        else:
            pubkeys_names = util.verify_payload(client, version,
                                            pubkeys_names,
                                            key_file_name,
                                            contents)

        i += 1

    print (f"\n[INFO] Secret creation completed - {i}/{len(file_names)}.",
           "Check Google Cloud Secret Manager.")
    print("\n[INFO] Saving validator pubkeys and secret names locally.")
    util.save_validator_pubkey_and_name(pubkeys_names, output_dir)
    print(f"\t[✓] Done. Check {output_dir}")
