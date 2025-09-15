#!/bin/bash
# Get authentication token for dr_smith user
# This script demonstrates the correct username format for API calls

TOKEN=$(curl -s -X POST "http://localhost:8001/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=dr_smith&password=secure_password" | \
  python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

echo "Got auth token: ${TOKEN:0:20}..."

# Export the token for use in other scripts
export AUTH_TOKEN="$TOKEN"
echo "Token exported as AUTH_TOKEN environment variable"
echo "You can now use it in other curl commands like:"
echo "curl -H \"Authorization: Bearer \$AUTH_TOKEN\" http://localhost:8002/api/v1/patients/"