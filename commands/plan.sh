#!/bin/bash

# Check if user story name is provided
if [ $# -lt 1 ]; then
    echo "Usage: $0 <user-story-name>"
    echo "Example: $0 hypothesis-feedback-tool"
    exit 1
fi

USER_STORY="$1"

# Check workflow steps and run if needed

echo "Checking workflow steps for user story: $USER_STORY in project: $PWD"

# Check if user story exists, create it if it doesn't
if [ ! -f "docs/stories/$USER_STORY/user-story.md" ]; then
    echo "User story does not exist. Creating user story..."
    claude "$(cat /workspace/.way/prompts/00_story.md)" \
    --model sonnet \
    --add-dir /workspace/.way/anchors --add-dir /workspace/.way/templates \
    --allowedTools "Read,LS,Grep,Bash(git checkout *),Bash(git commit *),Bash(rg *),Write,Edit,TodoWrite,TodoRead,Bash(git log:*)"
fi

if [ ! -f "docs/stories/$USER_STORY/user-story.md" ]; then
    echo "No user story generated. Exiting"
    exit 1
fi

# Check if research results exist, create it if it doesn't
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



# Check if selected solution exists, create it if it doesn't
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

# Check if solution specification exists
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

# Check if plan folder exists
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

# Path to the epics directory
EPICS_DIR="docs/stories/$USER_STORY/plan"

# Function to check if an epic has been decomposed
is_decomposed() {
    local epic_dir="$1"
    # Check if there are any .md files in the epic directory (besides README.md)
    local task_files=$(find "$epic_dir" -name "*.md" -not -name "README.md" | wc -l)
    [ "$task_files" -gt 0 ]
}

# Function to get list of undecomposed epics
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

# Main loop
echo "Starting epic decomposition process..."

while true; do
    # Get list of undecomposed epics
    undecomposed_epics=($(get_undecomposed_epics))
    
    # Check if all epics are decomposed
    if [ ${#undecomposed_epics[@]} -eq 0 ]; then
        break
    fi
    
    echo "Remaining epics to decompose: ${undecomposed_epics[*]}"

    # Run the decomposition command
    echo "Running decomposition prompt..."
    claude  -p "$(cat /workspace/.way/prompts/05_decompose.md | sed 's/\[user-story\]/'$USER_STORY'/g')" \
    --model sonnet \
    --add-dir /workspace/.way/anchors \
    --allowedTools "WebSearch,Read,LS,Grep,Bash(rg *),Bash(mkdir *),Write,Edit,TodoWrite,TodoRead,Bash(git log:*)"
    
    # Add delay to prevent rapid looping
    sleep 2
done

echo "Committing plan..."
git add docs/stories
git commit -m "Decomposed epics for $USER_STORY"

echo "Epic decomposition process finished."

