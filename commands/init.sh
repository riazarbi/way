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

# 2. Create init branch if it doesn't exist
echo "2. Checking for init branch..."
if [ -d ".git" ]; then
    # Check if init branch exists
    if git show-ref --verify --quiet refs/heads/init; then
        echo "  - init branch exists, staying on current branch"
    else
        echo "  - Creating and switching to init branch..."
        git checkout -b init
    fi
else
    echo "  - No git repository found, skipping branch creation"
fi

# 3. Check for README and project purpose section
echo "3. Checking for README and project purpose section..."
README_FOUND=false
PURPOSE_SECTION_FOUND=false

# Check if README exists
if [ -f "README.md" ]; then
    echo "  - README.md found"
    README_FOUND=true
    
    # Check if project purpose section exists
    if grep -q "^## Project Purpose" README.md; then
        echo "  - Project purpose section found in README.md"
        PURPOSE_SECTION_FOUND=true
    else
        echo "  - Project purpose section not found in README.md"
    fi
else
    echo "  - README.md not found"
fi

# 4. Use Claude to gather project purpose information if needed
if [ "$README_FOUND" = false ] || [ "$PURPOSE_SECTION_FOUND" = false ]; then
    echo "4. Gathering project purpose information using Claude..."
    
    echo "  - Running Claude to gather project purpose information..."
    claude -p "$(cat "$WAY_DIR/prompts/00_init.md")" \
    --model sonnet \
    --add-dir "$WAY_DIR/anchors" --add-dir "$WAY_DIR/templates" \
    --allowedTools "Read,LS,Grep,Bash(git checkout *),Bash(git commit *),Bash(rg *),Write,Edit,TodoWrite,TodoRead,Bash(git log:*)"
    
    # Check if README was created or updated
    if [ -f "README.md" ]; then
        if grep -q "^## Project Purpose" README.md; then
            echo "  - Project purpose section successfully added to README.md"
            PURPOSE_SECTION_FOUND=true
        else
            echo "  - Warning: Project purpose section may not have been added correctly"
        fi
    else
        echo "  - Warning: README.md was not created"
    fi
else
    echo "  - README.md and project purpose section already exist, skipping Claude interaction"
fi

# 5. Copy CONTRIBUTING file if it doesn't exist
echo "5. Checking for CONTRIBUTING file..."
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

# 6. Copy docs folder if it doesn't exist
echo "6. Checking for docs folder..."
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

# 7. Create docs/stories folder if it doesn't exist
echo "7. Checking for docs/stories folder..."
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
echo "  - README.md: $(if [ -f "README.md" ]; then echo "Present"; else echo "Missing"; fi)"
echo "  - Project Purpose Section: $(if [ "$PURPOSE_SECTION_FOUND" = true ]; then echo "Present"; else echo "Missing"; fi)"
echo "  - CONTRIBUTING.md: $(if [ -f "CONTRIBUTING.md" ]; then echo "Present"; else echo "Missing"; fi)"
echo "  - docs folder: $(if [ -d "docs" ]; then echo "Present"; else echo "Missing"; fi)"
echo "  - docs/stories folder: $(if [ -d "docs/stories" ]; then echo "Present"; else echo "Missing"; fi)" 