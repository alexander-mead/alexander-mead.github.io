#!/bin/bash

# Exit on error
set -euo pipefail

# Parse command-line arguments
if [[ -z "${1:-}" ]]; then
    echo "Usage: $0 <local|cloud|guided> [<x86_64|arm64> <aws_profile>]"
    exit 1
fi
DEPLOYMENT=$1
ARCHITECTURE=${2:-"arm64"}
AWS_PROFILE=${3:-"default"}

# Write info to screen
echo "Deployment: $DEPLOYMENT"
echo "Architecture: $ARCHITECTURE"
echo "AWS profile: $AWS_PROFILE"

# Load environment variables from .env file
if [ ! -f .env ]; then
    echo "Error: .env file not found. Please create one from the .env.example file."
    exit 1
fi

# Detect OS and load environment variables accordingly
unamestr=$(uname)
if [ "$unamestr" = "Linux" ]; then
    export "$(grep -v '^#' .env | xargs -d '\n')"
elif [ "$unamestr" = "FreeBSD" ] || [ "$unamestr" = "Darwin" ]; then
    export "$(grep -v '^#' .env | xargs -0)"
else
    echo "Unsupported OS: $unamestr."
    exit 1
fi

# Build
sam validate --lint
sam build --profile personal --parameter-overrides Architecture="$ARCHITECTURE"

# Deploy locally or to the cloud
if [ "$DEPLOYMENT" = "local" ]; then
    sam local start-api --profile personal --parameter-overrides Architecture="$ARCHITECTURE"
elif [ "$DEPLOYMENT" = "cloud" ]; then
    sam deploy --profile personal --parameter-overrides Architecture="$ARCHITECTURE"
elif [ "$DEPLOYMENT" = "guided" ]; then
    sam deploy --guided --profile personal --parameter-overrides Architecture="$ARCHITECTURE"
else
    echo "Invalid build option: $DEPLOYMENT."
    exit 1
fi
exit 0
