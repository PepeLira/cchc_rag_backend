#!/bin/bash

# Wait for PostgreSQL to be ready
until pg_isready -h postgres -p 5432; do
  echo "Waiting for PostgreSQL..."
  sleep 2
done

# Create the server configuration JSON file
cat <<EOF > /pgadmin4/servers.json
{
  "Servers": {
    "1": {
      "Name": "PostgreSQL",
      "Group": "Servers",
      "Host": "postgres",
      "Port": 5432,
      "MaintenanceDB": "postgres",
      "Username": "${PGADMIN_DEFAULT_EMAIL}",
      "Password": "${PGADMIN_DEFAULT_PASSWORD}",
      "SSLMode": "prefer"
    }
  }
}
EOF

# Start pgAdmin
/entrypoint.sh