"""Utilities for the create package"""
import json
import hashlib
from google.cloud import secretmanager

def create_secret_if_not_exists(secret_manager_client:secretmanager.SecretManagerServiceClient,
                                project_id:str, secret_id:str) -> bool:
    """Checks if a given secret exists and creates one if not
    
    Args:
        secret_manager_client: The secret manager client
        project_id: The project id
        secret_id: The secret name
    Returns:
        True if the secret exists.
        False if it was created.

    """
    secret_name = secret_manager_client.secret_path(project_id, secret_id)
    try:
        secret_manager_client.get_secret(request={"name": secret_name})
        return True
    except Exception as _: #pylint: disable=W0718
        #Create empty secret
        secret_manager_client.create_secret(request={
            "parent": f"projects/{project_id}",
            "secret_id": secret_id,
            "secret": {"replication": {"automatic": {}}},
        })
        return False

def save_validator_pubkey_and_name(pubkeys_to_names:dict, output:str):
    """
    Saves the validator pubkeys and secret names locally for records.

    Args:
        pubkeys_to_names: Map of Validator pubkeys to secret names
        output: Chosen output directory in the config.
    """
    #Write files
    with open(f"{output}public_keys.txt", "w", encoding="utf-8") as pf, open(f"{output}secret_names.txt", "w", encoding="utf-8") as nf, open(f"{output}pubkey_to_names.txt", "w", encoding="utf-8") as ptnf:
        for pubkey, name in pubkeys_to_names.items():
            pf.write(f"{pubkey}\n")
            nf.write(f"{name}\n")
            ptnf.write(f"{pubkey} : {name}\n")
        pf.close()
        nf.close()
        ptnf.close()

def verify_payload(client: secretmanager.SecretManagerServiceClient,
                   version: secretmanager.SecretVersion,
                   pubkeys_names: dict,
                   secret_name: str,
                   contents: str) -> dict:
    """
    Verifies the sha256 checkcsum of the contents of keystore file, compared
    to the hash of the created secret. If succesful, it stores the pubkey and
    secret name locally for records. It panics otherwise.

    Args:
        client: the Secret manager client
        version: the Secret version getting checked against
        pubkey_names: the dictionary where local data is getting stored
        secret_name: the name of the secret
        contents: the contents of the validator keystore to be checked against
            the secret.
    
    Returns: An updated dictionary with the new pubkey->secret name mapping
    """

    #Get string sha256
    str_sha256 = hashlib.sha256(contents.encode())
    
    #Access the secret version and verify payload SHA256
    response = client.access_secret_version(request={"name": version.name})

    #Get payload sha256
    payload = response.payload.data.decode("UTF-8")
    payload_sha256 = hashlib.sha256(payload.encode())

    #If checksum verifies, store pubkey and secret locally
    if str_sha256.digest() == payload_sha256.digest():
        print("\t[✓] Matching checksums of secret manager and local data.")
        pubkeys_names[json.loads(payload)["pubkey"]] = secret_name
    else:
        print("\t[x] Data corruption detected. Panicing.")
        exit(1)
    
    return pubkeys_names
