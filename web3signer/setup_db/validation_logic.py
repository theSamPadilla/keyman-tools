""" Validation functions for web3signer setup_db """

import os
import subprocess
    
# Check
def check_web3signer_migrations_dir() -> str:
    """
    Checks that the PATH location of web3signer contains the migrations directory.
    Returns the directory if it exists, "" otherwise
    """
    r = subprocess.run(["which", "web3signer"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Command not found
    if r.returncode != 0:
        return ""
    
    # Get the web3signer directory from $PATH location
    #? 'which web3signer' will point to the bin in the location directory
    w3s_dir = os.path.dirname(os.path.dirname(r.stdout)) #Get grandparent dir
    
    # Set the migrations directory path
    migrations_dir = os.path.join(w3s_dir, "migrations")

    # Check the location exists
    if os.path.exists(migrations_dir) and os.path.isdir(migrations_dir):
        return migrations_dir

# Helpers
def get_db_user_and_password(params: list) -> tuple:
    """Parses the params to find the user and password for the db"""
    user = ""
    passwd = ""
    while params:
        param = params.pop()
        if "--db-user" in param:
            user = param.split("=")[-1]
        elif "--db-passwd" in param:
            passwd = param.split("=")[-1]
    return user, passwd