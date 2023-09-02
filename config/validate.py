"""
Validate functions for the tool config.
"""
import re
import json
import os

def env_variables(project_id, key_directory_path, google_adc, output_dir )-> bool:
    """
        Runs the validation logic for the env params
    """
    if not project_id or not proj_id(project_id):
        print("[ERROR] Invalid Google Cloud Project Id.",
              "\nPlease set a valid project ID in the .env file.")
        print("Valid format (^[a-z][a-z0-9-]*[a-z0-9]$):",
              "\n\t- lowercase letters\n\t- digits\n\t- hyphens",
              "\n\t- it must start with a lowercase letter and end with a letter or number.")
        return False

    #Project keys
    if not os.path.exists(key_directory_path):
        print("[ERROR] Keys directory not found.\nPlease add the path to the .env file.")
        return False

    #Output Dir
    if not os.path.exists(output_dir):
        print("[ERROR] Output directory not found.\nPlease add the path to the .env file.")
        return False

    #Application Default Credentials exist
    if not os.path.exists(google_adc):
        print("[ERROR] Application default credentials file not found.",
                "\nPlease create an ADC file. See the README for how to do this.")
        return False

    #[Optional] Validate ADC format

    return True

def optional_params(params: list) -> list:
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
        print("[ERROR] Two many parameters.",
              "\nOnly accepted parameters are:",
              "\n\t- \'optimistic\' ->",
                "Set this flag if you don't want checksum verification of uploaded data.",
                "\n\t- \'optimistic\' ->",
                "Set this flag if you want to skip updating the version on existing secrets.",
                "\n\t See README for more info.")
        return []
    if "optimistic" not in params and "skip" not in params:
        print("[ERROR] Invalid optional parameter.",
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

## Individual Validate functions ##
def proj_id(s:str) -> bool:
    """Validates the format of a project ID in ^[a-z][a-z0-9-]*[a-z0-9]$"""
    pattern = "^[a-z][a-z0-9-]*[a-z0-9]$"
    return re.match(pattern, s) is not None

def adc_format(file_format:str, path:str) -> bool:
    """
    Validates the format of the ADC file.

    Args:
        file_format: The format of the file. Either Service Account Impersonation
            (value=sai) or principal (value=pri).
        path: The path of the adc file.
    
    Returns:
        True if format is valid. False otherwise.
    """
    #Validate ADC Service Account format:
    if file_format == "sai":
        with open(path, "r", encoding="utf-8") as f:
            buff = json.load(f)
            f.close()
        required_source_keys = ["client_id", "client_secret", "refresh_token", "type"]
        required_keys = ["service_account_impersonation_url", "source_credentials", "type"]
        if not all(k in buff for k in required_keys):
            print("[ERROR] Application default credentials file has the wrong format.",
                    f"\nPlease ensure the file has all the required keys: {required_keys}.")
            return False
        if not all(k in buff["source_credentials"] for k in required_source_keys):
            print("[ERROR] Application default credentials file has the wrong format.",
                    f"\nPlease ensure the file has all the required keys: {required_keys}.")
            return False
        return True
