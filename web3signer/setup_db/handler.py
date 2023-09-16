""" Handler for setup_db subcommand on web3signer """

import os
import sys

import web3signer.utilities as util
import web3signer.setup_db.validation_logic as sdb_logic

from cli import tool_name
from cli.pretty.colors import bold, end, green, red, pink


def handler(subcommand_flags: list):
    """
    Handles slashing-protection db setup.
        1. Checks if docker and web3signer are installed
        2. Checks if web3-signer dir exists in $HOME
        3. Checks if slashing-protection is running, spins up if not.
        4. Applies the migrations on the first time the db is spun up.
    """
    # Check if docker is installed
    print("[INFO] Checking dependencies.")
    dependencies = ["docker", "web3signer"]
    for c in dependencies:
        if not util.check_command_is_installed(c):
            print(f"\n[ERROR] Missing required dependency {bold}{c}{end}.",
                f"\n\tRun {bold}{green}python3 {tool_name}{end} {red}web3signer{end} {pink}install{end}")
            sys.exit(1)

    # Check if web3signer exists
    print("\n[INFO] Checking migrations directory")
    migrations_path = sdb_logic.check_web3signer_migrations_dir()
    if not migrations_path:
        print("[ERROR] web3signer not found in $PATH")
        sys.exit(1)
    print(f"\t[✓] Found migrations at {migrations_path}")

    # Get db setup scripts path
    script_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts")

    #TODO: You are here
    # Check if slashing-protection db is running, if running exit
    #? If it is running, the migrations should have been applied.

    # Get db user and pwd and create db if not

    # Apply migrations