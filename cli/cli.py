"""Collection of config and setup functions for the tool"""
from cli.pretty import *
from cli import *

import cli.pretty.main_help as main_help
import cli.pretty.command_help as cmd_help

def param_parser(params) -> list:
    """
        Parses and checks the parameters of the application based on the commands defined on cmd.json.
        It handles help printing without returning.
        Returns only if valid instructions are passed.

        Args:
            parms: sys.argv
        Returns:
            [command, [command-flags], subcommand, [subcommand-flags]}
    """
    # Check for help command (tool-level help)
    if "help" in params:
        main_help.main_help()
        exit(0)
    
    command = ""
    command_flags = []
    subcommand = ""
    subcommand_flags = []

    # Check for command
    if len(params) < 1:
        print(f"[ERROR] No command passed to {bold}{green}{main_file}{end}.",
              f"\n\tRun '{bold}{green}python3 {main_file}{end} {red}help{end}' to see usage.")
        return []

    # Pop command and check validity
    command = params.pop(0)
    if command not in cmd_config["commands"]:
        print(f"[ERROR] Invalid command '{bg_black}{command}{end}'.",
              f"\n\tValid commands are {red}{list(cmd_config['commands'].keys())}{end}.")
        return []

    # Get command flags
    buff = get_command_flags(cmd_config["commands"][command]["command-flags"], params, command)
    params = buff["params"]
    command_flags = buff["command_flags"]
    subcommand = buff["subcommand"]

    # Get default subcommand for this command
    default_sub = cmd_config["commands"][command]["subcommand-logic"]["default"]
    
    # Check for at least a passed subcommand or a default sub
    #? An empty string on the subcommand-logic->default means required subcommands.
    if not subcommand and not default_sub:
        print(f"[ERROR] Command '{red}{command}{end}' requires a subcommand.",
            f"\n\tRun '{green}{bold}python3 {main_file}{end} {red}{command} {yellow}--help{end}' for command help.")
        return []
        
    if subcommand:
        # Check subcommand validity
        if subcommand not in cmd_config["commands"][command]["subcommands"]:
            print(f"[ERROR] Invalid subcommand '{bg_black}{command} {subcommand}{end}'.",
                f"\n\tValid subcommands for {red}{command}{end} are {pink}{list(cmd_config['commands'][command]['subcommands'].keys())}{end}.")
            return []
        #? Else subcommand is valid

    # If there is no passed subcommand, assign the default
    else:
        subcommand = default_sub

    # Get subcommand flags
    subcommand_flags = get_subcommand_flags(
        cmd_config["commands"][command]["subcommands"][subcommand]["subcommand-flags"],
        params, command, subcommand)

    return [command, command_flags, subcommand, subcommand_flags]

# Helper Functions #
def get_command_flags(valid_flags:list, params:list, command:str) -> dict:
    """
        Gets the command flags for a given command.
        Handles warning and help invocation.
        Returns a map of conataining the remaining parameters, the valid flags, and the next subcommand. 
    """
    command_flags = []

    # Get the next flag if it exists
    next_flag = params.pop(0) if params else ""

    # Iterate through params checking for valid command flags #?Flags denoted by --
    while "--" in next_flag:
        # Get flag head
        #? Some flags may be key=value flags
        flag_to_val = next_flag.split("=")
        flag_head = flag_to_val[0]
        
        # Warn and ignore if flag is not valid
        if flag_head not in valid_flags:
            print(f"[WARN] Invalid flag '{yellow}{flag_head}{end}' for command '{red}{command}{end}'.",
                  "Ignoring and proceeding.")
        
        # If flag head is valid 
        else:
            # Catch command helps
            if flag_head == "--help":
                cmd_help.command_help(command)
                exit(0)
            
            # Get possible values for this flag head
            valid_flag_value = valid_flags[flag_head]["values"]

            # If there are multiple values for the flag head
            #? If there are not multiple values for the flag head, it is a boolean flag
            if len(valid_flag_value) > 0:
                flag_value = flag_to_val[1] # Get the value passed to the flag

                # If passed value is not valid, warn and use default
                if flag_value not in valid_flag_value:
                    print(f"[WARN] Invalid value '{bold}{flag_value}{end}' for flag '{yellow}{flag_head}{end}'.",
                    f"Ignoring and using default '{blue}{valid_flags[flag_head]['default']}{end}'.")
                    next_flag = f"{flag_head}={valid_flags[flag_head]['default']}"
                
                # If passed value is valid, build flag with value
                else:
                    next_flag = f"{flag_head}={flag_value}"

            # Else append the flag
            command_flags.append(next_flag)
        
        # Get the next flag if remaining parameters or break
        if params:
            next_flag = params.pop(0)
        else:
            break
    
    #? The while loop breaks either when there are no more params or when a non-flag parameter is reached
    # Assign the last flag as subcommand if it does not contain --, else there is no more params and no subcommand.
    subcommand = next_flag if "--" not in next_flag else ""

    return {
        "params": params,
        "subcommand": subcommand,
        "command_flags": command_flags
    }

def get_subcommand_flags(valid_flags:list, params:list, command:str, subcommand:str) -> list:
    """
        Gets the subcommand flags for a given subcommand.
        Handles warning locally.
        Returns a list of the valid flags. 
    """
    subcommand_flags = []

    # Get the next flag if it exists
    next_flag = params.pop(0) if params else ""

    # If no params exist, check for mandatory subcommand flags and pass default
    if not params:
        for flag_head, flag_body in valid_flags.items():

            #? A mandatory (aka always on) flag has at least one value
            #? It is up to the subcommand handler to implement the logic for what flag to prioritize.
            if len(flag_body["values"]) > 0:
                subcommand_flags.append(f"{flag_head}={flag_body['default']}")

    # Iterate through params checking for valid command flags #?Flags denoted by --
    while "--" in next_flag:
        # Get flag head
        #? Some flags may be key=value flags
        flag_to_val = next_flag.split("=")
        flag_head = flag_to_val[0]

        # Warn and ignore if flag head is not valid.
        if flag_head not in valid_flags:
            print(f"[WARN] Invalid flag '{yellow}{flag_head}{end}' for '{red}{command}{end} {pink}{subcommand}{end}'.",
                "Ignoring and proceeding.")
            
        # If flag head is valid
        else:
            
            # Get possible values for this flag head
            valid_flag_value = valid_flags[flag_head]["values"]

            # If there is at least one value for the flag head
            #? If there are not multiple values for the flag head, it is a boolean flag
            if len(valid_flag_value) > 0:
                flag_value = flag_to_val[1] # Get the value passed to the flag

                # Catch wildcard value "", build flag with value passed
                if "" in valid_flag_value:
                    next_flag = f"{flag_head}={flag_value}"

                # If passed value is not valid, warn and use default
                elif flag_value not in valid_flag_value:
                    print(f"[WARN] Invalid value '{bold}{flag_value}{end}' for flag '{yellow}{flag_head}{end}'.",
                    f"Ignoring and using default '{blue}{valid_flags[flag_head]['default']}{end}'.")
                    next_flag = f"{flag_head}={valid_flags[flag_head]['default']}"
                
                # If passed value is valid, build flag with value
                else:
                    next_flag = f"{flag_head}={flag_value}"

            subcommand_flags.append(next_flag)
        
        # Get the next flag if remaining parameters or break
        if params:
            next_flag = params.pop(0)
        else:
            break
    
    #? Any non-flag instructions after this gets ignored
    
    return subcommand_flags