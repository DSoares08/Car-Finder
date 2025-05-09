#!/bin/bash

# Make the script executable
chmod +x "$(dirname "$0")/start_server.sh"

# Navigate to the server directory
cd "$(dirname "$0")/server"

# Start the server
python3 server.py

# If you want to specify a custom port, uncomment the line below
# python3 server.py 8080
