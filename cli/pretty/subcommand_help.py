"""Prints Pretty Help Message for a given subcommand based on
the values of the subcommand in config.json"""

from cli.utilities import print_usage_string_for_command_and_subcommand
from cli.pretty import *
from cli import *

def subcommand_help(command: str, subcommand: str):
    """Prints help message for a given subcommand"""    

    # Command print
    print(f"\nSubcommand: {bold}{pink}{subcommand}{end}")

    # Usage String
    print(f"\n-----{bold}{bg_red} Usage {end}-----")
    print(f"{print_usage_string_for_command_and_subcommand(command, subcommand)} {yellow}[SUBCOMMAND FLAGS]{end}")

    # Description
    print(f"\n{bold}Description:{end}")
    print(f"{commands[command]['subcommands'][subcommand]['description']['long']}")

    # Subcommand Flags
    if len(commands[command]['subcommands'][subcommand]["subcommand-flags"]) > 0:
        print(f"\n-----{bold}{bg_blue} Subcommand Flags {end}-----")

        for flag, flag_body in commands[command]['subcommands'][subcommand]["subcommand-flags"].items():

            #Check if the flag takes values (aka it is always on)
            if len(flag_body["values"]) > 0:
                # Catch wildcard values
                print(f"{bold}{yellow}\'{flag}=<value>\'{end}\n{flag_body['description']}")
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