"""Utilities for the keys_config subcommand on web3signer command"""

import os
import sys
import glob

from cli.pretty.colors import red, end
    
def get_keystore_files(key_directory_path: str) -> list:
    """
    Gets a list of all the files in the key_directory_path that match the desired keystore format of
    keystore-m_12381_3600_*_0_0-*.json. This is compliant with EIP2334.
    See https://eips.ethereum.org/EIPS/eip-2334
    https://github.com/ethereum/staking-deposit-cli/blob/master/staking_deposit/credentials.py#L155

    It exists if it does not find any files.
    """
    # Set the filename desired format and filter with glob
    desired_format = "keystore-m_12381_3600_*_0_0-*.json"
    matching_files = glob.glob(os.path.join(key_directory_path, desired_format))

    # Verify that there exists at least one keystore matching the format
    if len(matching_files) < 1:
        print(f"\n{red}[ERROR]{end} No keys matching the keystore naming format found.",
              f"\n\tExpected format is {desired_format}. See README.md for more details.")
        sys.exit(1)

    # Get all filenames paths sorted by index
    #? Sorts by i in /full/path/to/keystore-m_12381_3600_i_0_0-timestamp.json
    file_names = sorted(matching_files, key=lambda x: int(x.split("_")[-3]))
    
    return file_names

def get_all_existing_keystore_configurations(config_file: str) -> dict:
    """
        Reads the existing keystore configuration and returns a set containing all keystores.
    """
    with open(config_file, "r", encoding="utf-8") as file:
        lines = file.readlines()
        file.close()

    mapping = {}
    file_name = ""
    file_passwd = ""

    # Iterate through the lines and extract the relevant mappings
    for line in lines:
        if "keystoreFile:" in line:
            file_name = line.strip().split(": ", 1)[-1].strip("\"")
        if "keystorePasswordFile:" in line:
            file_passwd = line.strip().split(": ", 1)[-1].strip("\"")

        # Write mapping and reset
        if file_name and file_passwd:
            mapping[file_name] = file_passwd
            file_name = ""
            file_passwd = ""

    return mapping