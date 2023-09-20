"""Utiliites for the cli package"""

from cli import main_file
from cli.pretty import end, bold, green, red, pink, yellow

def print_usage_string_for_command_and_subcommand(command: str, subcommand: str) -> str:
    """Prints the usage string with the provided command and subcommand"""
    return f"{green}{bold}python3 {main_file}{end} {red}{command}{end} {pink}{subcommand}{end}"

def print_usage_string_for_command_and_flag(command: str, flag: str) -> str:
    """Prints the usage string with the provided command and subcommand"""
    return f"{green}{bold}python3 {main_file}{end} {red}{command}{end} {yellow}{flag}{end}"
