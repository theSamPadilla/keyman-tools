# BLS Keys to Secret Manager Secure Upload
This repo contains a tool and instructions to securely upload/create validator keys to [Google Cloud Secret Manager](https://cloud.google.com/secret-manager).

The tool needs to run in the same filesystem where the keys are stored. All communications with the [Google Cloud Secret Manager API](https://cloud.google.com/secret-manager/docs/reference/rest) are authenticated using [Application Default Credentials](https://cloud.google.com/docs/authentication/application-default-credentials).

As an extra layer of safety, it is recommended to either:
- Generate the keys within the Google Cloud environment (such as a [Compute Engine](https://cloud.google.com/compute) VM)
- Securely upload the keys to an air-gapped machine on Google Cloud using [Google Cloud VPN](https://cloud.google.com/network-connectivity/docs/vpn/concepts/overview), then create the secrets.
- Setup another form of [private connectivity between your environment and Google Cloud](https://cloud.google.com/network-connectivity/docs/vpn/concepts/overview) when running this tool.

**Note:**
The tool doesn't literally _upload_ the keystores. Rather, it reads the keystrore contents and creates secret manager entries with the same encoding. The word _"upload"_ is used through this `README` interchangably with secret creation.

# Requiremnnts
### 1. Local Environment Setup
1. Clone the repo
```
git clone https://github.com/theSamPadilla/bls-to-execution-batch-update
```
2. [Download Python]((https://www.python.org/downloads/))
3. Install requirements:
```
pip install -r requirements.txt
```

### 2. Google Cloud Setup
1. [Download the Google Cloud CLI (gcloud)](https://cloud.google.com/sdk/docs/install)
This will be necessary to create your local credentials.

2. Enable the Secret Manager API on the Google Cloud Console for the project where you want to upload the keys
   - Open your Google Cloud Console
   - [Make sure billing is enabled](https://cloud.google.com/billing/docs/how-to/verify-billing-enabled#console)
   - Search for `Secret Manager` on the search bar
   - Enable the API.

[More instructions here](https://cloud.google.com/secret-manager/docs/configuring-secret-manager).

# Credentials
To limit the scope of actions that can be performed on your Google Cloud environment, we will use a [Google Cloud Service Account](https://cloud.google.com/iam/docs/service-account-overview) with a limited scope to Google Cloud Secret Manager.

To be even more secure, we will use short lived [Application Default Credentials](https://cloud.google.com/docs/authentication/application-default-credentials) [impersonating a service account](https://cloud.google.com/iam/docs/service-account-overview#impersonation) to authenticate the API calls.

Below are the instructions to do each of these.

#### Create a Service Account
1. Required Roles:
You need two required roles for this operation:
   - [`roles/iam.serviceAccountCreator`](https://cloud.google.com/iam/docs/service-accounts-create#permissions): Needed to create the service account
   - [`roles/iam.serviceAccountTokenCreator`](https://cloud.google.com/iam/docs/service-account-permissions#token-creator-role): Needed to impersonate the service account and generate credentials.
Ensure you have these permissions before beginning this process or ask your system administrator to grant you that role.

1. [Create a Service Account](https://cloud.google.com/iam/docs/service-accounts-create#creating)
   - Navigate the IAM page on your Google Cloud console
   - Enter a service account name to display in the Google Cloud console. The Google Cloud console generates a service account ID based on this name. Edit the ID if you want to. You cannot change the ID later.
   - _Optional_: Enter a description of the service account. Click Done to finish creating the service account. We will set permissions to the service account in the next step.
   - _Optional_: If you want to limit the scope of who can impersonate the Service account users role field, you can add members authorized to impersonate the service account.

You can also create a service account using gcloud:
```
gcloud iam service-accounts create <service-account-name> \
    --description="<description>" \
    --display-name="<display_name>"
```

1. [Grant the appropriate permission to the service account](https://cloud.google.com/marketplace/docs/grant-service-account-access).
The tool, by default, perform three operations:
- Secret creation: It creates the secret.
- Version modification: It populates the secret with contetns by making a new version.
- Version checking: It checks the contents of the secret to verify data integrity compared to the local keystore.

Each ot the three operation require the following IAM permissions:
- Secret creation: `secretmanager.secrets.create`
- Version modification: `secretmanager.versions.add`
- Version checking: `secretmanager.versions.access`

The last operation and its related permission can be optionally removed by passing the flag `optimistic` to the tool.

To grant these permissions, you have two options:
1. You can [create a custom role](https://cloud.google.com/iam/docs/creating-custom-roles) with only those permissions. [recommended]
2. You can use the default role of `roles/secretmanager.admin` that grants all the permissions listed above.

Choose the role you want to grant, and [follow the instructions here](https://cloud.google.com/marketplace/docs/grant-service-account-access) to grant the service account those permissions.

**Note:** May be good to refresh on the [principle of least privilege](https://cloud.google.com/iam/docs/using-iam-securely#least_privilege) when choosing the scope of permissions to grant to your service accoun.

#### Create a Application Default Credentials

# Configuring the Environment

# Running the tool

# Contributing

# Disclaimer & License
Although Google is the employer of the author of the repo, this is not an officially supported Google product and does not reflect on Google in any ways.

Neither the author of this repo nor its employer shall be held liable for any issues caused by the usage of this code. This includes but is not limited to bugs, errors, wrong or outdated inforamtion, or even lost of funds.

This repo is published solely on the basis of good faith and as a tool to help developers. This code should be used with caution. The user is running this code at its own risk.

Apache Header:

```
Copyright 2023 Sam Padilla

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```