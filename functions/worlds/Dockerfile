# Base image
# Previously was using python:3.13-slim
FROM python:3.13-slim

# Install git (required by uv to fetch some dependencies)
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Set the working directory
# NOTE: Setting this is considered to be best practice
# NOTE: Although seems to work fine without it...
WORKDIR /var/task

# Install uv
RUN pip install uv

# Copy only pyproject.toml and uv.lock
# Done at the top of the Dockerfile to cache dependencies
COPY pyproject.toml .python-version uv.lock ./

# Debug build step
RUN --mount=type=secret,id=WORLD_GENERATOR_TOKEN bash -euxc '
  echo "Secrets mounted at:" && ls -l /run/secrets
  echo "Token preview:" && head -c 8 /run/secrets/WORLD_GENERATOR_TOKEN && echo "..."
  TOKEN=$(cat /run/secrets/WORLD_GENERATOR_TOKEN)
  echo "Configuring git..."
  git config --global url."https://${TOKEN}:x-oauth-basic@github.com/".insteadOf "https://github.com/"
  echo "Git version:" && git --version
  echo "Running uv sync..."
  uv sync --no-dev
'

# This should be done towards the end of the Dockerfile
# It is done before poetry install because folder needs to exist for --package-mode=true
# It is possible that this should be moved to the bottom of the Dockerfile
COPY main.py ./

# What is actually run (entrypoint)
# This is the command run to start the application
# My attempts to pass environment variables to uvicorn via CMD have not worked
# The (internal) port here must be the same as that in the deployment configuration
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]