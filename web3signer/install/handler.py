""" Handler for install subcommand on web3signer """

import os
import sys

from cli import tool_name
from cli.pretty.colors import green, end

import web3signer.utilities as util
import web3signer.install.validation_logic as in_logic

def handler(_):
    """
    Handles installation validation.
        1. Checks if the java sdk is installed, installs it if not and if authorized.
        2. Checks that docker is reachable, halts if not.
        3. Checks if web3signer is installed the script, installs it if not and if authorized.
    """
    # Get installation scripts path
    script_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts")

    # Install Java if it is not installed and authorized.
    if not util.check_command_is_installed("java"):
        print("\nGrant permissions for installation below:")
        java_install_path = os.path.join(script_dir, "install_java_sdk.sh")
        if not in_logic.confirm_script_execution(java_install_path):
            return
        in_logic.run_installation_script(java_install_path)
    
    # Verify docker is installed
    if not util.check_command_is_installed("docker"):
        print(f"\n[ERROR] Docker is not installed or could not be reached by {tool_name}.",
                f"\n\t{tool_name} will not install Docker for you since docker installation varies for each linux distribution.",
                f"\n\tCheck {green}{os.path.join(script_dir, 'docker')}{end} for sample installation scripts for linux and debian.")
        sys.exit(1)

    # Install web3signer it is not installed and authorized.
    if not util.check_command_is_installed("web3signer"):
        print("\nGrant permissions for installation below:")
        w3s_install_path = os.path.join(script_dir, "install_web3signer.sh")
        if not in_logic.confirm_script_execution(w3s_install_path):
            return
        in_logic.run_installation_script(w3s_install_path)

    print("\n[INFO] Installation completed.\n")

    return
