#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Build the Docker image
echo "Building Docker image..."
docker build -t dev-environment "$SCRIPT_DIR"

# Run the container interactively
echo "Starting development container..."
docker run -it --rm \
    -v "$(pwd):/workspace" \
    -v "$SCRIPT_DIR/init-workspace.sh:/workspace/init-workspace.sh" \
    --user "$(id -u):$(id -g)" \
    dev-environment \
    bash -c "source /workspace/init-workspace.sh && exec bash" 