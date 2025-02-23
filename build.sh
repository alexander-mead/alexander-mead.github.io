#!/bin/sh

# Exit on error
set -e

if [ "$#" -ne 1 ]; then
    echo "Usage: build.sh <local|cloud|guided>"
    exit 1
fi

# Load environment variables from .env file
if [ ! -f .env ]; then
  echo "Error: .env file not found. Please create one from the .env.example file."
  exit 1
fi

# Detect OS and load environment variables accordingly
unamestr=$(uname)
if [ "$unamestr" = "Linux" ]; then
  export $(grep -v '^#' .env | xargs -d '\n')
elif [ "$unamestr" = "FreeBSD" ] || [ "$unamestr" = "Darwin" ]; then
  export $(grep -v '^#' .env | xargs -0)
fi

# Inject secrets
_TWINLAB_URL=$(printf '%s\n' "$TWINLAB_URL" | sed -e 's/[\/&]/\\&/g') # Escape slashes and ampersands
sed -e "s/{ { TWINLAB_URL } }/${_TWINLAB_URL}/g" \
    -e "s/{ { TWINLAB_USER } }/${TWINLAB_USER}/g" \
    -e "s/{ { TWINLAB_API_KEY } }/${TWINLAB_API_KEY}/g" \
    template.base.yaml > template.yaml

# Build
# sam build
sam build --no-cached --cache-dir .

# Remove the template file, which contains secrets
rm template.yaml

# Deploy locally or to the cloud
if [ "$1" = "local" ]; then
    sam local start-api
elif [ "$1" = "cloud" ]; then
    sam deploy
elif [ "$1" = "guided" ]; then
    sam deploy --guided
else
    echo "Invalid build option: $1."
    exit 1
fi
exit 0