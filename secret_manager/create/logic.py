"""Validation logic for create subcommand"""
import os

# Confirm overwrite of output
def check_and_confirm_overwrite(output_dir: str) -> bool:
    """
        Checks for existing output files and confirms overwrite if they exist
    """
    # Check if the output files exist
    exists_pf = os.path.exists(f"{output_dir}public_keys.txt")
    exists_nf = os.path.exists(f"{output_dir}secret_names.txt")
    exists_ptnf = os.path.exists(f"{output_dir}secret_names_to_pubkeys.txt")
    
    # Confirm overwrite
    if exists_nf or exists_pf or exists_ptnf:
        input_message = f"[WARN] There are public keys and secret files already in {output_dir}\n\tDo you want to overwrite them? (yes only - anything else will halt.)\n\t\t"
        response = input(input_message)
        if response.lower() != 'yes':
            return False
    
    print()
    return True