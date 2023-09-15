"""Puts all the keys into as few secrets as possible."""

import json

import secret_manager.create.utilities as util

from google.cloud import secretmanager

def create_fat_secrets(project_id: str, key_directory_path: str, output_dir: str):
    """Scans the key_directory_path and builds a payload as close to the Secret Manager
    secret size limit. It outsources the secret building to create_secret once the limit
    size is reached. 
        
    Args:
        project_id: Google cloud project ID where the secrets will live
        key_directory_path: Path to keystore files
        output_dir: Output path for txt files for local records
    """

    # Get filenames and clinet
    client, files = util.get_client_and_keyfiles(key_directory_path)

    # Create storing dict, pubkeys list, and indexes
    secret_name_to_pubkeys = {}
    pubkeys = []
    low_index = 0 #? Tracks the lowest key index included in any given payload
    key_i = 0 #? Tracks the number of keys read
    secrets_created = 0 #? Tracks the number of secrets created

    # Initialize payload metric variables
    max_payload_size = 64 * 1024  # 64 KB in bytes
    current_payload_size = 0
    payloads = []

    # Iterate through all json files in keys directory
    for key_file_name in files:
        print(f"[INFO] Scanning Secrets... {key_i}/{len(files)}", flush=True)
        
        # Read contents of json into str
        with open(f"{key_file_name}", 'r', encoding="utf-8") as f:
            contents = f.read()
            f.close()

        # Get key index
        #? Index is i in m/12381/3600/i/0/0 - See EIP2334
        #? https://eips.ethereum.org/EIPS/eip-2334
        #? This path is printed into the default filename keystore-m_12381_3600_i_0_0-timestamp.json
        #? https://github.com/ethereum/staking-deposit-cli/blob/master/staking_deposit/credentials.py#L155
        key_index = int(key_file_name.split("_")[-3])
        
        # Create secret if adding this JSON data to the payload would exceed the limit
        data_size = len(contents.encode("utf-8"))
        if current_payload_size + data_size + 1 > max_payload_size: # +1 for the newline char
            print("\n[INFO] Payload 64kib limit reached.")
            secret_name_to_pubkeys = create_secret(client, project_id, payloads, current_payload_size,
                                                   secret_name_to_pubkeys, pubkeys, low_index, key_index-1)

            # Reset payloads and pubkeys list, low index, and content size.
            # Add to secrets created
            payloads = [contents]
            payloads.append("\n")
            pubkeys = [json.loads(contents)["pubkey"]]
            low_index = key_index
            current_payload_size = data_size + 1  # Add 1 for the newline character
            secrets_created += 1

        # Else add the contents and a newline character to the payload.
        # Increase the payload size and add pubkey to list
        else:
            payloads.append(contents)
            payloads.append("\n")
            pubkeys.append(json.loads(contents)["pubkey"])
            current_payload_size += data_size + 1  # Add 1 for the newline character

        key_i += 1

    # Create the final secret if the payloads list is not empty
    if len(payloads) > 0:
        print("\n[INFO] Remaining payload after secret scan completed.")
        secret_name_to_pubkeys = create_secret(client, project_id, payloads, current_payload_size,
                                               secret_name_to_pubkeys, pubkeys, low_index, key_index)
        secrets_created += 1

    # Print secret creation completion message
    print ("\n[INFO] Secret creation completed.",
           f"\n\t[✓] Scanned {key_i}/{len(files)} secrets.",
           f"\n\t[✓] Created {secrets_created} secrets."
           "\nCheck Google Cloud Secret Manager.")

    # Save local records
    print("\n[INFO] Saving validator pubkeys and secret names locally.")
    util.save_validator_pubkey_and_name(secret_name_to_pubkeys, output_dir)
    print(f"\t[✓] Done. Check {output_dir}")

def create_secret(client: secretmanager.SecretManagerServiceClient, project_id:str,
                  payloads:list, payload_size:int, secret_names_to_pubkeys: dict, pubkeys: list, 
                  low_index:int, high_index:int) -> dict:
    """Creates the atomic secret as close to 64 kb as possible.

    Args:
        client: Google Cloud secret manager client
        project_id: Google Cloud project id
        paylods: List of paylods (containing newline characters) for the secret
        payload_size: the size of the payload in bytes, for logging purposes
        secret_names_to_pubkeys: Dictionary of secret names:pubkeys for internal record
        pubkeys: List of all the pubkeys getting added to this secret
        low_index: The smallest key index whose contents are getting written to the secret
        high_index: The largest key index whose contents are getting written to the secret

    Returns:
        Updated secret_names_to_pubkeys map
    """
    print(f"[INFO] Creating secret from index {low_index} to {high_index}",
          f"and secret size {payload_size/1024}kb")


    # Create secret if does not exist
    secret_name = f"key-index_{low_index}_to_{high_index}"
    util.create_secret_if_not_exists(client, project_id, secret_name)

    # Get the payload string and bytes
    payload_string = "".join(payloads)
    payload_bytes = payload_string.encode(encoding="utf-8")

    # Add secret version
    request={"parent": f"projects/{project_id}/secrets/{secret_name}",
            "payload": {"data": payload_bytes}}
    version = client.add_secret_version(request=request)
    
    # Verify payload calculate string SHA256
    if util.verify_payload(client, version, payload_string):
        print("\t[✓] Matching checksums of secret manager and local data.\n")
        secret_names_to_pubkeys[secret_name] = pubkeys
    else:
        print("\t[x] Data corruption detected. Panicing.")
        exit(1)

    return secret_names_to_pubkeys
