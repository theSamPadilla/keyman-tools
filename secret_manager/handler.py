""" Receives calls from main, handles validation, and routes to appropriate subcommand"""

import secret_manager.logic as logic
import secret_manager.create.handler as create

def handler(command_flags, subcommand, subcommand_flags):
    """
    Checks valid secret-manager config and routes execution to appropriate subcommand.
        1. Gets and validates env variables defined in .env
        2. Unpacks command and subcommand flags
        2. Confirms overwrite of external files
        3. Forwards request to the appropriate handler function
    """
    # Get and validate env variables
    project_id, key_directory_path, google_adc, output_dir = logic.get_env_variables()
    if not logic.validate_env_variables(project_id, key_directory_path, google_adc, output_dir):
        return
    
    #? No command flags to process

    # Route to appropriate subcommand
    if subcommand == "create":
        create.handler(subcommand_flags, project_id, key_directory_path, output_dir)