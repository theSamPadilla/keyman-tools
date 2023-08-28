# Requirements
1. Enable the Secret Manager API, once per project.
2. Assign the Secret Manager Admin role (roles/secretmanager.admin) on the project, folder, or organization.
3. Install the Google Cloud CLI
4. Authenticate to the Secret Manager API using one of the following ways:
    - If you use client libraries to access the Secret Manager API, set up Application Default Credentials.
    - If you use the Google Cloud CLI to access the Secret Manager API, use your Google Cloud CLI credentials to authenticate.
    - To authenticate a REST call, use either Google Cloud CLI credentials or Application Default Credentials.

5. Setup an service account impersonation ACD:
You must give yourself `iam.serviceAccounts.getAccessToken` permissions
https://cloud.google.com/docs/authentication/use-service-account-impersonation