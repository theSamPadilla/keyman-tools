#!/bin/bash
####################
# Install Web3signer #
####################
# Source .bashrc first then check if web3signer is installed
source "$HOME"/.bashrc
if command -v web3signer &> /dev/null; then
    echo -e "\n\n[INFO] Web3signer is already installed. It has been written to the PATH on "$HOME"/.bashrc.\n"
    exit 0
fi

# Set version
export w3s_version=web3signer-23.9.1-RC1

# Get the zip
echo -e "\n\n[INFO] Installing $w3s_version \n"
wget https://artifacts.consensys.net/public/web3signer/raw/names/web3signer.tar.gz/versions/latest/"$w3s_version".tar.gz

# Set latest version as of 23.9.1-RC1 and publish the sha256
#? See latest at https://cloudsmith.io/~consensys/repos/web3signer/packages/detail/raw/web3signer.tar.gz/23.9.1-RC1/
sha='ef3e92e933e95e88658f9b7d39d8b565b8b4c86adcf5e69d8abfbd7c1ab79c49'
echo -e "\n[INFO] Verifying SHA256 for web3signer: $sha."
echo -e "[INFO] SHA256 hard-coded on installation script at latest=$w3s_version."

# Verify the downloaded file using sha256sum
if echo "$sha "$w3s_version".tar.gz" | sha256sum --check --status -; then
  echo -e "\t[✓] SHA256 checksum verification succeeded."
else
  echo -e "\tSHA256 checksum verification failed. Aborting installation."
  echo -e "\tCheck hard-coded SHA256 on the installation script."
  exit 1
fi

# Untar, remove build, and move to home
echo -e "\n[INFO] Unpacking and moving web3signer to home directory."
tar -xf "$w3s_version".tar.gz
rm "$w3s_version".tar.gz
mv "$w3s_version"* "$HOME"/$w3s_version
echo -e "\t[✓] Done."

# Add web3signer bin to path (append to PATH)
echo -e "\n[INFO] Adding web3signer bin to PATH."
echo "export PATH=\$PATH:$HOME/$w3s_version/bin" >> "$HOME"/.bashrc
source "$HOME"/.bashrc  # Update the PATH for the current session
echo -e "\t[✓] Done."

# Done
echo -e "\n\nSuccesfully installed web3signer."
echo -e "------------------------\n"