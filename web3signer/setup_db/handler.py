""" Handler for setup_db subcommand on web3signer """

import os
import sys

import web3signer.utilities as util
import web3signer.setup_db.validation_logic as sdb_logic

from cli.utilities import print_usage_string_for_command_and_subcommand
from cli.pretty import red, end, green

def handler(subcommand_flags: list, authorize: bool):
    """
    Handles slashing-protection db setup.
        1. Checks if docker and web3signer are installed
        2. Checks if web3-signer dir exists in $HOME
        3. Checks if slashing-protection is running, spins up if not.
        4. Applies the migrations on the first time the db is spun up.
    """
    # Check dependencies
    util.check_dependencies(["docker", "web3signer"])

    # Check if web3signer exists
    migrations_path = sdb_logic.check_web3signer_migrations_dir()
    if not migrations_path:
        print(f"\n{red}[ERROR]{end} web3signer not found in $PATH.",
                f"\n\t Install it manually or run {print_usage_string_for_command_and_subcommand('web3signer', 'install')}")
        sys.exit(1)

    # Get db setup scripts path
    script_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts")

    # Check if slashing-protection db is running
    container_name = "slashing-protection-db" # Do not change this. It is hardcoded in the bash scripts
    container_id = sdb_logic.get_container_id(container_name)

    #? If it is running, the migrations should have been applied, return
    if container_id:
        print(f"\n\n[{green}SUCCESS{end}] Slashing protection database setup complete.")
        return

    # Get script path
    start_db_path = os.path.join(script_dir, "run-db.sh")

    # Get db user and pwd and create db
    user, passwd = sdb_logic.get_db_user_and_password(subcommand_flags)
    container_id = sdb_logic.start_slashing_protection_db(container_name, migrations_path,
                                                          user, passwd, start_db_path, authorize)

    # Exit if container_id was not found, this should be an error.
    if not container_id:
        print(f"\n{red}[ERROR]{end} Creation or lookup of {container_name} failed.")
        sys.exit(1)

    # Get migrations script path, authorizaition, and apply migrations
    apply_migrations_script_path = os.path.join(script_dir, "database_migration.sh")
    sdb_logic.apply_db_migrations(container_id, migrations_path, user,
                                  apply_migrations_script_path, authorize)

    print(f"\n\n[{green}SUCCESS{end}] Slashing protection database setup complete.")
