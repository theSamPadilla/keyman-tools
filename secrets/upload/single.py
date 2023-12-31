"""Puts all the keys into their own secret."""

import json

import secrets.upload.utilities as upload_util
import secrets.utilities as util

from cli.pretty.colors import green, end, red

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
    # Get filenames and clinet
    client = util.create_sm_client()
    files = upload_util.get_keyfiles(key_directory_path)

    # Initialize counter and local tracker
    i = 1
    secret_names_to_pubkeys = {}

    print("[INFO] Creating Secrets...")
    # Iterate through all keystores
    for key_file_path in files:
        
        #Get the name of the secret only
        key_file_name = key_file_path.split("/")[-1].strip(".json")
        
        # Create secret if does not exist
        exists = upload_util.create_secret_if_not_exists(client, project_id, key_file_name)

        # Read contents of json into str and pass to bytes
        with open(f"{key_file_path}", 'r', encoding="utf-8") as f:
            contents = f.read()
            f.close()
        payload_bytes = contents.encode("utf-8")

        print(f"\t[{green}✓{end}] Read file {key_file_name} - {i}/{len(files)}")

        # Skip version update if skip is set
        if skip and exists:
            print("\t\t[-] Skipping version update of existing secret.")
            secret_names_to_pubkeys[key_file_name] = json.loads(contents)["pubkey"]
            i += 1
            continue

        # Add secret version
        request={"parent": f"projects/{project_id}/secrets/{key_file_name}",
                "payload": {"data": payload_bytes}}
        version = client.add_secret_version(request=request)

        # Add secret and save keys and name to file if optimistic.
        if optimistic:
            secret_names_to_pubkeys[key_file_name] = json.loads(contents)["pubkey"]

        # Else calculate string SHA256
        else:
            if upload_util.verify_payload(client, version, contents):
                print(f"\t[{green}✓{end}] Matching checksums of secret manager and local data.")
                secret_names_to_pubkeys[key_file_name] = json.loads(contents)["pubkey"]
            else:
                print(f"\t[{red}x{end}] Data corruption detected. Panicing.")
                exit(1)

        i += 1

    print ("\n[INFO] Secret creation completed .",
           "Check Google Cloud Secret Manager.")
    print("\n[INFO] Saving validator pubkeys and secret names locally.")
    upload_util.save_validator_pubkey_and_name(secret_names_to_pubkeys, output_dir)
    print(f"\n\n[{green}SUCCESS{end}] Secret creation and local saving complete. Check {output_dir}\n")

