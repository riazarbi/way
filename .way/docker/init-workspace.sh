#!/bin/bash

# Create and set up .claude directory
CLAUDE_DIR=".claude"
echo "Setting up $CLAUDE_DIR directory..."
mkdir -p "$CLAUDE_DIR"
cd "$CLAUDE_DIR"

# Initialize npm project if package.json doesn't exist
if [ ! -f "package.json" ]; then
    echo "Initializing npm project in $CLAUDE_DIR..."
    npm init -y
fi

# Install claude-code locally if not already installed
if [ ! -d "node_modules/@anthropic-ai/claude-code" ]; then
    echo "Installing claude-code..."
    npm install @anthropic-ai/claude-code
fi

# Debug information
echo "Checking npm installation..."
npm list @anthropic-ai/claude-code

# Find the claude binary
CLAUDE_BIN=$(find node_modules/.bin -name claude 2>/dev/null)
if [ -n "$CLAUDE_BIN" ]; then
    echo "Found claude binary at: $CLAUDE_BIN"
    
    # Create a symlink to make the claude command available
    if [ ! -f "/usr/local/bin/claude" ]; then
        echo "Creating symlink for claude command..."
        ln -sf "$(pwd)/$CLAUDE_BIN" /usr/local/bin/claude
        chmod +x /usr/local/bin/claude
    fi
    
    # Add the local bin directory to PATH
    export PATH="$PATH:$(pwd)/node_modules/.bin"
    echo "Added node_modules/.bin to PATH"
else
    echo "ERROR: Could not find claude binary in node_modules/.bin"
    exit 1
fi

# Return to workspace root
cd /workspace

# Ensure .claude-code directory exists and has correct permissions
echo "Setting up .claude-code directory..."
mkdir -p .claude-code
chmod 777 .claude-code

# If there are any existing files in .claude-code, ensure they have correct permissions
if [ -d ".claude-code" ]; then
    chmod -R 777 .claude-code
    echo "Updated permissions for existing .claude-code directory"
fi 