"""Deletes all the secrets matching the provided pattern"""
import os

import secret_manager.utilities as util

from cli.pretty.colors import green, end

def delete_secrets(client: util.secretmanager.SecretManagerServiceClient, secrets: list, project_id: str):
    """
    Deletes all the provided secrets.
    
    Args:
        client: the Secret Manager clietn
        secrets: the list of secrets names to be deleted.
        project_id: Google Cloud project id where to look for secrets.
    
    Returns: The number of secrets deleted
    """

    print ("\n[INFO] Deleting secrets...")
    i = 1

    for secret in secrets:

        print(f"\t[-] Deleting secret name: {secret} - {i}/{len(secrets)}")

        # Set secret name
        name = f"projects/{project_id}/secrets/{secret}"

        # Delete
        client.delete_secret(request={"name": name})

        i += 1

    return i-1
