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
    echo "Usage: $0 <local|docker|cloud> [<amd64|arm64>]"
    exit 1
fi
DEPLOYMENT=$1
ARCH=${2:-"amd64"}

# Check deployment
allowed_deployments=("local" "docker" "cloud")
if [[ ! " ${allowed_deployments[*]} " =~ $DEPLOYMENT ]]; then
    echo "Error: Invalid deployment type. Allowed values are: ${allowed_deployments[*]}"
    exit 1
fi

# Parameters
IMAGE_ID="$GOOGLE_REGION-docker.pkg.dev/$GOOGLE_PROJECT_ID/$GOOGLE_REPOSITORY/$GOOGLE_SERVICE_NAME:latest"
INTERNAL_PORT=8080 # NOTE: This must be identical to the port in the Dockerfile
EXPOSED_PORT=8000
MEMORY="512Mi"
CPU="1"
MAX_INSTANCES=5
TIMEOUT="30s"

# Build the Docker image if required
if [[ "$DEPLOYMENT" = "docker" || "$DEPLOYMENT" = "cloud" ]]; then
    if [ -f .env ]; then
        source .env # Source the environment variables if .env exists
    fi
    if [[ -z "${WORLD_GENERATOR_TOKEN:-}" ]]; then
        echo "Error: WORLD_GENERATOR_TOKEN is not set in the .env file."
        exit 1
    fi
    ./scripts/build.sh "$ARCH"
fi

# Run the application based on the deployment type
if [ "$DEPLOYMENT" = "local" ]; then
    uv run fastapi dev main.py
elif [ "$DEPLOYMENT" = "docker" ]; then
    # Run the Docker container
    # Replacing -p with --expose does not seem to work?!
    docker run -p $EXPOSED_PORT:$INTERNAL_PORT "$IMAGE_ID"
elif [ "$DEPLOYMENT" = "cloud" ]; then
    docker push "$IMAGE_ID"
    gcloud run deploy "$GOOGLE_SERVICE_NAME" \
        --region="$GOOGLE_REGION" \
        --image="$IMAGE_ID" \
        --project="$GOOGLE_PROJECT_ID" \
        --memory=$MEMORY \
        --cpu=$CPU \
        --max-instances=$MAX_INSTANCES \
        --timeout=$TIMEOUT \
        --allow-unauthenticated
else
    echo "Error: Unknown deployment type."
    exit 1
fi
