#!/bin/bash
# Check if required parameters are provided
if [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ]; then
  echo -e "\n\n[ERROR] "${0##*/}": Not all required parameters are set."
  echo -e "\tUsage: <migrations_path> <container_id> <db_user> "
  exit 1
fi

# Unpack parameters
migrations_path="$1"
container_id="$2"
db_user="$3"

db_name="slashing-protection" # Do not change this. It is hardcoded in run-db.sh

# Loop through migration files in increasing order
for sql_file in $(ls "$migrations_path"/V*.sql | sort); do

    # Extract the file name
    file_name=$(basename "$sql_file")

    # Construct the psql command
    psql_command="psql --echo-all --host=localhost --port=5432 --dbname=$db_name --username=$db_user -f /migrations/$file_name"

    # Print command running
    echo -e "\tApplying command $psql_command\n"
    echo -e "\tFrom file $file_name\n"
    echo -e "\n\nResult:\n"

    # Run the command
    docker exec $container_id $psql_command
done
