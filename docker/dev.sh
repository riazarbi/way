#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Get current user's UID and GID
USER_ID=$(id -u)
GROUP_ID=$(id -g)
USERNAME=$(id -un)

# Check if Google Application Default Credentials exist
GOOGLE_CREDS_PATH="$HOME/.config/gcloud/application_default_credentials.json"
if [ -f "$GOOGLE_CREDS_PATH" ]; then
    echo "Found Google Application Default Credentials, will mount into container"
    GOOGLE_CREDS_MOUNT="-v $GOOGLE_CREDS_PATH:/home/$USERNAME/.config/gcloud/application_default_credentials.json:ro"
else
    echo "Warning: Google Application Default Credentials not found at $GOOGLE_CREDS_PATH"
    echo "Container will not have access to Google Cloud credentials"
    GOOGLE_CREDS_MOUNT=""
fi

# Build the Docker image with user information
echo "Building Docker image..."
podman build --format=docker \
    -t dev-environment \
    --build-arg USERNAME=$USERNAME \
    --build-arg USER_UID=$USER_ID \
    --build-arg USER_GID=$GROUP_ID \
    "$SCRIPT_DIR"

# Run the container interactively
echo "Starting development container..."
podman run -it --rm \
    -v "$(pwd):/workspace:rw" \
    $GOOGLE_CREDS_MOUNT \
    --network=host \
    --privileged \
    --user "$USER_ID:$GROUP_ID" \
    -e HOME=/workspace \
    -e USERNAME=$USERNAME \
    -e USER_UID=$USER_ID \
    -e USER_GID=$GROUP_ID \
    -e GOOGLE_APPLICATION_CREDENTIALS=/home/$USERNAME/.config/gcloud/application_default_credentials.json \
    --userns=keep-id \
    dev-environment 
    
