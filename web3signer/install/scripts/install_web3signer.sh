#!/bin/bash
####################
# Install Web3signer #
####################
# Source .bashrc first then check if web3signer is installed
source "$HOME"/.bashrc
if command -v web3signer &> /dev/null; then
    echo -e "[INFO] Web3signer is already installed. It has been written to the PATH on "$HOME"/.bashrc.\n"
    exit 0
fi

# Set version
export w3s_version=web3signer-23.9.0

# Get the zip
echo -e "[INFO] Installing $w3s_version \n"
wget https://artifacts.consensys.net/public/web3signer/raw/names/web3signer.tar.gz/versions/latest/"$w3s_version".tar.gz

# Set latest version as of 23.9.0 and publish the sha256
sha='7af5cd0589f6105f2267b6c9e6eedda077d597e6410975e1687a6a20e7f1518c'
echo -e "\n[INFO] Verifying SHA256 for web3signer: $sha."
echo -e "[INFO] SHA256 hard-coded on installation script at latest=23.9.0."

# Verify the downloaded file using sha256sum
if echo "$sha web3signer-23.9.0.tar.gz" | sha256sum --check --status -; then
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