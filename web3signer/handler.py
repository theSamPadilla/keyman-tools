""" Receives calls from main, handles validation, and routes to appropriate subcommand"""

import os

import web3signer.install.handler as install
import web3signer.keys_config.handler as config
import web3signer.setup_db.handler as sdb
import web3signer.utilities as util

from cli.pretty.colors import blue, end, bold

def handler(command_flags, subcommand, subcommand_flags):
    """
    Sources .bashrc, checks web3sigenr logic and routes subcommands
    """
    # Check for authorize-bash flag
    authorize = "--authorize-bash" in command_flags

    # Source .bashrc
    brc_path = os.path.expanduser('~/.bashrc')
    if util.read_bashrc():
        print(f"\n[INFO] Found PATH entries in {blue}{brc_path}{end} and updated {blue}{bold}$PATH{end}.\n")
    else:
        print(f"\n[INFO] No PATH entries or no file found at {blue}{brc_path}{end}.\n")

    # Route
    if subcommand == "install":
        install.handler(subcommand_flags, authorize)
    elif subcommand == "keys-config":
        config.handler(subcommand_flags)
    elif subcommand == "setup-db":
        sdb.handler(subcommand_flags, authorize)

    return
