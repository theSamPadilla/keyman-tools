"""Utiliites for the cli package"""

from cli import tool_name
from cli.pretty import end, bold, green, red, pink

def print_usage_string(command: str, subcommand: str) -> str:
    """Prints the usage string with the provided command and subcommand"""
    return f"{green}{bold}python3 {tool_name}{end} {red}{command}{end} {pink}{subcommand}{end}."