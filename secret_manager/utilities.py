"""Utilities for the secret-manager command"""
from google.cloud import secretmanager

def create_sm_client() -> secretmanager.SecretManagerServiceClient:
    """Creates and returns a Google Cloud Secret Manager Client with ADC"""
    return secretmanager.SecretManagerServiceClient()