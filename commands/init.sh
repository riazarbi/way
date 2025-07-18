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

# 8. Create quality config file if it doesn't exist or has invalid structure
echo "8. Checking for quality configuration..."
if [ ! -f ".quality-config.json" ]; then
    echo "  - .quality-config.json not found, copying from templates..."
    if [ -f "$TEMPLATES_DIR/quality-config.json" ]; then
        cp "$TEMPLATES_DIR/quality-config.json" ".quality-config.json"
        echo "  - .quality-config.json copied successfully"
    else
        echo "  - Warning: $TEMPLATES_DIR/quality-config.json not found"
    fi
else
    # Check if the existing file has valid JSON structure
    if command -v jq &> /dev/null; then
        if jq empty .quality-config.json 2>/dev/null; then
            # Check if it has the required structure
            if jq -e '.test and .lint and .metrics' .quality-config.json >/dev/null 2>&1; then
                echo "  - .quality-config.json exists and has valid structure"
            else
                echo "  - .quality-config.json exists but missing required structure, copying template..."
                if [ -f "$TEMPLATES_DIR/quality-config.json" ]; then
                    cp "$TEMPLATES_DIR/quality-config.json" ".quality-config.json"
                    echo "  - .quality-config.json updated successfully"
                else
                    echo "  - Warning: $TEMPLATES_DIR/quality-config.json not found"
                fi
            fi
        else
            echo "  - .quality-config.json exists but has invalid JSON, copying template..."
            if [ -f "$TEMPLATES_DIR/quality-config.json" ]; then
                cp "$TEMPLATES_DIR/quality-config.json" ".quality-config.json"
                echo "  - .quality-config.json updated successfully"
            else
                echo "  - Warning: $TEMPLATES_DIR/quality-config.json not found"
            fi
        fi
    else
        echo "  - .quality-config.json exists (jq not available for validation)"
    fi
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
echo "  - .quality-config.json: $(if [ -f ".quality-config.json" ]; then echo "Present"; else echo "Missing"; fi)" 