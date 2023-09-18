""" Handler for install subcommand on web3signer """

import os
import sys

from cli import tool_name
from cli.utilities import print_usage_string_for_command_and_subcommand
from cli.pretty.colors import yellow, end, red

import web3signer.utilities as util
import web3signer.install.validation_logic as in_logic

def handler(subcommand_flags, authorize: bool):
    """
    Handles installation validation.
        1. Checks if the java sdk is installed, installs it if not and if authorized.
        2. Checks that docker is reachable, installs if --linux-distro flag was provided.
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

        # Get the --linux-distro value
        linux_distro = subcommand_flags.pop().split("=")[-1] # --linux-distro is the only flag passed

        # Get the installation script for the distro and install
        if linux_distro:
            docker_install_script = os.path.join(script_dir, "docker", f"install_docker_{linux_distro}.sh")
            in_logic.run_installation_script(docker_install_script, "docker", authorize)

        # Else print error and exit
        else:
            print(f"\n{red}[ERROR]{end} Docker is not installed or could not be reached by {tool_name}.",
                    f"\n\t{tool_name} supports docker instalation for Ubuntu and Debian.\n\tTo install docker for your linux distro, run:",
                    f"\n\t{print_usage_string_for_command_and_subcommand('web3signer', 'install')} {yellow}--linux-distro=<bedian-or-ubuntu>{end}.")
            sys.exit(1)

    # Install web3signer it is not installed
    if not util.check_command_is_installed("web3signer"):
        w3s_install_path = os.path.join(script_dir, "install_web3signer.sh")
        in_logic.run_installation_script(w3s_install_path, "web3signer", authorize)

    print("\n[INFO] Installation completed.\n")

    return
