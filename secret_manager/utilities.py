"""Utilities for the secret-manager command"""

import re
import sys

from google.cloud import secretmanager

def create_sm_client() -> secretmanager.SecretManagerServiceClient:
    """Creates and returns a Google Cloud Secret Manager Client with ADC"""
    return secretmanager.SecretManagerServiceClient()

def get_key_index(key: dict, mode: str) -> int:
    """
    Returns the key index for a given keystore payload or file name compliant with:
    For a kesytore: Index is i in m/12381/3600/i/0/0 on 'path'
    For a file name: Index is i in keystore-m_12381_3600_i_0_0-timestamp.json
    See EIP2334:
    #? https://eips.ethereum.org/EIPS/eip-2334
    #? https://github.com/ethereum/staking-deposit-cli/blob/master/staking_deposit/credentials.py#L155

    """
    if mode == "keystore":
        return int(key['path'].split("/")[-3])
    if mode == "file":
        return int(key.split("_")[-3])
    print("[PANIC] Invalid key index value on get_key_index.")
    sys.exit(1)

def get_secret_names_matching_pattern(client: secretmanager.SecretManagerServiceClient,
                                      project_id: str, pattern: str) -> list:
    """
    Gets a list of secret names matchign the provided pattern.

    Args:
        project-id: The Google Cloud Project ID from where to fetch secrets
        pattern: A regex string pattern to check against.
    
    Returns: A list of secret names.
    """
    matching_secrets = []

    # Build the parent and pattern
    parent = f"projects/{project_id}"

    # Get the raw secret names
    raw_secret_names = client.list_secrets(request={"parent": parent})

    for secret in raw_secret_names:
        secret = secret.name.split("/")[-1] #Get only the secret name
        if re.match(pattern, secret):
            matching_secrets.append(secret)

    return matching_secrets
