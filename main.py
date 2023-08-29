"""Batch Secure Upload Validator Signing Keys to Secret Manager"""
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
        [PROJECT_ID, KEY_DIRECTORY_PATH, GOOGLE_APPLICATION_CREDENTIALS].
    """

    #Unpack configs
    PROJECT_ID, KEY_DIRECTORY_PATH, _ = secrets_configs

    #Create client #?Note: Credentials are read from env file
    client = secretmanager.SecretManagerServiceClient()

    #Iterate through all json files in keys directory
    file_names = os.listdir(KEY_DIRECTORY_PATH)
    i = 0
    for key_file_name in file_names:
        print(f"[INFO] Uploading Files... {i}/{len(file_names)}", flush=True)
        if key_file_name.endswith(".json"):
            key_file_name = key_file_name.strip(".json")

            #Create secret if does not exist
            create_secret_if_not_exists(client, PROJECT_ID, key_file_name)

            #Read contents of json into str and pass to bytes
            with open(f"{KEY_DIRECTORY_PATH}{key_file_name}.json", 'r', encoding="us-ascii") as f:
                contents = f.read()
                f.close()
            payload_bytes = contents.encode("UTF-8")

            #Calculate string SHA256.
            str_sha256 = hashlib.sha256(contents.encode())

            #Add secret version
            request={"parent": f"projects/{PROJECT_ID}/secrets/{key_file_name}",
                     "payload": {"data": payload_bytes}}
            version = client.add_secret_version(request=request)

            #Access the secret version and verify payload SHA256
            response = client.access_secret_version(request={"name": version.name})

            #Verify payload sha256.
            payload_sha256 = hashlib.sha256(response.payload.data.decode("UTF-8").encode())
            if str_sha256.digest() == payload_sha256.digest():
                print("\t- Matching hashes of uploaded and local data.")
            else:
                print("\nData corruption detected. Panicing.")
                exit(1)

            i += 1

    print ("\n[INFO] Done with file uploads {i}/{len(file_names)}.\n",
           "\tCheck Google Cloud Secret Manager.")

# Helper Functions #
def validate_env_and_params():
    """
    Validates the execution environment and parameters:
        1. Checks validity of PROJECT_ID
        2. Checks application default credentials
        3. Checks that the key directory exists.
    Returns True if all are valid, false otherwise.
    """
    #Parameters
    PROJECT_ID, KEY_DIRECTORY_PATH, GOOGLE_APPLICATION_CREDENTIALS = get_configs()

    #Project ID
    if not PROJECT_ID or not valid_proj_id(PROJECT_ID):
        print("ERROR: Invalid Google Cloud Project Id.",
              "\nPlease set a valid project ID in the .env file.")
        print("Valid format (^[a-z][a-z0-9-]*[a-z0-9]$):",
              "\n\t- lowercase letters\n\t- digits\n\t- hyphens",
              "\n\t- it must start with a lowercase letter and end with a letter or number.")
        return []

    #Project keys
    if not os.path.exists(KEY_DIRECTORY_PATH):
        print("ERROR: Keys directory not found.\nPlease add the path to the .env file.")
        return []

    #Application Default Credentials
    if not os.path.exists(GOOGLE_APPLICATION_CREDENTIALS):
        print("ERROR: Application default credentials file not found.",
                "\nPlease create an ADC file. See the README for how to do this.")
        return []

    #Validate ADC format (Service Account format):
    with open(GOOGLE_APPLICATION_CREDENTIALS, "r", encoding="utf-8") as f:
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

    return [PROJECT_ID, KEY_DIRECTORY_PATH, GOOGLE_APPLICATION_CREDENTIALS]

def get_configs():
    """Opens the .env file and loads configs"""
    load_dotenv()
    PROJECT_ID = os.getenv("PROJECT_ID")
    KEY_DIRECTORY_PATH = os.getenv("KEY_DIRECTORY_PATH")
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    
    return [PROJECT_ID, KEY_DIRECTORY_PATH, GOOGLE_APPLICATION_CREDENTIALS]

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

# Main Caller #
if __name__ == "__main__":
    configs = validate_env_and_params()
    if not configs:
        exit(3)
    create_secrets(configs)
