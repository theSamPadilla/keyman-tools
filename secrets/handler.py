""" Receives calls from main, handles validation, and routes to appropriate subcommand"""
import sys

import secrets.validation_logic as validation_logic
import secrets.delete.handler as delete
import secrets.upload.handler as upload
import secrets.get.handler as get

def handler(_, subcommand, subcommand_flags):
    """
    Checks valid secrets config and routes execution to appropriate subcommand.
        1. Gets and validates env variables defined in .env
        2. Unpacks command and subcommand flags
        2. Confirms overwrite of external files
        3. Forwards request to the appropriate handler function
    """
    # Get env variables
    project_id, key_directory_path, google_adc, output_dir = validation_logic.get_env_variables()
    
    # Verify project ID and google_adc
    if not validation_logic.validate_env_variables(project_id, key_directory_path,
                                                   google_adc, output_dir, subcommand):
        sys.exit(1)

    #? No command flags to process

    # Route to appropriate subcommand if validation passes
    if subcommand == "upload":
        upload.handler(subcommand_flags, project_id, key_directory_path, output_dir)
    elif subcommand == "get":
        get.handler(subcommand_flags, project_id, output_dir)
    elif subcommand == "delete":
        delete.handler(subcommand_flags, project_id)