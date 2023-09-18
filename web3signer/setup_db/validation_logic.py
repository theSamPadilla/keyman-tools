""" Validation functions for web3signer setup_db """

import os
import sys
import subprocess

import web3signer.utilities as util
from cli.pretty.colors import red, end, green, bold

# Check
def check_web3signer_migrations_dir() -> str:
    """
    Checks that the PATH location of web3signer contains the migrations/postgresql directory.
    Returns the directory if it exists, "" otherwise
    """
    print("\n[INFO] Checking postgres migrations directory.")

    # Run process and capture stdout
    r = subprocess.run(["which", "web3signer"], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       text=True, check=False)

    # Command not found
    if r.returncode != 0:
        return ""

    # Get the web3signer directory from $PATH location
    #? 'which web3signer' will point to the bin in the location directory
    w3s_dir = os.path.dirname(os.path.dirname(r.stdout)) #Get grandparent dir

    # Set the migrations directory path
    migrations_dir = os.path.join(w3s_dir, "migrations", "postgresql")

    # Check the location exists
    if os.path.exists(migrations_dir) and os.path.isdir(migrations_dir):
        print(f"\t[{green}✓{end}] Found postgres migrations at {green}{migrations_dir}{end}")
        return migrations_dir
    
    # Return empty if the location on $PATH was not found
    return ""

# Helpers
def get_db_user_and_password(params: list) -> tuple:
    """
    Parses the subcommand flags passed in params to find the user and password for the db
    Returns: user, passwd
    """
    user = ""
    passwd = ""
    while params:
        param = params.pop()
        if "--db-user" in param:
            user = param.split("=")[-1]
        elif "--db-password" in param:
            passwd = param.split("=")[-1]
    return user, passwd

def get_container_id(container_name: str) -> str:
    """
    Runs docker subprocesses to check for the container id.
    Args:
        container_name: The name of the container. Hardcoded on caller to be slashing-protection-db
    Returns: The id of the container or an empty string if no container is found.
    """
    print(f"\n[INFO] Checking for {container_name} container ID.")

    # Run process and capture stdout
    r = subprocess.run(["docker", "ps", "--quiet", "--filter", f"name={container_name}"],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)

    # Command found
    #? This throws an error because the command itself failed for some unknown reason.
    if r.returncode != 0:
        print(f"\n{red}[ERROR]{end} Failed to look for the slashing-protection-db")
        sys.exit(1)

    # Return id if found
    container_id = r.stdout.strip()
    if r.stdout:
        print(f"\t[{green}✓{end}] Found container with id {bold}{container_id}{end}.")
        return container_id
    
    print(f"\t[{red}x{end}] Container {container_name} not found.")
    return ""

# Make
def start_slashing_protection_db(container_name: str, migrations_path: str,
                                 usr: str, passwd: str, script_path: str, authorize: bool) -> str:
    """
    Starts a docker container with the slashing protection database. 
    Args:
        container_name: The name of the container. Hardcoded on caller to be slashing-protection-db 
        migrations_path: The directory path to the postgresql migrations directory.
        user: The postgres user, defined on by the subcommand flag.
        passwd: The postgres user password, defined on by the subcommand flag.
        script_path: Path to the docker startup script. 
        authorize: Authorization flag. Prompts for confirmation if set to True.
    Returns: The container ID of the created container.
    """

    print(f"\n[INFO] Starting up {container_name} container.")
    if not authorize:
        print("\nGrant permissions for installation below:")
        if not util.confirm_script_execution(script_path):
            sys.exit(0)

    # Run process and output stderr and stdout
    r = subprocess.run(["bash", script_path, migrations_path, usr, passwd],
                         text=True, check=False)

    # Running the process failed
    if r.returncode != 0:
        print(f"\n{red}[ERROR]{end} Failed the database startup script.")
        sys.exit(1)

    print(f"\n\n[INFO] Succesfully started {container_name}.")

    # Else get and return the container id
    return get_container_id(container_name)

def apply_db_migrations(container_id: str, migrations_path: str,
                                usr: str, script_path: str, authorize: bool):
    """
    Starts a docker container with the slashing protection database. 
    Args:
        container_name: The id of the container. 
        migrations_path: The directory path to the postgresql migrations directory.
        user: The postgres user, defined on by the subcommand flag.
        script_path: Path to the docker startup script. 
        authorize: Authorization flag. Prompts for confirmation if set to True.
    Returns: The container ID of the created container.
    """

    print(f"\n[INFO] Applying migrations to container id {container_id}")
    if not authorize:
        print("\nGrant permissions for installation below:")
        if not util.confirm_script_execution(script_path):
            sys.exit(0)

    # Run process and output stdout and stderr
    r = subprocess.run(["bash", script_path, migrations_path, container_id, usr],
                        text=True, check=False)

    # Running the process failed
    if r.returncode != 0:
        print(f"\n{red}[ERROR]{end} Failed to run the database startup script.")
        sys.exit(1)

    print(f"\n[INFO] Succesfully applied migrations to {container_id}.")
