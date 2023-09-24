""" Handler for keys-config subcommand on web3signer """

import os

import web3signer.keys_config.utilitites as util
import web3signer.keys_config.validation_logic as logic

from cli.pretty.colors import bold, end, blue, yellow, green, red

def handler(subcommand_flags):
    """
    Handles creation of a keystore configuration file.
        1. Checks for mandatory flags
        2. Reads all the required keys
        3. Writes to the file
    """
    # Unpack the required flags
    keystore_path, password_path, output_path, key_type = logic.get_and_validate_params(subcommand_flags)

    # Get all the keystore files in keystore_path
    keystore_names = util.get_keystore_files(keystore_path)
    print(f"[INFO] Found {bold}{yellow}{len(keystore_names)}{end} keystores in {blue}{keystore_path}{end}")
 
    # Check if file exists, get all existing keystores written to this file.
    existing_keystores_to_passwd = {}
    appending = False
    if os.path.exists(output_path) and os.path.isfile(output_path):
        print(f"\n[INFO] {bold}Appending to existing{end} configuration file {blue}{output_path}{end}")
        print("\t[-] Enforcing non-repetition of keystore configuration based on secret names.")
        existing_keystores_to_passwd = util.get_all_existing_keystore_configurations(output_path)
        appending = True

    else:
        print(f"\n[INFO] {bold}Creating new{end} configuration file {blue}{output_path}{end}")

    # Open the file in append mode
    print ("\n[INFO] Writing secret information...")
    counter = 1

    with open(output_path, 'a', encoding="utf-8") as file:
        # Add divider if appending
        if appending:
            file.write("---\n") # This separates one key config from another

        # Iterate through all the secrets and write config
        # Format:
        #? type: "file-keystore"
        #? keyType: ""
        #? keystoreFile: ""
        #? keystorePasswordFile: ""
        for keystore in keystore_names:
            if keystore not in existing_keystores_to_passwd:
                file.write("type: \"file-keystore\"\n")
                file.write(f"keyType: \"{key_type}\"\n")
                file.write(f"keystoreFile: \"{keystore}\"\n")
                file.write(f"keystorePasswordFile: \"{password_path}\"\n")

                # Write a separator if there are still keystores to write
                if counter < len(keystore_names):
                    file.write("---\n") # This separates one key config from another

                # Print success, count, and add to dictionary
                print(f"\t[{green}✓{end}]Wrote configuration for {keystore} - {counter}/{len(keystore_names)}")
                existing_keystores_to_passwd[keystore] = password_path
                counter += 1

            else:
                print(f"\t[{red}x{end}] Keystore {keystore} already exists in the config file.",
                      "\n\t\tIgnoring keystore.")

        file.close()

    # Print completion
    print(f"\n[{green}SUCCESS{end}] Added {bold}{yellow}{counter-1}{end} secret configurations to {green}{output_path}{end}")

    return
