#!/bin/bash
echo "Running web3signer..."

# Web3 Signer
nohup web3signer --key-config-path=<key-config-path-generated-by-this-tool> \
	--data-path=<web3-signer-path> \
	--http-listen-port=<port> \
	--metrics-enabled \
	--http-host-allowlist=* \
	eth2 \
	--network=<network> \
	--slashing-protection-db-url="jdbc:postgresql://localhost/web3signer" \
	--slashing-protection-db-username=<username> \
	--slashing-protection-db-password=<password> >> <path-to-log.log 2>&1 &