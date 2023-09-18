"""Handler for the 'get' subcommand of secret-manager command"""

import os

import secret_manager.validation_logic as logic
import secret_manager.get.validation_logic as get_logic
import secret_manager.get.index_range as get_range
    
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

    # Unpack subcommand flags
    while subcommand_flags:
        flag = subcommand_flags.pop()

        # Check for index range
        #TODO: All these flags get passed by default. Handle empty flag values better.
        if "--index-range" in flag:
            split_flag = flag.split("=")
            by_range = True
            low, high = get_logic.validate_index_range(split_flag[0], split_flag[1])
            break

    # Check overwirte
    if not logic.check_and_confirm_overwrite([os.path.join(output_dir, "imported_validator_keys")], output_dir):
        return

    # Route to subcommand in order of priority
    if by_range:
        get_range.get_secrets_from_index_range(low, high, project_id, output_dir)

    return
