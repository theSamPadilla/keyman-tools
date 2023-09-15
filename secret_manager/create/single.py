"""Puts all the keys into their own secret."""

import json

import secret_manager.create.utilities as create_util
import secret_manager.utilities as util

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
    files = create_util.get_keyfiles(key_directory_path)

    # Initialize counter and local tracker
    i = 0
    secret_names_to_pubkeys = {}

    # Iterate through all keystores
    for key_file_path in files:
        print(f"[INFO] Creating Secrets... {i}/{len(files)}", flush=True)
        
        #Get the name of the secret only
        key_file_name = key_file_path.split("/")[-1].strip(".json")
        
        # Create secret if does not exist
        exists = create_util.create_secret_if_not_exists(client, project_id, key_file_name)

        # Read contents of json into str and pass to bytes
        with open(f"{key_file_path}", 'r', encoding="utf-8") as f:
            contents = f.read()
            f.close()
        payload_bytes = contents.encode("utf-8")

        # Skip version update if skip is set
        if skip and exists:
            print("\t[-] Skipping version update of existing secret.")
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
            if create_util.verify_payload(client, version, contents):
                print("\t[✓] Matching checksums of secret manager and local data.")
                secret_names_to_pubkeys[key_file_name] = json.loads(contents)["pubkey"]
            else:
                print("\t[x] Data corruption detected. Panicing.")
                exit(1)

        i += 1

    print (f"\n[INFO] Secret creation completed - {i}/{len(files)}.",
           "Check Google Cloud Secret Manager.")
    print("\n[INFO] Saving validator pubkeys and secret names locally.")
    create_util.save_validator_pubkey_and_name(secret_names_to_pubkeys, output_dir)
    print(f"\t[✓] Done. Check {output_dir}")
