""" Validation functions for web3signer install """

import subprocess
import os
import sys

from cli.pretty.colors import bg_red, bold, end, green, yellow
from web3signer.utilities import read_bashrc

# Check installations
def check_command_is_installed(command: str) -> bool:
    """Checks if the passed command is installed. Returns true if yes, false otherwise"""
    print(f"[INFO] Looking for command: {bold}{command}{end}.")

    r = subprocess.run(["which", command], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    #Command found
    if r.returncode == 0:
        print(f"\t[✓] {bold}{command}{end} found at {green}{r.stdout}{end}")
        return True

    # Not found
    print(f"\t[x] {bold}{command}{end} not installed.")
    return False
    
# Install commands
def run_installation_script(path: str):
    """
    Run the provided script and runs .bashrc to apply the changes.
    Args:
        path: Path to an installation script.
    """
    if not os.path.isfile(path) or not path.endswith('.sh'):
        print(f"[ERROR] Provided path {path} is not a a valid bash script")
        sys.exit()
    
    subprocess.run(["bash", path])
    read_bashrc()
    return

# Confirm
def confirm_script_execution(script: str) -> bool:
    """
        Confirm the user wants to execute the script.
    """
    input_message = f"{yellow}[WARN]{end} This command is about to {bold}execute the commands{end} in {green}{script}{end}.\n\tThis may alter your computer configurations, make sure you have verified the code that is about to execute.\n\n\t{bg_red}{bold}Do you want to proceed?{end} {bold}(yes only - anything else will halt.){end}\n\t\t"
    response = input(input_message)
    if response.lower() != 'yes':
        return False

    print()
    return True