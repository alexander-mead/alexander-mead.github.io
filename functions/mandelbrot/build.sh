#!/bin/sh

# Exit on error
set -e

# Parse command-line arguments
if [ "$#" -ne 1 ]; then
    echo "Usage: build.sh <local|cloud|guided>"
    exit 1
fi

# Build
sam build

# Deploy locally or to the cloud
if [ "$1" = "local" ]; then
    sam local start-api
elif [ "$1" = "cloud" ]; then
    sam deploy --config-env personal
elif [ "$1" = "guided" ]; then
    sam deploy --guided --profile personal
else
    echo "Invalid build option: $1."
    exit 1
fi
exit 0