#!/bin/sh

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
# sed -e "s/{ { TWINLAB_SERVER } }/${TWINLAB_SERVER}/g" \ # Does not work, because slashes in environment variables ?!?
sed -e "s/{ { TWINLAB_GROUPNAME } }/${TWINLAB_GROUPNAME}/g" \
    -e "s/{ { TWINLAB_USERNAME } }/${TWINLAB_USERNAME}/g" \
    -e "s/{ { TWINLAB_TOKEN } }/${TWINLAB_TOKEN}/g" \
    template.base.yaml > template.yaml

# Build
sam build

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