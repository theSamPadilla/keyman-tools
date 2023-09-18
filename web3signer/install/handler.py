""" Handler for install subcommand on web3signer """

import os
import sys

from cli import tool_name
from cli.pretty.colors import green, end, red

import web3signer.utilities as util
import web3signer.install.validation_logic as in_logic

def handler(_, authorize: bool):
    """
    Handles installation validation.
        1. Checks if the java sdk is installed, installs it if not and if authorized.
        2. Checks that docker is reachable, halts if not.
        3. Checks if web3signer is installed the script, installs it if not and if authorized.
    
    Args:
        _: Subcommand flags passed to every handler.
        authorize: Boolean on whther authorization before script execution is required.
    
    """
    # Get installation scripts path
    script_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts")

    # Install Java if it is not installed
    if not util.check_command_is_installed("java"):
        java_install_path = os.path.join(script_dir, "install_java_sdk.sh")
        in_logic.run_installation_script(java_install_path, "java", authorize)

    # Verify docker is installed
    if not util.check_command_is_installed("docker"):
        print(f"\n{red}[ERROR]{end} Docker is not installed or could not be reached by {tool_name}.",
                f"\n\t{tool_name} will not install Docker for you since docker installation varies for each linux distribution.",
                f"\n\tCheck {green}{os.path.join(script_dir, 'docker')}{end} for sample installation scripts for linux and debian.")
        sys.exit(1)

    # Install web3signer it is not installed
    if not util.check_command_is_installed("web3signer"):
        w3s_install_path = os.path.join(script_dir, "install_web3signer.sh")
        in_logic.run_installation_script(w3s_install_path, "web3signer", authorize)

    print("\n[INFO] Installation completed.\n")

    return
