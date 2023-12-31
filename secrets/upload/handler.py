"""Handler for 'upload' subcommand on secrets command"""
import os

import secrets.validation_logic as logic
import secrets.upload.single as single
import secrets.upload.fat as fatty

def handler(subcommand_flags: list, project_id: str, key_directory_path: str, output_dir: str):
    """
    Handles upload subcommand logic.
        1. Unpacks subcommand flags
        2. Confirms overwrite
        3. Routes to subcommand execution    
    """
    # Intialize flags
    skip = False
    optimistic = False

    #Unpack subcommand flags
    while subcommand_flags:
        flag = subcommand_flags.pop()
        if flag == "--skip":
            skip = True
        elif flag == "--optimistic":
            optimistic = True
        elif "--secret-mode" in flag:
            secret_mode = flag.split("=")[1]
    
    #Confirm overwrite
    output_files = [
        os.path.join(output_dir, "public_keys.txt"),
        os.path.join(output_dir, "secret_names.txt"),
        os.path.join(output_dir, "secret_names_to_pubkeys.txt")
    ]
    if not logic.check_and_confirm_overwrite(output_files, output_dir):
        return

    #Route to subcommand execution
    if secret_mode == "fat":
        fatty.create_fat_secrets(project_id, key_directory_path, output_dir) #? Fat secrets don't skip nor are optimistic
    else:
        single.create_single_secrets(project_id, key_directory_path, output_dir, optimistic, skip)

    return