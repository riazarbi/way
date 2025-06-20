#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Get current user's UID and GID
USER_ID=$(id -u)
GROUP_ID=$(id -g)
USERNAME=$(id -un)

# Build the Docker image with user information
echo "Building Docker image..."
podman build -t dev-environment \
    --build-arg USERNAME=$USERNAME \
    --build-arg USER_UID=$USER_ID \
    --build-arg USER_GID=$GROUP_ID \
    "$SCRIPT_DIR"

# Run the container interactively
echo "Starting development container..."
podman run -it --rm \
    -v "$(pwd):/workspace:rw" \
    --user "$USER_ID:$GROUP_ID" \
    -p 5000:5000 \
    -e HOME=/workspace \
    -e USERNAME=$USERNAME \
    -e USER_UID=$USER_ID \
    -e USER_GID=$GROUP_ID \
    --userns=keep-id \
    dev-environment 