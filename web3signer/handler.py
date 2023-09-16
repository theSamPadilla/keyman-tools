""" Receives calls from main, handles validation, and routes to appropriate subcommand"""

import os

import web3signer.install.handler as install
import web3signer.config.handler as config
import web3signer.run.handler as run
import web3signer.utilities as util
from cli.pretty.colors import blue, end, bold

def handler(_, subcommand, subcommand_flags):
    """
    Sources .bashrc, checks web3sigenr logic and routes subcommands
    """
    #? No command flags to validate
    # Source .bashrc
    brc_path = os.path.expanduser('~/.bashrc')
    if util.read_bashrc():
        print(f"[INFO] Found PATH entries in {blue}{brc_path}{end} and updated {blue}{bold}$PATH{end}.\n")
    else:
        print(f"[INFO] No PATH entries or no file found at {blue}{brc_path}{end}.\n")

    # Route
    if subcommand == "install":
        install.handler(subcommand_flags)
    elif subcommand == "config":
        print("Config WIP")
        config.handler(subcommand_flags)
    elif subcommand == "setup-db":
        print("Setup db WIP")
        run.handler(subcommand_flags)
    elif subcommand == "run":
        print("Run WIP")
        run.handler(subcommand_flags)
    return