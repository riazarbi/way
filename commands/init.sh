#!/bin/bash

# Store the absolute path to the .way directory before changing directories
WAY_DIR=/workspace/.way
TEMPLATES_DIR="$WAY_DIR/templates"

echo "Using templates from: $TEMPLATES_DIR"

echo "Initializing project in: $(pwd)"
sleep 5

# 1. Commit all existing code
echo "1. Committing all existing code..."
if [ -d ".git" ]; then
    # Check if there are any changes to commit
    if ! git diff-index --quiet HEAD --; then
        echo "  - Staging all changes..."
        git add .
        
        echo "  - Committing changes..."
        git commit -m "Initial commit before project initialization"
    else
        echo "  - No changes to commit"
    fi
else
    echo "  - No git repository found, skipping commit"
fi

# 2. Create a new init branch
echo "2. Creating new init branch..."
if [ -d ".git" ]; then
    # Check if we're already on an init branch
    current_branch=$(git branch --show-current)
    if [[ "$current_branch" == "init" ]]; then
        echo "  - Already on init branch"
    else
        echo "  - Creating and switching to init branch..."
        git checkout -b init
    fi
else
    echo "  - No git repository found, skipping branch creation"
fi

# 3. Copy CONTRIBUTING file if it doesn't exist
echo "3. Checking for CONTRIBUTING file..."
if [ ! -f "CONTRIBUTING.md" ]; then
    echo "  - CONTRIBUTING.md not found, copying from templates..."
    if [ -f "$TEMPLATES_DIR/CONTRIBUTING.md" ]; then
        cp "$TEMPLATES_DIR/CONTRIBUTING.md" "CONTRIBUTING.md"
        echo "  - CONTRIBUTING.md copied successfully"
    else
        echo "  - Warning: $TEMPLATES_DIR/CONTRIBUTING.md not found"
    fi
else
    echo "  - CONTRIBUTING.md already exists"
fi

# 4. Copy docs folder if it doesn't exist
echo "4. Checking for docs folder..."
if [ ! -d "docs" ]; then
    echo "  - docs folder not found, copying from templates..."
    if [ -d "$TEMPLATES_DIR/docs" ]; then
        cp -r "$TEMPLATES_DIR/docs" "docs"
        echo "  - docs folder copied successfully"
    else
        echo "  - Warning: $TEMPLATES_DIR/docs not found"
    fi
else
    echo "  - docs folder already exists"
fi

# 5. Create docs/stories folder if it doesn't exist
echo "5. Checking for docs/stories folder..."
if [ ! -d "docs/stories" ]; then
    echo "  - Creating docs/stories folder..."
    mkdir -p "docs/stories"
    echo "  - docs/stories folder created successfully"
else
    echo "  - docs/stories folder already exists"
fi

echo "Project initialization complete!"
echo "Summary:"
echo "  - Repository: $(git remote get-url origin 2>/dev/null || echo 'No remote')"
echo "  - Branch: $(git branch --show-current 2>/dev/null || echo 'Not a git repo')"
echo "  - CONTRIBUTING.md: $(if [ -f "CONTRIBUTING.md" ]; then echo "Present"; else echo "Missing"; fi)"
echo "  - docs folder: $(if [ -d "docs" ]; then echo "Present"; else echo "Missing"; fi)"
echo "  - docs/stories folder: $(if [ -d "docs/stories" ]; then echo "Present"; else echo "Missing"; fi)" 