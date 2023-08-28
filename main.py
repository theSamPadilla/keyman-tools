"""Batch Secure Upload Validator Signing Keys to Secret Manager"""
import json
import sys
import os
import re
import hashlib

from dotenv import load_dotenv
from google.cloud import secretmanager
from google.api_core.exceptions import NotFound

def main(exec_mode: str, config_list:str):
    """Main driver. Unpacks configs and calls uploads.
    Args:
        exec_mode: string - 'gcloud' or 'api'.
        config_list: list<string> - [PROJECT_ID, KEY_DIRECTORY_PATH, GOOGLE_APPLICATION_CREDENTIALS, GCLOUD_PATH].
    """

    #Upload through gcloud or API
    if exec_mode == "gcloud":
        gcloud_create(config_list)
    else:
        api_create(config_list)
        
    print ("\n[INFO] Done with file uploads. Check Google Cloud Secret Manager.")

# Upload Secrets #
def gcloud_create(secrets_configs:list):
    """Creates secrets using the google cloud cli"""
    return

def api_create(secrets_configs:list):
    """Creates secrets using the python library through the API.
    
    Args:
        secret_configs: list<string> -
        [PROJECT_ID, KEY_DIRECTORY_PATH, GOOGLE_APPLICATION_CREDENTIALS, GCLOUD_PATH].
    """

    #Unpack configs
    PROJECT_ID, KEY_DIRECTORY_PATH, _, _ = secrets_configs

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
           
# Helper Functions #
def validate_env_and_params(args:list):
    """
    Validates the execution environment and parameters:
        1. Checks for valid number of parameters.
        2. Checks validity of PROJECT_ID
        3. Checks application default credentials and gcloud exist
        4. Checks that the key directory exists.
    Returns True if all are valid, false otherwise.
    """
    #Parameters
    if len(args) != 2 or (args[1] != "gcloud" and args[1] != "api"):
        print("ERROR: Wrong number of parameters",
              "\nPlease pass execution mode flag as \'glcoud\' or \'api\'.")
        return []
    PROJECT_ID, KEY_DIRECTORY_PATH, GOOGLE_APPLICATION_CREDENTIALS, GCLOUD_PATH = get_configs()

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

    #Gcloud
    #?Note: If uploading via gcloud, no need for ADC.
    if args[1] == 'gcloud':
        if not os.path.exists(GCLOUD_PATH):
            print("ERROR: Google Cloud CLI (gcloud) not found.",
                    "\nPlease download gcloud into the local machine",
                    "https://cloud.google.com/sdk/docs/install or use the API to upload keys.")
            return []
        return [PROJECT_ID, KEY_DIRECTORY_PATH, GOOGLE_APPLICATION_CREDENTIALS, GCLOUD_PATH]

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

    return [PROJECT_ID, KEY_DIRECTORY_PATH, GOOGLE_APPLICATION_CREDENTIALS, GCLOUD_PATH]

def get_configs():
    """Opens the .env file and loads configs"""
    load_dotenv()
    PROJECT_ID = os.getenv("PROJECT_ID")
    KEY_DIRECTORY_PATH = os.getenv("KEY_DIRECTORY_PATH")
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    GCLOUD_PATH = os.getenv("GCLOUD_PATH")
    
    return [PROJECT_ID, KEY_DIRECTORY_PATH, GOOGLE_APPLICATION_CREDENTIALS, GCLOUD_PATH]

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

    return


# Main Caller #
if __name__ == "__main__":
    configs = validate_env_and_params(sys.argv)
    if not configs:
        exit(3)
    main(sys.argv[1], configs)
