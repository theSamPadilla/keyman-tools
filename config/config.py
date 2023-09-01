"""Collection of config and setup functions for the tool"""
import os
from dotenv import load_dotenv #type: ignore

import config.utilities as util
import config.validate as val

def config_tool(params) -> list:
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
        util.print_help()
        exit(0)

    #Get and validate env variables
    project_id, key_directory_path, google_adc, output_dir = get_env_variables()
    if not val.env_variables(project_id, key_directory_path, google_adc, output_dir):
        return []

    #Exec modes
    atomic = False
    optimistic, skip = False, False

    #Single secret creation mode
    if "atomic" in params:
        atomic = True
        return [project_id, key_directory_path, google_adc, output_dir, optimistic, skip, atomic]

    #Confirm overwrite
    exists_pf = os.path.exists(f"{output_dir}public_keys.txt")
    exists_nf = os.path.exists(f"{output_dir}secret_names.txt")
    exists_ptnf = os.path.exists(f"{output_dir}pubkey_to_names.txt")
    if exists_nf or exists_pf or exists_ptnf:
        if not confirm_overwrite(output_dir):
            return []

    #Process optional params if they exist
    if len(params) > 1:
        optional_params = val.optional_params(params)
        if not optional_params:
            return []
        optimistic = optional_params[0]
        skip = optional_params[1]

    return [project_id, key_directory_path, google_adc, output_dir, optimistic, skip, atomic]

# Helper Functions #
def get_env_variables() -> list:
    """Opens the .env file and loads configs"""
    load_dotenv()
    project_id = os.getenv("PROJECT_ID")
    key_directory_path = os.getenv("KEY_DIRECTORY_PATH")
    #?Note: Credentials are read from env variable directly
    google_adc = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    output_dir = os.getenv("OUTPUT_DIRECTORY")

    return [project_id, key_directory_path, google_adc, output_dir]

def confirm_overwrite(output_dir: str) -> bool:
    """
        Confirms overwrite of existing output files
    """
    input_message = f"[WARN] There are public keys and secret files already in {output_dir}.\n\tDo you want to overwrite it? (yes only - anything else will halt.)\n\t\t"
    response = input(input_message)
    if response.lower() != 'yes':
        return False
    print()
    return True
