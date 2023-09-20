"""Utilities for the get subcommand on secret-manager command"""

import sys

from cli.pretty.colors import yellow, end, bold, red

def confirm_delete(authorize: bool, delete_mode:str, name_or_pattern: str):
    """
    Prompts the user for confirmation if the authorize confirmation is not passed.
    
    Args:
        authorize: Boolean indicating whether to prompt for confirmation or not.
        delete_mode: 'name' or 'pattern'.
        name_or_pattern: The name of the secret to be deleted or the pattern for deletion.
    """
    if delete_mode == "name":
        message = f"the secret {name_or_pattern}. This action is {red}{bold}irreversible{end}."
    else:
        message = f"all secrets matching the pattern {name_or_pattern}. This can mean multiple secrets deleted. This is action is {red}{bold}irreversible{end}."

    # Set secret name
    if not authorize:
        input_message = f"{yellow}[WARN]{end} You are about to delete {message}\n\tDo you want to proceed?{end} (yes only - anything else will halt.)\n\t\t"
        response = input(input_message)
        if response.lower() != 'yes':
            print("\n\nAborting.\n")
            sys.exit(1)

    print()
    return
