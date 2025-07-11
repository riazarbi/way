#!/bin/bash

# =============================================================================
# Way - AI-Powered Development Workflow Tool
# Plan Script: Creates complete project plans for user stories
# =============================================================================

# Check if user story name is provided
if [ $# -lt 1 ]; then
    echo "Usage: $0 <user-story-name>"
    echo "Example: $0 hypothesis-feedback-tool"
    exit 1
fi

USER_STORY="$1"

# =============================================================================
# BRANCH VALIDATION
# Ensure we're on the correct git branch that matches the user story name
# This prevents accidentally running the script on the wrong branch
# =============================================================================
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "$USER_STORY" ]; then
    echo "Error: Current branch '$CURRENT_BRANCH' does not match user story name '$USER_STORY'"
    echo "Please switch to branch '$USER_STORY' or use a different user story name"
    exit 1
fi

echo "Confirmed: On branch '$CURRENT_BRANCH' for user story '$USER_STORY'"

# =============================================================================
# USER STORY CREATION PHASE
# Create the user story if it doesn't exist, then commit and tag it
# This is the foundation for all subsequent workflow steps
# =============================================================================
echo "Checking workflow steps for user story: $USER_STORY in project: $PWD"

# Check if user story exists, create it if it doesn't
if [ ! -f "docs/stories/$USER_STORY/user-story.md" ]; then
    echo "User story does not exist. Creating user story..."
    claude "$(cat /workspace/.way/prompts/00_story.md)" \
    --model sonnet \
    --add-dir /workspace/.way/anchors --add-dir /workspace/.way/templates \
    --allowedTools "Read,LS,Grep,Bash(git checkout *),Bash(git commit *),Bash(rg *),Write,Edit,TodoWrite,TodoRead,Bash(git log:*)"
    
    # Verify the user story was actually created
    if [ ! -f "docs/stories/$USER_STORY/user-story.md" ]; then
        echo "No user story generated. Exiting"
        exit 1
    fi
    
    # Commit the user story that was just created
    echo "Committing user story..."
    git add "docs/stories/$USER_STORY/user-story.md"
    git commit -m "Created user story: $USER_STORY"
    
    # Get the commit hash for this user story creation
    USER_STORY_COMMIT=$(git rev-parse HEAD)
    
    # Tag this commit as the user story step for easy reference
    echo "Tagging user story commit..."
    git tag "$CURRENT_BRANCH-story" $USER_STORY_COMMIT
    
    # Track the number of user story formulation attempts (starts at 1)
    echo "Tracking user story formulation attempts..."
    ATTEMPT_COUNT=1
    git notes --ref=attempts add -m "$ATTEMPT_COUNT" $USER_STORY_COMMIT
    
    echo "User story committed at: $USER_STORY_COMMIT"
    echo "User story formulation attempt: $ATTEMPT_COUNT"
fi

# =============================================================================
# USER STORY MODIFICATION CHECK
# Detect if the user story has been modified since the tagged commit
# This helps prevent accidental changes to the user story
# =============================================================================
TAG_NAME="$CURRENT_BRANCH-story"
if git tag -l "$TAG_NAME" | grep -q "$TAG_NAME"; then
    echo "Checking if user story has been modified..."
    if ! git diff --quiet "$TAG_NAME" -- "docs/stories/$USER_STORY/user-story.md"; then
        echo "Warning: User story has been modified since the tagged commit"
        echo ""
        echo "=== CHANGES DETECTED ==="
        echo "Showing differences between tagged version and current version:"
        echo ""
        git diff --color=always "$TAG_NAME" -- "docs/stories/$USER_STORY/user-story.md"
        echo ""
        echo "=== END OF CHANGES ==="
        echo ""
        echo "Options:"
        echo "1. Revert changes (discard modifications to the user story, use original tagged version)"
        echo "2. Commit changes (reset hard, destroying all downstream commits, and restart the process with the new user story.)"
        echo "3. Panic and exit (non destructive)"
        read -p "Choose option (1/2/3): " -n 1 -r
        echo
        case $REPLY in
            1)
                echo "Reverting user story to tagged version..."
                git checkout "$TAG_NAME" -- "docs/stories/$USER_STORY/user-story.md"
                echo "User story reverted to tagged version"
                ;;
            2)
                echo "Committing user story changes..."
                # Capture the current user story content before reset
                CURRENT_USER_STORY_CONTENT=$(cat "docs/stories/$USER_STORY/user-story.md")
                # Get current attempt count from the old tag
                CURRENT_ATTEMPT=$(git notes --ref=attempts show "$TAG_NAME" 2>/dev/null || echo "1")
                # Increment attempt count
                NEW_ATTEMPT=$((CURRENT_ATTEMPT + 1))
                # Reset to the tagged commit
                git reset --hard "$TAG_NAME"
                # Write the captured content back to the file
                echo "$CURRENT_USER_STORY_CONTENT" > "docs/stories/$USER_STORY/user-story.md"
                # Add the modified user story
                git add "docs/stories/$USER_STORY/user-story.md"
                # Commit the changes
                git commit -m "Updated user story: $USER_STORY"
                # Get the new commit hash
                NEW_USER_STORY_COMMIT=$(git rev-parse HEAD)
                # Remove the old tag
                git tag -d "$TAG_NAME"
                # Create new tag
                git tag "$TAG_NAME" $NEW_USER_STORY_COMMIT
                # Add incremented attempt count as note to the new commit
                git notes --ref=attempts add -m "$NEW_ATTEMPT" $NEW_USER_STORY_COMMIT
                echo "User story changes committed and tagged at: $NEW_USER_STORY_COMMIT"
                echo "User story formulation attempt: $NEW_ATTEMPT"
                ;;
            3)
                echo "Exiting..."
                exit 1
                ;;
            *)
                echo "Invalid option. Exiting..."
                exit 1
                ;;
        esac
    else
        echo "User story unchanged since tagged commit"
    fi
