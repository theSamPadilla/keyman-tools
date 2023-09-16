"""Config package to setup the tool"""

import os
import json

from cli.pretty import *

# Get and verify config.json
def get_cmd_config():
    """Opens and gets the cmd_config.json config file"""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

    # Get cmd configs
    with open(path, "r", encoding="utf-8") as c:
        config = json.load(c)
        c.close()
    
    return config

# Parse configs
def get_usage_string() -> str:
    """Parses the usage booleans to build the usage message"""
    usage = ""

    if p_global_flags:
        usage += f"{yellow}[GLOBAL_FLAGS]{end} "
    if p_commands:
        usage += f"{red}[COMMAND]{end} "
    if p_command_flags:
        usage += f"{yellow}[COMMAND_FLAGS]{end} "
    if p_subcommands:
        usage += f"{pink}[SUBCOMMAND]{end} "
    if p_subcommand_flags:
        usage += f"{yellow}[SUBCOMMAND_FLAGS]{end}"

    return usage

# Get the cmd file and validate it
cmd_config = get_cmd_config()

# Tool properties
tool_name = cmd_config["name"] #? str
main_file = cmd_config["main-file"] #? str

# Usage Bools
p_global_flags = cmd_config["usage"]["global-flags"] #? bool
p_commands = cmd_config["usage"]["commands"] #? bool
p_command_flags = cmd_config["usage"]["command-flags"] #? bool
p_subcommands = cmd_config["usage"]["subcommands"] #? bool
p_subcommand_flags = cmd_config["usage"]["subcommand-flags"] #? bool

# Usage string
usage_string = get_usage_string() #? str

# Commands, global_flags, and output dicts
global_flags = cmd_config["global-flags"] #? dict
commands = cmd_config["commands"] #? dict
