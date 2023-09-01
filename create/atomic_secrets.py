"""Puts all the keys into as few secrets as possible."""

import os
import json
from google.cloud import secretmanager
import create.utilities as util

def create_atomic_secrets(project_id: str, key_directory_path: str, output_dir: str):
    """Creates secrets using the python library through the API.
    
    Args:
        project_id: Google cloud project ID where the secrets will live
        key_directory_path: Path to keystore files
        output_dir: Output path for txt files for local records
    """
    print("You are in the atomic secret creation. WIP")
