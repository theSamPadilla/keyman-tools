"""Handler for the 'delete' subcommand of secrets command"""

import sys

import secrets.utilities as util
import secrets.delete.utilities as de_util
import secrets.delete.delete_secrets as del_executer

from cli.pretty.colors import red, end, green
from cli.utilities import print_usage_string_for_command_and_flag

def handler(subcommand_flags: list, project_id: str):
    """
    Handles upload subcommand logic.
        1. Unpacks subcommand flags
        2. Checks validity of the flags
        3. Gets confirmation or overwrite
        4. Deletes the secrets
    
    Args:
        - subcommand_flags: List of subcommand flags
        - project_id: The Google Cloud Project ID to delete secrets from
        
    """
    # Define subcommand bool flags
    secret_name = ""
    pattern = ""
    skip_confirm = False
    
    # Unpack and catch subcommand flags
    while subcommand_flags:
        flag = subcommand_flags.pop()
        
        if "--secret-name" in flag and len(flag.split("=")) > 1:
            secret_name = flag.split("=")[-1]
        elif "--pattern" in flag and len(flag.split("=")) > 1:
            pattern = flag.split("=")[-1]
        elif "--skip-confirmation" in flag:
            skip_confirm = True

    # Alert and exist if no flag values are passed to delete
    if not secret_name and not pattern:
        print (f"[{red}ERROR{end}] No delete pattern was passed.",
               f"\n\tRun {print_usage_string_for_command_and_flag('secrets', '--help')} to see more.")
        sys.exit(1)

    # Create Secret Manager Client
    client = util.create_sm_client()

    # Send to delete name delete if key is present
    if secret_name:
        # Get confirmation then send to executer
        de_util.confirm_delete(skip_confirm, "name", secret_name) # This will exit if confirmation is not succesful
        deleted_secrets = del_executer.delete_secrets(client, [secret_name], project_id)

    else:
        # Find pattern
        deletion_pattern = r'key-index_(0|[1-9]\d*)_to_(0|[1-9]\d*)' if pattern == "index-range" else r'^keystore-m_12381_3600_\d+_0_0-\d+$'

        # Get confirmation
        de_util.confirm_delete(skip_confirm, "pattern", deletion_pattern)
        matching_secrets = util.get_secret_names_matching_pattern(client, project_id, deletion_pattern)

        # Send to executer
        deleted_secrets = del_executer.delete_secrets(client, matching_secrets, project_id)


    print(f"\n[{green}SUCCESS{end}] Succesfully deleted {deleted_secrets} secrets.\n")

    return
