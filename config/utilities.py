"""Utility functions for config package"""

def print_help():
    """Prints help message"""
    print("\nWelcome to the bls keys to secret manager tool!")
    print("This tool creates Google Cloud Secret Manager entries",
          "for all the validator keys in the target directory defined in",
          "the \'.env\' file.")

    print("\n\n----- PARAMETERS -----")
    print("The tool takes 3 optional parameters")
    print("- \'optimistic\' ->",
        "Makes the tool not check the validator keystore cheksum with the",
        "checksum of the created secret.")
    print("- \'skip\' -> Makes the tool skip a version update of existing secrets.")
    print("- \'help\' -> Prints this message.")

    print("\n\n----- OUTPUT -----")
    print("The tool will create three files in \'OUTPUT_DIRECTORY\':")
    print("- \'public_keys.txt\' -> A list of all the public keys uploaded.")
    print("- \'secret_names.txt\' -> A list of all the secret names created.")
    print("- \'pubkey_to_names.txt\' -> A mapping of the public key to the created secret name.")
    print("\nFor a full description, see the README.md\n")