fi

# =============================================================================
# SOLUTION RESEARCH PHASE
# Research potential solutions and approaches for the user story
# This phase explores the solution space and identifies options
# =============================================================================
if [ ! -f "docs/stories/$USER_STORY/solution-space.md" ]; then
    echo "Running search step..."
    claude -p "$(cat /workspace/.way/prompts/01_search.md | sed 's/\[user-story\]/'$USER_STORY'/g')" \
    --model sonnet \
    --add-dir /workspace/.way/anchors \
    --allowedTools "WebSearch,Read,LS,Grep,Bash(rg *),Write,Edit,TodoWrite,TodoRead,Bash(git log:*)"
fi

if [ ! -f "docs/stories/$USER_STORY/solution-space.md" ]; then
    echo "No output generated. Exiting"
    exit 1
fi

# =============================================================================
# SOLUTION SELECTION PHASE
# Choose the optimal solution from the researched options
# This phase evaluates and selects the best approach
# =============================================================================
if [ ! -f "docs/stories/$USER_STORY/target-solution.md" ]; then
    echo "Running select step..."
    claude -p "$(cat /workspace/.way/prompts/02_select.md | sed 's/\[user-story\]/'$USER_STORY'/g')" \
    --model sonnet \
    --add-dir /workspace/.way/anchors \
    --allowedTools "WebSearch,Read,LS,Grep,Bash(rg *),Write,TodoWrite,TodoRead,Bash(git log:*)"
fi

if [ ! -f "docs/stories/$USER_STORY/target-solution.md" ]; then
    echo "No output generated. Exiting"
    exit 1
fi

# =============================================================================
# SOLUTION DEFINITION PHASE
# Create detailed specifications for the selected solution
# This phase defines the technical requirements and implementation details
# =============================================================================
if [ ! -f "docs/stories/$USER_STORY/solution-specification.md" ]; then
    echo "Running define step..."
    claude -p "$(cat /workspace/.way/prompts/03_define.md | sed 's/\[user-story\]/'$USER_STORY'/g')" \
    --model sonnet \
    --add-dir /workspace/.way/anchors \
    --allowedTools "WebSearch,Read,LS,Grep,Bash(rg *),Write,Edit,TodoWrite,TodoRead,Bash(git log:*)"
fi

if [ ! -f "docs/stories/$USER_STORY/solution-specification.md" ]; then
    echo "No output generated. Exiting"
    exit 1
fi

# =============================================================================
# IMPLEMENTATION PLANNING PHASE
# Create the implementation plan with epics and high-level tasks
# This phase breaks down the solution into manageable work units
# =============================================================================
if [ ! -d "docs/stories/$USER_STORY/plan" ]; then
    echo "Running plan step..."
    claude -p "$(cat /workspace/.way/prompts/04_plan.md | sed 's/\[user-story\]/'$USER_STORY'/g')" \
    --model sonnet \
    --add-dir /workspace/.way/anchors \
    --allowedTools "WebSearch,Read,LS,Grep,Bash(rg *),Bash(mkdir *),Write,Edit,TodoWrite,TodoRead,Bash(git log:*)"
fi

if [ ! -d "docs/stories/$USER_STORY/plan" ]; then
    echo "No output generated. Exiting"
    exit 1
fi

echo "All workflow steps complete. Proceeding with decomposition..."

# =============================================================================
# EPIC DECOMPOSITION PHASE
# Break down epics into individual tasks for implementation
# This phase creates the detailed task breakdown for development
# =============================================================================

# Path to the epics directory
EPICS_DIR="docs/stories/$USER_STORY/plan"

# Function to check if an epic has been decomposed into tasks
is_decomposed() {
    local epic_dir="$1"
    # Check if there are any .md files in the epic directory (besides README.md)
    local task_files=$(find "$epic_dir" -name "*.md" -not -name "README.md" | wc -l)
    [ "$task_files" -gt 0 ]
}

# Function to get list of undecomposed epics that need task breakdown
get_undecomposed_epics() {
    local undecomposed=()
    if [ -d "$EPICS_DIR" ]; then
        for epic_dir in "$EPICS_DIR"/*; do
            if [ -d "$epic_dir" ] && ! is_decomposed "$epic_dir"; then
                undecomposed+=("$(basename "$epic_dir")")
            fi
        done
    fi
    echo "${undecomposed[@]}"
}

# Main decomposition loop - process each epic until all are decomposed
echo "Starting epic decomposition process..."

while true; do
    # Get list of undecomposed epics
    undecomposed_epics=($(get_undecomposed_epics))
    
    # Check if all epics are decomposed
    if [ ${#undecomposed_epics[@]} -eq 0 ]; then
        break
    fi
    
    echo "Remaining epics to decompose: ${undecomposed_epics[*]}"

    # Run the decomposition command to break down epics into tasks
    echo "Running decomposition prompt..."
    claude  -p "$(cat /workspace/.way/prompts/05_decompose.md | sed 's/\[user-story\]/'$USER_STORY'/g')" \
    --model sonnet \
    --add-dir /workspace/.way/anchors \
    --allowedTools "WebSearch,Read,LS,Grep,Bash(rg *),Bash(mkdir *),Write,Edit,TodoWrite,TodoRead,Bash(git log:*)"
    
    # Add delay to prevent rapid looping and rate limit issues
    sleep 2
done

# =============================================================================
# FINAL COMMIT
# Commit all the planning work and mark the plan as complete
# =============================================================================
echo "Committing plan..."
git add docs/stories
git commit -m "Decomposed epics for $USER_STORY"

echo "Epic decomposition process finished."

