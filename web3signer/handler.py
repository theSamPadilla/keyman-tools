""" Receives calls from main, handles validation, and routes to appropriate subcommand"""

import web3signer.install.handler as install
import web3signer.config.handler as config
import web3signer.run.handler as run

def handler(_, subcommand, subcommand_flags):
    """
    Checks web3sigenr logic and routes subcommands
    """

    #? No command flags to validate

    # Route
    if subcommand == "install":
        install.handler(subcommand_flags)
    elif subcommand == "config":
        print("Config WIP")
        config.handler(subcommand_flags)
    elif subcommand == "run":
        print("Run WIP")
        run.handler(subcommand_flags)
    return