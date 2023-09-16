#!/bin/bash
####################
# Install Java SDK #
####################
# Source .bashrc first then check if Java is installed
source "$HOME"/.bashrc
if command -v java &> /dev/null; then
    echo -e "[INFO] Java is already installed. It has been written to the PATH on "$HOME"/.bashrc.\n"
    exit 0
fi

# Set version
export jdk_version="jdk-20"

# Get the zip
echo -e "[INFO] Installing the Java SDK as a dependency of web3signer.\n"
wget https://download.oracle.com/java/20/latest/"$jdk_version"_linux-x64_bin.tar.gz

# Get and publish the sha256
sha=$(wget -qO- https://download.oracle.com/java/20/latest/jdk-20_linux-x64_bin.tar.gz.sha256)
echo -e "\n[INFO] Verifying SHA256 for Java SDK: $sha."

# Verify the downloaded file using sha256sum
if echo "$sha jdk-20_linux-x64_bin.tar.gz" | sha256sum --check --status -; then
  echo -e "\t[✓] SHA256 checksum verification succeeded."
else
  echo -e "\tSHA256 checksum verification failed. Aborting installation."
  exit 1
fi

# Untar, remove build, and move to home
echo -e "\n[INFO] Unpacking and moving Java SDK to home directory."
tar -xf "$jdk_version"_linux-x64_bin.tar.gz
rm "$jdk_version"_linux-x64_bin.tar.gz
mv "$jdk_version"* "$HOME"/$jdk_version
echo -e "\t[✓] Done."

# Add Java SDK bin to path (append to PATH)
echo -e "\n[INFO] Adding Java SDK bin to PATH."
echo "export PATH=\$PATH:$HOME/$jdk_version/bin" >> "$HOME"/.bashrc
source "$HOME"/.bashrc  # Update the PATH for the current session
echo -e "\t[✓] Done."

# Done
echo -e "\n\nSuccesfully installed the Java SDK."
echo -e "------------------------\n"