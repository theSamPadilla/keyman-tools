#!/usr/bin/python3
############################################
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
############################################

"""Batch Secure Upload of Validator Signing Keys to Google Cloud Secret Manager"""
import json
import os
import re
import hashlib
import sys

from dotenv import load_dotenv #type: ignore
from google.cloud import secretmanager

def create_secrets(secrets_configs:list):
    """Creates secrets using the python library through the API.
    
    Args:
        secret_configs: list<string> -
        [project_id, key_directory_path, google_adc].
    """

    #Unpack configs
    project_id, key_directory_path, _, output_dir, optimistic, skip = secrets_configs

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
            exists = create_secret_if_not_exists(client, project_id, key_file_name)

            #Skip version update is skip is set
            if skip and exists:
                print("\t[-] Skipping version update of existing secret.")
                continue

            #Read contents of json into str and pass to bytes
            with open(f"{key_directory_path}{key_file_name}.json", 'r', encoding="us-ascii") as f:
                contents = f.read()
                f.close()
            payload_bytes = contents.encode("UTF-8")

            #Add secret version
            request={"parent": f"projects/{project_id}/secrets/{key_file_name}",
                    "payload": {"data": payload_bytes}}
            version = client.add_secret_version(request=request)

            # Add secret and save keys and name to file if optimistic.
            if optimistic:
                pubkeys_names[json.loads(contents)["pubkey"]] = key_file_name

            #Else calculate string SHA256
            else:
                pubkeys_names = verify_payload(client, version,
                                               pubkeys_names,
                                               key_file_name,
                                               contents)

            i += 1

    print (f"\n[INFO] Secret creation completed - {i}/{len(file_names)}.",
           "Check Google Cloud Secret Manager.")

    print("\n[INFO] Saving validator pubkeys and secret names locally.")
    save_validator_pubkey_and_name(pubkeys_names, output_dir)
    print(f"\t[✓] Done. Check {output_dir}")

# Helper Functions #
def validate_env_and_params(params) -> list:
    """
    Validates the execution environment and parameters:
        1. Checks optional parameters
        2. Checks validity of project_id
        3. Checks that key directory exists
        4. Checks that output directory exists
        5. Checks that and prompts for overwrite
            confirmation if local stores exist already
        6. Checks application default credentials file exists and its format
    Returns True if all are valid, false otherwise.
    """
    #Help
    if "help" in params or "--help" in params or "h" in params:
        print_help()
        exit(0)

    #Process optional params if they exist
    optimistic, skip = False, False
    if len(params) > 1:
        optional_params = check_optional_params(params)
        if not optional_params:
            return []
        optimistic = optional_params[0]
        skip = optional_params[1]

    #Configs
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
    exists_ptnf = os.path.exists(f"{output_dir}pubkey_to_names.txt")
    if exists_nf or exists_pf or exists_ptnf:
        input_message = f"[WARN] There are public keys and secret files already in {output_dir}.\n\tDo you want to overwrite it? (yes only - anything else will halt.)\n\t\t"
        response = input(input_message)
        if response.lower() != 'yes':
            return []
        print()

    #Application Default Credentials exist
    if not os.path.exists(google_adc):
        print("ERROR: Application default credentials file not found.",
                "\nPlease create an ADC file. See the README for how to do this.")
        return []

    #[Optional] Validate ADC format

    return [project_id, key_directory_path, google_adc, output_dir, optimistic, skip]

def get_configs() -> list:
    """Opens the .env file and loads configs"""
    load_dotenv()
    project_id = os.getenv("PROJECT_ID")
    key_directory_path = os.getenv("KEY_DIRECTORY_PATH")
    #?Note: Credentials are read from env variable directly
    google_adc = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    output_dir = os.getenv("OUTPUT_DIRECTORY")

    return [project_id, key_directory_path, google_adc, output_dir]

def valid_proj_id(s:str) -> bool:
    """Validates the format of a project ID in ^[a-z][a-z0-9-]*[a-z0-9]$"""
    pattern = "^[a-z][a-z0-9-]*[a-z0-9]$"
    return re.match(pattern, s) is not None

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

def print_help():
    """Prints help message"""
    print("\nWelcome to the bls keys to secret manager tool!")
    print("This tool creates Google Cloud Secret Manager entries",
          "for all the validator keys in the target directory defined in",
          "the \'.env\' file.")

    print("\n\n----- PARAMETERS -----")
    print("The tool takes 3 optional parameters")
    print("- \'optimistic\' -> Makes the tool not check the validator keystore cheksum with the checksum of the created secret.")
    print("- \'skip\' -> Makes the tool skip a version update of existing secrets.")
    print("- \'help\' -> Prints this message.")

    print("\n\n----- OUTPUT -----")
    print("The tool will create three files in \'OUTPUT_DIRECTORY\':")
    print("- \'public_keys.txt\' -> A list of all the public keys uploaded.")
    print("- \'secret_names.txt\' -> A list of all the secret names created.")
    print("- \'pubkey_to_names.txt\' -> A mapping of the public key to the created secret name.")
    print("\nFor a full description, see the README.md\n")

def validate_adc_format(adc_format:str, adc_path:str) -> bool:
    """
    Validates the format of the ADC file.

    Args:
        adc_format: The format of the file. Either Service Account Impersonation
            (value=sai) or principal (value=pri).
        adc_path: The path of the adc file.
    
    Returns:
        True if format is valid. False otherwise.
    """
    #Validate ADC Service Account format:
    if adc_format == "sai":
        with open(adc_path, "r", encoding="utf-8") as f:
            buff = json.load(f)
            f.close()
        required_source_keys = ["client_id", "client_secret", "refresh_token", "type"]
        required_keys = ["service_account_impersonation_url", "source_credentials", "type"]
        if not all(k in buff for k in required_keys):
            print("ERROR: Application default credentials file has the wrong format.",
                    f"\nPlease ensure the file has all the required keys: {required_keys}.")
            return False
        if not all(k in buff["source_credentials"] for k in required_source_keys):
            print("ERROR: Application default credentials file has the wrong format.",
                    f"\nPlease ensure the file has all the required keys: {required_keys}.")
            return False
        return True

def check_optional_params(params: list) -> list:
    """
    Checks for the optional parameters `skip` and `optional`

    Args:
        params: the list of optional parmeters.
    Returns:
        [] If params are invalid
        [bool, bool] with the value of optimistic and skip, in that order.
    """
    optimistic = False
    skip = False
    if len(params) > 3:
        print("ERROR: Two many parameters.",
              "\nOnly accepted parameters are:",
              "\n\t- \'optimistic\' ->",
                "Set this flag if you don't want checksum verification of uploaded data.",
                "\n\t- \'optimistic\' ->",
                "Set this flag if you want to skip updating the version on existing secrets.",
                "\n\t See README for more info.")
        return []
    if "optimistic" not in params and "skip" not in params:
        print("ERROR: Invalid optional parameter.",
            "\nOnly accepted parameters are:",
            "\n\t- \'optimistic\' ->",
            "Set this flag if you don't want checksum verification of uploaded data.",
            "\n\t- \'optimistic\' ->",
            "Set this flag if you want to skip updating the version on existing secrets.",
            "\n\t See README for more info.")
        return []
    if "optimistic" in params:
        optimistic = True
    if "skip" in params:
        skip = True

    return [optimistic, skip]

# Main Caller #
if __name__ == "__main__":
    configs = validate_env_and_params(sys.argv)
    if not configs:
        exit(3)
    create_secrets(configs)
