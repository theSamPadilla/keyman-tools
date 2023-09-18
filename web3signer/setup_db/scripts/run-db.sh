#!/bin/bash
# Check if required parameters are provided
if [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ]; then
  echo -e "\n\n[ERROR] "${0##*/}": Not all required parameters are set."
  echo -e "\tUsage: <migrations_path> <db_user> <db_passwd>"
  exit 1
fi

# Unpack parameters
migrations_path="$1"
db_user="$2"
db_passwd="$3"

# Docker command
# Do not change the container name as it is hardcoded in the tool.
docker run --name slashing-protection-db \
	-d \
	-v $migrations_path:/migrations \
	-p 5432:5432 \
	-e POSTGRES_PASSWORD=$db_passwd \
	-e POSTGRES_USER=$db_user \
	-e POSTGRES_DB=slashing-protection \
	postgres