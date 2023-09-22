"""Handler for the 'get' subcommand of secrets command"""

import os

import secrets.validation_logic as logic
import secrets.get.validation_logic as get_logic
import secrets.get.index_range as get_range
import secrets.get.secret_name as get_name
    
def handler(subcommand_flags: list, project_id: str, output_dir: str):
    """
    Handles create subcommand logic.
        1. Unpacks subcommand flags
        2. Checks validity of the flags
        3. Checks for overwrite
        4. Routes to subcommand execution    
    """
    # Define subcommand bool flags
    by_range = False
    by_name = False

    # Unpack subcommand flags
    while subcommand_flags:
        
        # Get only the flags with a value
        flag_head_to_val = subcommand_flags.pop().split("=")
        if len(flag_head_to_val) > 1:

            # Get the flag head
            flag = flag_head_to_val[0]
            flag_value = flag_head_to_val[1]

            # Check for name - this breaks immediately since it takes priority
            if "--secret-name" in flag:
                by_name = True
                target_secret_name = flag_value
                break

            # Check for index range
            if "--index-range" in flag:
                by_range = True
                low, high = get_logic.validate_index_range(flag, flag_value)

    # Check overwirte
    if not logic.check_and_confirm_overwrite([os.path.join(output_dir, "imported_validator_keys")], output_dir):
        return

    # Route to subcommand in order of priority
    if by_name:
        get_name.get_secrets_from_name(project_id, output_dir, target_secret_name)
    elif by_range:
        get_range.get_secrets_from_index_range(low, high, project_id, output_dir)

    return
