"""Utilities for the create subcommand on secrets command"""
import os
import hashlib
import glob

from google.cloud import secretmanager
from cli.pretty.colors import red, end


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

def save_validator_pubkey_and_name(secret_names_to_pubkeys:dict, output:str):
    """
    Saves the validator pubkeys and secret names locally for records.

    Args:
        secret_names_to_pubkeys: Map of secret names to validator pubkeys.
            For atomic secret creation, the dict is secret_name:[pubkey1, pubkey2... pubkeyN]
            For single secret creation, the dict is secret_name: pubkey
        output: Chosen output directory in the config.
    """
    # Get Paths
    pk_path = os.path.join(output, "public_keys.txt")
    sn_path = os.path.join(output, "secret_names.txt")
    pksn_path = os.path.join(output, "secret_names_to_pubkeys.txt")
 
    # Write files
    with open(pk_path, "w", encoding="utf-8") as pf, open(sn_path, "w", encoding="utf-8") as nf, open(pksn_path, "w", encoding="utf-8") as ptnf:
        for secret_name, pubkey in secret_names_to_pubkeys.items():
            pf.write(f"{pubkey}\n")
            nf.write(f"{secret_name}\n")
            ptnf.write(f"{secret_name} : {pubkey}\n")
        pf.close()
        nf.close()
        ptnf.close()

def verify_payload(client: secretmanager.SecretManagerServiceClient,
                   version: secretmanager.SecretVersion,
                   contents: str) -> bool:
    """
    Verifies the sha256 checkcsum of the contents string, compared
    to the hash of the created secret.
    Args:
        client: the Secret manager client
        version: the Secret version getting checked against
        contents: the contents of the validator keystore to be checked against
            the secret.
    
    Returns: True if checksum matches, False otherwise
    """

    #Get string sha256
    str_sha256 = hashlib.sha256(contents.encode())
    
    #Access the secret version and verify payload SHA256
    response = client.access_secret_version(request={"name": version.name})

    #Get payload sha256
    payload = response.payload.data.decode("UTF-8")
    payload_sha256 = hashlib.sha256(payload.encode())

    #If checksum verifies
    if str_sha256.digest() == payload_sha256.digest():
        return True
    return False

def get_keyfiles(key_directory_path: str) -> list:
    """
    Gets a list of all the files in the key_directory_path that match the desired keystore format of
    keystore-m_12381_3600_*_0_0-*.json. This is compliant with EIP2334.
    See https://eips.ethereum.org/EIPS/eip-2334
    https://github.com/ethereum/staking-deposit-cli/blob/master/staking_deposit/credentials.py#L155
    """
    # Set the filename desired format and filter with glob
    desired_format = "keystore-m_12381_3600_*_0_0-*.json"
    matching_files = glob.glob(os.path.join(key_directory_path, desired_format))

    # Verify that there exists keystores matching the format
    if len(matching_files) == 0:
        print(f"\n{red}[ERROR]{end} No keys matching the keystore naming format found.",
              f"\n\tExpected format is {desired_format}. See README.md for more details.")
        return

    # Get all filenames paths sorted by index
    #? Sorts by i in /full/path/to/keystore-m_12381_3600_i_0_0-timestamp.json
    file_names = sorted(matching_files, key=lambda x: int(x.split("_")[-3]))
    
    return file_names
