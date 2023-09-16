""" Receives calls from main, handles validation, and routes to appropriate subcommand"""

import secret_manager.validation_logic as validation_logic
import secret_manager.create.handler as create
import secret_manager.get.handler as get

def handler(_, subcommand, subcommand_flags):
    """
    Checks valid secret-manager config and routes execution to appropriate subcommand.
        1. Gets and validates env variables defined in .env
        2. Unpacks command and subcommand flags
        2. Confirms overwrite of external files
        3. Forwards request to the appropriate handler function
    """
    # Get and validate env variables
    project_id, key_directory_path, google_adc, output_dir = validation_logic.get_env_variables()
    if not validation_logic.validate_env_variables(project_id, key_directory_path, google_adc, output_dir):
        return
    
    #? No command flags to process

    # Route to appropriate subcommand
    if subcommand == "create":
        create.handler(subcommand_flags, project_id, key_directory_path, output_dir)
    elif subcommand == "get":
        get.handler(subcommand_flags, project_id, output_dir)
