# Secure Validator Keystore to Secret Manager
This repo contains a tool and instructions to securely upload/create validator keys to [Google Cloud Secret Manager](https://cloud.google.com/secret-manager).

The tool needs to run in the same filesystem where the keys are stored (store the keys in a differnt directory than this repo). All communications with the [Google Cloud Secret Manager API](https://cloud.google.com/secret-manager/docs/reference/rest) are authenticated using [Application Default Credentials](https://cloud.google.com/docs/authentication/application-default-credentials).

As an extra layer of safety, it is recommended to either:
- Generate the keys within the Google Cloud environment (such as a [Compute Engine](https://cloud.google.com/compute) VM) without public internet connectivity (no public IP address), ensuring API traffic is private.
- Securely upload the keys to an air-gapped machine on Google Cloud using [Google Cloud VPN](https://cloud.google.com/network-connectivity/docs/vpn/concepts/overview), then create the secrets.
- Setup another form of [private connectivity](https://cloud.google.com/vpc/docs/private-access-options) between your environment and Google Cloud when running this tool.

**Note:**
The tool doesn't _literally upload_ the keystores. Rather, it reads the keystrore contents and creates secret manager entries with the same encoding. The word _"upload"_ is used through this `README` interchangably with secret creation.

# Requiremnnts
## Local Environment Setup
1. Clone the repo
```
git clone https://github.com/theSamPadilla/bls-to-execution-batch-update
```
2. [Download Python]((https://www.python.org/downloads/))
3. [Download pip](https://pip.pypa.io/en/stable/installation/)
4. Install requirements:
```
pip install -r requirements.txt
```

## Google Cloud Setup
1. [Download the Google Cloud CLI (gcloud)](https://cloud.google.com/sdk/docs/install)
This will be necessary to create your local credentials.

2. Enable the Secret Manager API on the Google Cloud Console for the project where you want to upload the keys
   - Open your Google Cloud Console
   - [Make sure billing is enabled](https://cloud.google.com/billing/docs/how-to/verify-billing-enabled#console)
   - Search for `Secret Manager` on the search bar
   - Enable the API.

    [More instructions here](https://cloud.google.com/secret-manager/docs/configuring-secret-manager).

# Credentials
To limit the scope of actions that can be performed on your Google Cloud environment, we will use a [Google Cloud Service Account](https://cloud.google.com/iam/docs/service-account-overview) with a limited scope to Google Cloud Secret Manager. To be even more secure, we will use short lived [Application Default Credentials (ADC)](https://cloud.google.com/docs/authentication/application-default-credentials) [impersonating a service account](https://cloud.google.com/iam/docs/service-account-overview#impersonation) to authenticate the API calls.

Below are the instructions to do each of these. You can skip the process of generating a service account and use your principal credentials directly. This is not recommended as it increases the privileges of the credentials you generate.

To generate an ADC file from your principal, you can run:
```
gcloud auth application-default login
```

## Create a Service Account
### Required Roles:
You will need two roles for this operation:
1. [`roles/iam.serviceAccountCreator`](https://cloud.google.com/iam/docs/service-accounts-create#permissions): Needed to create the service account
2. [`roles/iam.serviceAccountTokenCreator`](https://cloud.google.com/iam/docs/service-account-permissions#token-creator-role): Needed to impersonate the service account and generate credentials.
Ensure you have these permissions before beginning this process or ask your system administrator to grant you that role.

### Create a Service Account
To [create a service account]((https://cloud.google.com/iam/docs/service-accounts-create#creating)):
   - Navigate to the IAM page on your Google Cloud console
   - Enter a service account name to display in the Google Cloud console. The Google Cloud console generates a service account ID based on this name. Edit the ID if you want to. You cannot change the ID later.
   - _Optional_: Enter a description of the service account. Click Done to finish creating the service account. We will set permissions to the service account in the next step.
   - _Optional_: If you want to limit the scope of who can impersonate the Service account users role field, you can add members authorized to impersonate the service account.

You can also create a service account using gcloud:
```
gcloud iam service-accounts create <service-account-name> \
    --description="<description>" \
    --display-name="<display_name>"
```

### Grant the appropriate permission to the service account.
The tool, by default, performs three operations:
- **Secret creation:** It creates the secret.
- **Version modification:** It populates the secret with contetns by making a new version.
- **Version accessing:** It accesses the contents of the secret to verify data integrity compared to the local keystore.

Each ot the three operation require the following [Secret Manager IAM permissions](https://cloud.google.com/secret-manager/docs/access-control#assign-iam-roles):
- **Secret creation:** `secretmanager.secrets.create`
- **Version modification:** `secretmanager.versions.add`
- **Version accessing:** `secretmanager.versions.access`

The last operation and its related permission can be optionally removed by passing the flag `optimistic` when executing the tool.

To grant these permissions, you have two options:
1. [Create a custom role](https://cloud.google.com/iam/docs/creating-custom-roles) with only those permissions (recommended).
2. Use the default role of `roles/secretmanager.admin` that grants all the permissions needed.

Choose the role you want to grant, then [follow the instructions here](https://cloud.google.com/marketplace/docs/grant-service-account-access) to grant the service account those permissions.

**Note:**
It is recommended to refresh on the [principle of least privilege](https://cloud.google.com/iam/docs/using-iam-securely#least_privilege) when choosing the scope of permissions to grant to your service account.

## Create Application Default Credentials
Application default credentials are one of the best and most secure ways to authenticate your API calls.
It works through environment variables and the public Google Cloud libraries automatically search for the credentials in your execution environment.

In the case of this tool, we will create an ADC file impersonating our service account and set the [GOOGLE_APPLICATION_CREDENTIALS](https://cloud.google.com/docs/authentication/application-default-credentials#GAC) environment variable using our `.env` file.
[Service account impersonation](https://cloud.google.com/docs/authentication/use-service-account-impersonation) allows you to request short-lived credentials for a service account that has either the authorization that your use case requires, or, as in our case, a scope more limited than the user.

First, [initialize `gcloud`](https://cloud.google.com/sdk/gcloud/reference/init):
```
gcloud init
```

Follow the prompts to complete the authentication process. Make sure to log-in with your own email and connect to the appropriate project where the keys will be stored.

Then creat the ADC file by running:
```
gcloud auth application-default login --impersonate-service-account <service-account-email>
```

Make sure to replace `<service-account-email>` with the email of the service account created previously.

Follow the prompts to complete the authentication process.
The command will create a `application_default_credentials.json` in the default location of `/home/<user>/.config/gcloud/`.
You can leave the credential file there or move it your directory of choice. Just make a note of where the file is located as it will need to be passed to the `.env` file

# Configuring the Environment
Make a copy the `sample.env`:
```
cd secure-validator-keystore-to-secret-manager
cp sample.env .env
```

Then, in `.env`, replace:
- `PROJECT_ID` with your Google Cloud Project ID
- `KEY_DIRECTORY_PATH` with the path to the directory containing your validator keystores.
    Note that every `.json` file in this directory will be uploaded to Secret Manager. Make sure to only have the keys you want to upload in this directory.
- `GOOGLE_APPLICATION_CREDENTIALS` with the path to the ADC file created preciously=.
- `OUTPUT_DIRECTORY` with the path to the directory where you want the output files to be written.

# Running the tool
### Parameters
The tool takes two optional parameters:
- `optimistic`
When this flag is passed, it makes the tool not check the validator keystore cheksum with the checksum of the created secret.
Set this flag if you choose not to give your service account secret access permissions (`secretmanager.versions.access`).
The tool will verify the checksums if the file is not set.

- `help` or `--help` or `h`
Prints a CLI help message.

### Output file overwrite Confirmation
Before running, the tool will check for the following files in `OUTPUT_DIRECTORY`:
- `public_keys.txt`
- `secret_names.txt`
- `pubkey_to_names.txt`

If it finds any of these files, it will prompt you for a manual `yes` confirmation that you want to overwrite them.

### Output
The tool outputs the aforementioned three files in you `OUTPUT_DIRECTORY`.
- `public_keys.txt` - A list of all the public keys uploaded.
- `secret_names.txt` - A list of all the secret names created.
- `pubkey_to_names.txt` - A mapping of the public key to the created secret name.

### Running
To run the tool:
```
python main.py
```

# Contributing
This repo is accepting contributions, issues, and feedback.
To contribute, fork the repo, make the changes, then make a PR against `main`.

#### Possible Extensions:
- Automate key generation.
- Enable upload via `gcloud`.
- Enable batch deletion of secrets on Secret Manager.

# Disclaimer & License
Although Google is the employer of the author of the repo, this is not an officially supported Google product and does not reflect on Google in any ways.

Neither the author of this repo nor its employer shall be held liable for any issues caused by the usage of this code. This includes but is not limited to bugs, errors, wrong or outdated inforamtion, or even loss of funds.

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