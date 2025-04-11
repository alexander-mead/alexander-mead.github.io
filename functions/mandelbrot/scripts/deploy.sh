#!/bin/sh

# Exit on error
set -euo pipefail

# Parse command-line arguments
if [[ -z "${1:-}" ]]; then
    echo "Usage: $0 <local|cloud|guided> [<x86_64|arm64> <aws_profile>]"
    exit 1
fi
DEPLOYMENT=$1
ARCHITECTURE=${2:-"x86_64"}
AWS_PROFILE=${3:-"default"}

# Write info to screen
echo "Deployment: $DEPLOYMENT"
echo "Architecture: $ARCHITECTURE"
echo "AWS profile: $AWS_PROFILE"

# Build
sam validate --lint
sam build --profile personal --parameter-overrides Architecture=$ARCHITECTURE

# Deploy locally or to the cloud
if [ "$DEPLOYMENT" = "local" ]; then
    sam local start-api --profile $AWS_PROFILE --parameter-overrides Architecture=$ARCHITECTURE
elif [ "$DEPLOYMENT" = "cloud" ]; then
    sam deploy --profile $AWS_PROFILE --parameter-overrides Architecture=$ARCHITECTURE
elif [ "$DEPLOYMENT" = "guided" ]; then
    sam deploy --guided --profile $AWS_PROFILE --parameter-overrides Architecture=$ARCHITECTURE
else
    echo "Invalid deploy option: $DEPLOYMENT."
    exit 1
fi
exit 0