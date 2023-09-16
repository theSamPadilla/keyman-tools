"""Prints Pretty Help Message based on config.json for the whole tool"""
from cli.pretty import *
from cli import *

def main_help():
    """Prints main help message for the tool"""    
    print(f"\n{bold}Welcome to {tool_name}!{end}")
    print(cmd_config["program-description"])
    
    # Usage String
    print(f"\n\n-----{bold}{bg_red} USAGE {end}-----")
    print(f"{bold}{green}python3 {main_file}{end} " + usage_string)

    # Global Flags
    if p_global_flags:
        print(f"\n\n-----{bold}{bg_blue} GLOBAL FLAGS {end}-----")
        print(f"{tool_name} takes {len(global_flags)} optional parameters")
        for flag, description in global_flags.items():
            print(f"- {yellow}'{flag}\'{end} ->",
            description["short"])

    # Commands
    if p_commands:
        print(f"\n\n-----{bold}{bg_blue} COMMANDS {end}-----")
        for comm, body in commands.items():
            print(f"- {red}\'{comm}\'{end} ->",
                body["description"]["short"])
    
    # Subcommands and flags 
    if p_subcommands:
        print(f"\n\n-----{bold}{bg_blue} SUBCOMMANDS {end}-----")
        for comm, body in commands.items():
            # Print subcommands if they exist
            if len(body["subcommands"]) > 0:
                print(f"{red}{bold}\'{comm}\'{end}:")
                for sub, sub_body in body["subcommands"].items():
                    print(f"\t- {pink}\'{sub}\'{end} ->",
                    sub_body["description"]["short"])

            # Print command flags if they exist
            if len(body["command-flags"]) > 0:
                print(f"\n\tCommand Flags:")
                for flag in body["command-flags"]:
                    print(f"\t- {yellow}\'{flag}\'{end}")

            # Newline
            print()

    print(f"-----{bold}{bg_blue} MORE HELP {end}-----")    
    print(f"For a full description, see the {bold}README.md{end}\n")