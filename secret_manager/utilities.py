"""Utilities for the secret-manager command"""
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
    exit(1)