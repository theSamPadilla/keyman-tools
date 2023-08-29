"""Batch Secure Upload of Validator Signing Keys to Google Cloud Secret Manager"""
import json
import os
import re
import hashlib

from dotenv import load_dotenv #type: ignore
from google.cloud import secretmanager
from google.api_core.exceptions import NotFound

def create_secrets(secrets_configs:list):
    """Creates secrets using the python library through the API.
    
    Args:
        secret_configs: list<string> -
        [project_id, key_directory_path, google_adc].
    """

    #Unpack configs
    project_id, key_directory_path, _, output_dir = secrets_configs

    #Create client and storing dict
    client = secretmanager.SecretManagerServiceClient()
    pubkeys_names = {}

    #Iterate through all json files in keys directory
    file_names = os.listdir(key_directory_path)
    i = 0
    for key_file_name in file_names:
        print(f"[INFO] Creating Secrets... {i}/{len(file_names)}", flush=True)
        if key_file_name.endswith(".json"):
            key_file_name = key_file_name.strip(".json")

            #Create secret if does not exist
            create_secret_if_not_exists(client, project_id, key_file_name)

            #Read contents of json into str and pass to bytes
            with open(f"{key_directory_path}{key_file_name}.json", 'r', encoding="us-ascii") as f:
                contents = f.read()
                f.close()
            payload_bytes = contents.encode("UTF-8")

            #Calculate string SHA256.
            str_sha256 = hashlib.sha256(contents.encode())

            #Add secret version
            request={"parent": f"projects/{project_id}/secrets/{key_file_name}",
                     "payload": {"data": payload_bytes}}
            version = client.add_secret_version(request=request)

            #Access the secret version and verify payload SHA256
            response = client.access_secret_version(request={"name": version.name})

            #Get payload sha256
            payload = response.payload.data.decode("UTF-8")
            payload_sha256 = hashlib.sha256(payload.encode())

            #If checksum verifies, store pubkey and secret locally
            if str_sha256.digest() == payload_sha256.digest():
                print("\t[✓] Matching checksums of secret manager and local data.")
                pubkeys_names[json.loads(payload)["pubkey"]] = key_file_name
            else:
                print("\t[x] Data corruption detected. Panicing.")
                exit(1)

            i += 1

    print (f"\n[INFO] Secret creation completed - {i}/{len(file_names)}.",
           "Check Google Cloud Secret Manager.")

    print("\n[INFO] Saving validator pubkeys and secret names locally.")
    save_validator_pubkey_and_name(pubkeys_names, output_dir)
    print(f"\t[✓] Done. Check {output_dir}")

# Helper Functions #
def validate_env_and_params():
    """
    Validates the execution environment and parameters:
        1. Checks validity of project_id
        2. Checks that key directory exists
        2. Checks that output directory exists
        3. Checks that and prompts for overwrite
            confirmation if local stores exist already
        4. Checks application default credentials file exists and its format
    Returns True if all are valid, false otherwise.
    """
    #Parameters
    project_id, key_directory_path, google_adc, output_dir = get_configs()

    #Project ID
    if not project_id or not valid_proj_id(project_id):
        print("ERROR: Invalid Google Cloud Project Id.",
              "\nPlease set a valid project ID in the .env file.")
        print("Valid format (^[a-z][a-z0-9-]*[a-z0-9]$):",
              "\n\t- lowercase letters\n\t- digits\n\t- hyphens",
              "\n\t- it must start with a lowercase letter and end with a letter or number.")
        return []

    #Project keys
    if not os.path.exists(key_directory_path):
        print("ERROR: Keys directory not found.\nPlease add the path to the .env file.")
        return []

    #Output Dir
    if not os.path.exists(output_dir):
        print("ERROR: Output directory not found.\nPlease add the path to the .env file.")
        return []

    #Confirm overwrite
    exists_pf = os.path.exists(f"{output_dir}public_keys.txt")
    exists_nf = os.path.exists(f"{output_dir}secret_names.txt")
    if exists_nf or exists_pf:
        input_message = f"[WARN] There are public keys and secret files already in {output_dir}.\n\tDo you want to overwrite it? (yes only - anything else will halt.)\n\t\t"
        response = input(input_message)
        if response.lower() != 'yes':
            return []
        print()

    #Application Default Credentials
    if not os.path.exists(google_adc):
        print("ERROR: Application default credentials file not found.",
                "\nPlease create an ADC file. See the README for how to do this.")
        return []

    #Validate ADC format (Service Account format):
    with open(google_adc, "r", encoding="utf-8") as f:
        buff = json.load(f)
        f.close()
    required_source_keys = ["client_id", "client_secret", "refresh_token", "type"]
    required_keys = ["service_account_impersonation_url", "source_credentials", "type"]
    if not all([k in buff for k in required_keys]):
        print("ERROR: Application default credentials file has the wrong format.",
                f"\nPlease ensure the file has all the required keys: {required_keys}.")
        return []
    if not all([k in buff["source_credentials"] for k in required_source_keys]):
        print("ERROR: Application default credentials file has the wrong format.",
                f"\nPlease ensure the file has all the required keys: {required_keys}.")
        return []

    return [project_id, key_directory_path, google_adc, output_dir]

def get_configs():
    """Opens the .env file and loads configs"""
    load_dotenv()
    project_id = os.getenv("PROJECT_ID")
    key_directory_path = os.getenv("KEY_DIRECTORY_PATH")
    #?Note: Credentials are read from env variable directly
    google_adc = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    output_dir = os.getenv("OUTPUT_DIRECTORY")

    return [project_id, key_directory_path, google_adc, output_dir]

def valid_proj_id(s:str):
    """Validates the format of a project ID in ^[a-z][a-z0-9-]*[a-z0-9]$"""
    pattern = "^[a-z][a-z0-9-]*[a-z0-9]$"
    return re.match(pattern, s) is not None

def create_secret_if_not_exists(secret_manager_client:secretmanager.SecretManagerServiceClient, project_id:str, secret_id:str) -> secretmanager.Secret:
    """Checks if a given secret exists and creates one if not"""
    secret_name = secret_manager_client.secret_path(project_id, secret_id)
    try:
        secret_manager_client.get_secret(request={"name": secret_name})
    except NotFound:
        #Create empty secret
        secret_manager_client.create_secret(request={
            "parent": f"projects/{project_id}",
            "secret_id": secret_id,
            "secret": {"replication": {"automatic": {}}},
        })

def save_validator_pubkey_and_name(pubkeys_to_names:dict, output:str):
    """
    Saves the validator pubkeys and secret names locally for records.

    Args:
        pubkeys_to_names: Map of Validator pubkeys to secret names
        output: Chosen output directory in the config.
    """
    #Write files
    with open(f"{output}public_keys.txt", "w", encoding="utf-8") as pf, open(f"{output}secret_names.txt", "w", encoding="utf-8") as nf:
        for pubkey, name in pubkeys_to_names.items():
            pf.write(f"{pubkey}\n")
            nf.write(f"{name}\n")
        pf.close()
        nf.close()

# Main Caller #
if __name__ == "__main__":
    configs = validate_env_and_params()
    if not configs:
        exit(3)
    create_secrets(configs)
