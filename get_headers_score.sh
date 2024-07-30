#!/bin/bash

# Function to print usage
print_usage() {
  echo "Usage: $0 <website_url>"
  echo "Example: $0 https://example.com"
}

# Check if URL is provided
if [ -z "$1" ]; then
  echo "Error: No URL provided."
  print_usage
  exit 1
fi

# Set the URL
URL=$1

# Set Headers Doctor API endpoint
API_DOMAIN="https://api.headers.doctor"
# API_DOMAIN="http://localhost:8000"
ROOT_URL="/results/scores"

# Make the API request
echo "Scanning $URL..."
RESPONSE=$(curl -s -X 'POST' \
  "$API_DOMAIN$ROOT_URL" \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "hostname": "'"$URL"'",
  "hidden": false,
  "port": 0,
  "redirects": false,
  "date": "'"$(date -u +"%Y-%m-%dT%H:%M:%S.%3NZ")"'"
  }'
)

# Check if the request was successful
if [ $? -ne 0 ]; then
  echo "Error: Failed to connect to Headers Doctor API."
  exit 1
fi

# Parse the response to get the header score
HEADER_SCORE=$(echo $RESPONSE | jq -r '.security_score')
DATE_SCAN=$(echo $RESPONSE | jq -r '.date')

# Check if jq parsing was successful
if [ $? -ne 0 ]; then
  echo "Error: Failed to parse the response."
  exit 1
fi

# Print the header score
echo "Header Score for $URL: $HEADER_SCORE"

# Provide a link to the public Headers Doctor results page
URL=$(echo $URL | sed 's|https://||')
echo "Check detailed results at: $API_DOMAIN/results/$URL/$DATE_SCAN?descriptions=true&security=true"
