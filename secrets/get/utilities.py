"""Utilities for the get subcommand on secrets command"""

import json
import os

import secrets.utilities as util

def read_secret_range(client: util.secretmanager.SecretManagerServiceClient,
                      project_id: str, secret_name: str, target_low: int, target_high: int,
                      secret_low, secret_high) -> list:
    """
    Reads the latest version of a 'fat' secret and returns only the keys within a given range.
    Works only for key secrets with format key-index_l_to_h, where l and h are integers and l<h.
    Caller must pre-validate that the low and high are in range (low >= l and high <= h)
    
    Args:
        client: A Google Cloud secret manager client.
        project_id: Google Cloud project ID where to read the secrets from
        secret_name: The secret name
        low: The low key index to start reading from.
        high: The high key index to stop reading at.

    Returns: A list os secret payloads
    """
    # Read the secret contents and turn a fat payload into a list of secrets
    payload = process_raw_payload(read_secret(client, project_id, secret_name))

    #? Note: There are only 3 conditions under which this function is invoked:
    #? 1. Either only the low or high target index is in the range, find it.
    #? 2. Both target indexes in the range, find both.
    #? 3. Both target indexes outside the range, read the whole file.

    # Check when the whole file needs to be read and return immediately
    if target_low == secret_low and secret_high == target_high:
        return payload

    # Find low
    elif target_low > secret_low and secret_high == target_high:
        lli = binary_search(payload, target_low) #low list index
        return payload[lli:]

    # Find high
    elif target_low == secret_low and secret_high < target_high:
        hli = binary_search(payload, target_high) #high list index
        return payload[:hli]

    #Find both
    lli = binary_search(payload, target_low)
    hli = binary_search(payload, target_high)

    return payload[lli:hli+1] # +1 because you want the last index too

def process_raw_payload(raw: str) -> list:
    """
    Processes the raw payload of a fat secret.
    Returns: A list of dictionaries, with each entry being an individual secret.
    """
    secret_string_list = raw.strip().split('\n')
    return [json.loads(obj) for obj in secret_string_list]

def binary_search(payload: list, target: int) -> int:
    """Performs binary search on the payload to find the list index of the key with index == target"""
    l = 0
    h = len(payload)

    while l <= h:
        mid = (l + h) // 2
        key_index = util.get_key_index(payload[mid], "keystore")

        # Return if found
        if key_index == target:
            return mid

        # Go right
        if target > key_index:
            l = mid+1

        #Go left
        else:
            h = mid-1

    return -1

def write_secrets(secrets: list, output_dir: str):
    """
    Writes the secrets in the list to output_dir.
    It writes in format keystore-m_12381_3600_i_0_0-timestamp.json, where i is the key index.
    """
    # Create output dir if it does not exist:
    os.makedirs(os.path.dirname(output_dir), exist_ok=True)

    total = len(secrets)
    curr = 1

    for secret in secrets:
        # Get key index and set file name
        i = util.get_key_index(secret, mode="keystore")
        keystore_name = f"keystore-m_12381_3600_{i}_0_0-timestamp.json"

        print(f"\t[-] Writing secret to {keystore_name} - {curr}/{total}")

        # Write
        path = os.path.join(output_dir, keystore_name)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(secret, f)
            f.close()

        curr += 1

    return

def read_secret(client: util.secretmanager.SecretManagerServiceClient,
                      project_id: str, secret_name: str) -> str:
    """
    Reads the secret contents of the provided secret name.
    Args:
        client: A Google Cloud secret manager client.
        project_id: Google Cloud project ID where to read the secrets from
        secret_name: The secret name
    Returns the string payload of the secret.
    """
    # Set secret name
    name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"

    # Get secret latest version, decode, and process the payload
    response = client.access_secret_version(request={"name": name})

    return response.payload.data.decode("UTF-8")