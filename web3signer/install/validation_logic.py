""" Validation functions for web3signer install """

import os
import sys
import subprocess

import web3signer.utilities as util
from cli.pretty.colors import red, end
    
# Install commands
def run_installation_script(path: str, command: str, authorize: bool):
    """
    Run the provided script and runs .bashrc to apply the changes.
    Args:
        path: Path to an installation script.
        command: The command that is getting installed
        authorize: Authorization flag. Prompts for confirmation if set to True.
    """

    print(f"\n[INFO] Installing {command}.")

    # Prompt for authorization if not authorized
    if not authorize:
        print("\nGrant permissions for installation below:")
        if not util.confirm_script_execution(path):
            sys.exit(0)

    if not os.path.isfile(path) or not path.endswith('.sh'):
        print(f"\n{red}[ERROR]{end} Provided path {path} is not a a valid bash script")
        sys.exit(1)
    
    # Run script and output stdout and stderr
    subprocess.run(["bash", path], check=False)
    util.read_bashrc()
    return
