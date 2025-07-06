#!/bin/bash

set -e

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Get the .way directory path (parent of docker directory)
WAY_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"

# Get current user's UID and GID
USER_ID=$(id -u)
GROUP_ID=$(id -g)
USERNAME=$(id -un)

# Get git configuration from host
GIT_USER_NAME=$(git config user.name 2>/dev/null || echo "$USERNAME")
GIT_USER_EMAIL=$(git config user.email 2>/dev/null || echo "$USERNAME@example.com")

echo "Using git configuration:"
echo "  Name: $GIT_USER_NAME"
echo "  Email: $GIT_USER_EMAIL"

# Safety check: prevent running from home directory or projects directory
CURRENT_DIR="$(pwd)"
HOME_DIR="$HOME"
PROJECTS_DIR="$HOME/projects"

if [ "$CURRENT_DIR" = "$HOME_DIR" ]; then
    echo "Error: Cannot run dev.sh from home directory ($HOME_DIR)"
    echo "Please navigate to a specific project directory first."
    exit 1
fi

if [ "$CURRENT_DIR" = "$PROJECTS_DIR" ]; then
    echo "Error: Cannot run dev.sh from projects directory ($PROJECTS_DIR)"
    echo "Please navigate to a specific project directory first."
    exit 1
fi

# Additional check: prevent running from any parent of .way directory
if [[ "$CURRENT_DIR" == "$WAY_DIR"* ]] && [ "$CURRENT_DIR" != "$WAY_DIR" ]; then
    echo "Error: Cannot run dev.sh from a parent directory of .way"
    echo "Current directory: $CURRENT_DIR"
    echo ".way directory: $WAY_DIR"
    echo "Please navigate to a specific project directory first."
    exit 1
fi

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

# Get the current directory name for mounting
CURRENT_DIR=$(basename "$(pwd)")
WORKSPACE_PATH="/workspace/$CURRENT_DIR"

# Check if .gemini folder exists in projects directory
GEMINI_PATH="$HOME/projects/.gemini"
if [ -d "$GEMINI_PATH" ]; then
    echo "Found .gemini folder, will mount into container"
    GEMINI_MOUNT="-v $GEMINI_PATH:/workspace/.gemini:rw"
else
    echo "Warning: .gemini folder not found at $GEMINI_PATH"
    echo "Container will not have access to .gemini configuration"
    GEMINI_MOUNT=""
fi

# Check if .claude.json file exists in projects directory
CLAUDE_JSON_PATH="$HOME/projects/.claude.json"
if [ -f "$CLAUDE_JSON_PATH" ]; then
    echo "Found .claude.json file, will mount into container"
    CLAUDE_JSON_MOUNT="-v $CLAUDE_JSON_PATH:/workspace/.claude.json:rw"
else
    echo "Warning: .claude.json file not found at $CLAUDE_JSON_PATH"
    CLAUDE_JSON_MOUNT=""
fi

# Check if .claude folder exists in projects directory
CLAUDE_FOLDER_PATH="$HOME/projects/.claude"
if [ -d "$CLAUDE_FOLDER_PATH" ]; then
    echo "Found .claude folder, will mount into container"
    CLAUDE_FOLDER_MOUNT="-v $CLAUDE_FOLDER_PATH:/workspace/.claude:rw"
else
    echo "Warning: .claude folder not found at $CLAUDE_FOLDER_PATH"
    CLAUDE_FOLDER_MOUNT=""
fi

# Combine both mounts
CLAUDE_MOUNT="$CLAUDE_JSON_MOUNT $CLAUDE_FOLDER_MOUNT"

# Build the Docker image
echo "Building Docker image..."
podman build --format=docker \
    -t dev-environment \
    "$SCRIPT_DIR"

# Run the container interactively
echo "Starting development container..."
echo "Mounting current directory to $WORKSPACE_PATH"
echo "Mounting .way directory to /workspace/.way"
echo "Starting in directory: $WORKSPACE_PATH"
podman run -it --rm \
    -v "$(pwd):$WORKSPACE_PATH:rw" \
    -v "$WAY_DIR:/workspace/.way:rw" \
    $GOOGLE_CREDS_MOUNT \
    $GEMINI_MOUNT \
    $CLAUDE_MOUNT \
    --network=host \
    --privileged \
    --user "$USER_ID:$GROUP_ID" \
    -e HOME=$WORKSPACE_PATH \
    -e USERNAME=$USERNAME \
    -e USER_UID=$USER_ID \
    -e USER_GID=$GROUP_ID \
    -e GOOGLE_APPLICATION_CREDENTIALS=/home/$USERNAME/.config/gcloud/application_default_credentials.json \
    -e PATH="/workspace/.way/commands:/home/ubuntu/.local/bin:$PATH" \
    --userns=keep-id \
    -w $WORKSPACE_PATH \
    dev-environment 
    
