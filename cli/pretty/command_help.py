"""Prints Pretty Help Message for a given command based on
the command-help value of the command in config.json"""
from cli.pretty import *
from cli import *

def command_help(command: str):
    """Prints help message for a given command"""    

    # Command print
    print(f"\nCommand: {bold}{red}{command}{end}")

    # Usage String
    print(f"\n-----{bold}{bg_red} Usage {end}-----")
    print(get_command_usage_string(command))

    # Description
    print(f"\n{bold}Description:{end}")
    print(f"{commands[command]['description']['long']}")

    # Flags
    if len(commands[command]["command-flags"]) > 0:
        print(f"\n\n-----{bold}{bg_blue} Command Flags {end}-----")
        for flag, flag_body in commands[command]["command-flags"].items():
            print(f"{yellow}\'{flag}\'{end}\n{flag_body['description']['long']}")
            if flag_body['default']:
                print(f"\t{bold}Default: {flag_body['default']}{end}")
            print()

    # Subcommands
    if len(commands[command]["subcommands"]) > 0:
        print(f"-----{bold}{bg_blue} Subcommands {end}-----")

        for subcomm, body in commands[command]["subcommands"].items():
            print(f"{bg_pink}Subcommand:{end} {pink}{bold}\'{subcomm}\'{end}")
            print(f"{body['description']['long']}")

            # Print subcommandcommand flags if they exist
            if len(body["subcommand-flags"]) > 0:
                print(f"\n{bg_black}Subcommand Flags:{end}")
                for flag, flag_body in body["subcommand-flags"].items():

                    #Check if the flag takes values (aka it is always on)
                    if len(flag_body["values"]) > 0:

                        # Catch wildcard values
                        print(f"{yellow}\'{flag}=<value>\'{end}\n{flag_body['description']}")
                        if "" in flag_body["values"]:
                            if flag_body['default']:
                                print(f"{bg_black}{bold}default{end}: {blue}{flag_body['default']}{end}")
                            print()
                            continue

                        # Print accepted values
                        print(f"\t{bold}Accepted Values:{end}")

                        for val, desc in flag_body['values'].items():
                            print(f"\t- {blue}{val}{end}:\n\t{desc}")

                        # Print default if it exists
                        if flag_body['default']:
                            print(f"\t{bg_black}{bold}default{end}: {blue}{flag_body['default']}{end}")
                        print()

                    #Boolean flags
                    else:
                        print(f"{yellow}\'{flag}\'{end}\n{flag_body['description']}")
                        print(f"{bg_black}{bold}default{end}: {blue}{flag_body['default']}{end}")
                        print()
            print("\n")

def get_command_usage_string(command: str) -> str:
    """Gets the usage string for the command passed"""
    usage = f"{green}python3 {main_file} {bold}{red}{command}{end}"

    if len(commands[command]["command-flags"]) > 0:
        usage += f" {yellow}[FLAGS]{end}"
         
    if len(commands[command]["subcommands"]) > 0:
        usage += f" {pink}[SUBCOMMANDS]{end}"

    for sub in commands[command]["subcommands"]:
        if len(commands[command]["subcommands"][sub]["subcommand-flags"]) > 0:
            usage += f" {yellow}[SUBCOMMAND_FLAGS]{end}"
            break
    
    return usage