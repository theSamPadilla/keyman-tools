""" Gets and Validates module-level settings for the create command """
import os
import json
import re

from dotenv import load_dotenv
from cli.pretty.colors import bg_red, bold, end, yellow, red

# Get module level settings
def get_env_variables() -> list:
    """Opens the .env file and loads configs"""
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    load_dotenv(env_path)
    project_id = os.getenv("PROJECT_ID")
    key_directory_path = os.getenv("KEY_DIRECTORY_PATH")
    #?Note: Credentials are read from env variable directly
    google_adc = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    output_dir = os.getenv("OUTPUT_DIRECTORY")

    return [project_id, key_directory_path, google_adc, output_dir]

# Validate logic
def validate_env_variables(project_id, key_directory_path, google_adc, output_dir )-> bool:
    """
        Runs the validation logic for the env params
    """
    if not project_id or not validate_proj_id(project_id):
        print(f"\n{red}[ERROR]{end} Invalid Google Cloud Project Id.",
              "\nPlease set a valid project ID in the .env file.")
        print("Valid format (^[a-z][a-z0-9-]*[a-z0-9]$):",
              "\n\t- lowercase letters\n\t- digits\n\t- hyphens",
              "\n\t- it must start with a lowercase letter and end with a letter or number.")
        return False

    # Project keys
    if not os.path.exists(key_directory_path):
        print(f"\n{red}[ERROR]{end} Keys directory not found.\nPlease add the path to the .env file.")
        return False

    # Output Dir
    if not os.path.exists(output_dir):
        print(f"\n{red}[ERROR]{end} Output directory not found.\nPlease add the path to the .env file.")
        return False

    # Application Default Credentials exist
    if not os.path.exists(google_adc):
        print(f"\n{red}[ERROR]{end} Application default credentials file not found.",
                "\nPlease create an ADC file. See the README for how to do this.")
        return False

    #? You can optionally validate the ADC format for Service Account Impersonation or Principal
    # if not validate_adc_format("sai"):
    #     return False

    return True

def validate_proj_id(s:str) -> bool:
    """Validates the format of a project ID in ^[a-z][a-z0-9-]*[a-z0-9]$"""
    pattern = "^[a-z][a-z0-9-]*[a-z0-9]$"
    return re.match(pattern, s) is not None

def validate_adc_format(file_format:str, path:str) -> bool:
    """
    Validates the format of the ADC file.

    Args:
        file_format: The format of the file. Either Service Account Impersonation
            (value=sai) or principal (value=pri).
        path: The path of the adc file.
    
    Returns:
        True if format is valid. False otherwise.
    """
    # Validate ADC Service Account format:
    if file_format == "sai":
        with open(path, "r", encoding="utf-8") as f:
            buff = json.load(f)
            f.close()
        required_source_keys = ["client_id", "client_secret", "refresh_token", "type"]
        required_keys = ["service_account_impersonation_url", "source_credentials", "type"]
        if not all(k in buff for k in required_keys):
            print(f"\n{red}[ERROR]{end} Application default credentials file has the wrong format.",
                    f"\nPlease ensure the file has all the required keys: {required_keys}.")
            return False
        if not all(k in buff["source_credentials"] for k in required_source_keys):
            print(f"\n{red}[ERROR]{end} Application default credentials file has the wrong format.",
                    f"\nPlease ensure the file has all the required keys: {required_keys}.")
            return False
        return True

# Verify overwrite
def check_and_confirm_overwrite(output_files: list, output_dir: str) -> bool:
    """
        Checks if any output files already exist and confirms overwrite if they exist
    """
    if any(os.path.exists(output) for output in output_files):
        input_message = f"{yellow}[WARN]{end} There are conflicting files or directories already in {output_dir}\n\t{bg_red}{bold}Do you want to overwrite them?{end} (yes only - anything else will halt.)\n\t\t"
        response = input(input_message)
        if response.lower() != 'yes':
            return False

    print()
    return True