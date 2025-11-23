#!/bin/bash

# Ensure that the script exits if any commands fail
set -euo pipefail

# Get environment variables
env_vars=(
    GOOGLE_PROJECT_ID
    GOOGLE_REPOSITORY
    GOOGLE_SERVICE_NAME
    GOOGLE_REGION
    WORLD_GENERATOR_TOKEN
)
if [ -f .env ]; then
    source .env
fi
for var in "${env_vars[@]}"; do
    if [[ -z "${!var:-}" ]]; then
        echo "Error: $var is not set."
        exit 1
    fi
done

# Read arguments from command line
if [[ -z "${1:-}" ]]; then
    echo "Usage: $0 <local|docker|google-project-id> [<amd64|arm64>]"
    exit 1
fi
GOOGLE_PROJECT_ID=$1
ARCH=${2:-"amd64"}

# Parameters
# TODO: IMAGE_ID is not DRY! However, need to run script in isolation as well as via deploy.sh.
IMAGE_ID="${GOOGLE_REGION}-docker.pkg.dev/${GOOGLE_PROJECT_ID}/${GOOGLE_REPOSITORY}/${GOOGLE_SERVICE_NAME}:latest"
PLATFORM="linux/${ARCH}"

# Build the Docker image
# Note tokens needs to be exported for it to be available to the docker build command
export WORLD_GENERATOR_TOKEN
docker build \
    --tag "$IMAGE_ID" \
    --platform "$PLATFORM" \
    --secret id=WORLD_GENERATOR_TOKEN,env=WORLD_GENERATOR_TOKEN \
    .
