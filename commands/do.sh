#!/bin/bash

# Check if user story name is provided
if [ $# -lt 1 ]; then
    echo "Usage: $0 <user-story-name>"
    echo "Example: $0 hypothesis-feedback-tool"
    exit 1
fi

USER_STORY="$1"

# Check if delivery folder exists, create it if it doesn't
if [ ! -d "docs/stories/$USER_STORY/delivery" ]; then
    echo "Delivery folder does not exist. Creating delivery structure..."
    mkdir -p "docs/stories/$USER_STORY/delivery/todo"
    mkdir -p "docs/stories/$USER_STORY/delivery/doing"
    mkdir -p "docs/stories/$USER_STORY/delivery/done"
    mkdir -p "docs/stories/$USER_STORY/delivery/check"
    mkdir -p "docs/stories/$USER_STORY/delivery/blocked"
    
    # Copy plan contents to todo
    if [ -d "docs/stories/$USER_STORY/plan" ]; then
        echo "Copying plan contents to delivery/todo..."
        cp -r "docs/stories/$USER_STORY/plan"/* "docs/stories/$USER_STORY/delivery/todo/"
    else
        echo "Warning: Plan directory does not exist. Todo folder is empty."
        exit 1
    fi
fi

# Function to check for STOP_PRODUCTION.md file
has_stop_file() {
    local delivery_dir="docs/stories/$USER_STORY/delivery"
    [[ -f "$delivery_dir/STOP_PRODUCTION.md" ]]
}

# Function to check if there are any tasks left to work on
has_tasks_to_work_on() {
    local delivery_dir="docs/stories/$USER_STORY/delivery"
    
    # Check if directory exists
    if [[ ! -d "$delivery_dir" ]]; then
        return 1  # Directory doesn't exist, so no tasks
    fi
    
    # Count non-README files in todo, doing, and check folders
    local todo_count=$(find "$delivery_dir/todo" -type f ! -iname "readme*" 2>/dev/null | wc -l)
    local doing_count=$(find "$delivery_dir/doing" -type f ! -iname "readme*" 2>/dev/null | wc -l)
    local check_count=$(find "$delivery_dir/check" -type f ! -iname "readme*" 2>/dev/null | wc -l)
    
    # Return 0 (true) if there are tasks in any of these folders, 1 (false) if all are empty
    [[ $todo_count -gt 0 || $doing_count -gt 0 || $check_count -gt 0 ]]
}

# Function to check if both doing and check folders are empty
are_doing_and_check_empty() {
    local delivery_dir="docs/stories/$USER_STORY/delivery"
    
    # Check if directories exist
    if [[ ! -d "$delivery_dir/doing" ]] || [[ ! -d "$delivery_dir/check" ]]; then
        return 0  # Consider empty if directories don't exist
    fi
    
    # Count files in doing and check (excluding README files)
    local doing_count=$(find "$delivery_dir/doing" -type f ! -iname "readme*" 2>/dev/null | wc -l)
    local check_count=$(find "$delivery_dir/check" -type f ! -iname "readme*" 2>/dev/null | wc -l)
    
    # Return 0 (true) if both are empty, 1 (false) if either has files
    [[ $doing_count -eq 0 && $check_count -eq 0 ]]
}

# Main loop
while has_tasks_to_work_on; do
    # Check for STOP_PRODUCTION.md file before proceeding
    if has_stop_file; then
        echo "STOP_PRODUCTION.md file detected in docs/stories/$USER_STORY/delivery folder. Exiting immediately."
        exit 1
    fi
    
    # Check if both doing and check folders are empty
    if are_doing_and_check_empty; then
        echo "Both doing and check folders are empty. Invoking triage to select next task..."
        
        echo "Triaging ..."
        #claude --dangerously-skip-permissions  --output-format stream-json --verbose -p  "execute /workspace/.way/prompts/06_triage.md against user story folder docs/stories/$USER_STORY in project folder $PWD" | jq --color-output .

    #echo "Sleeping for 720 seconds..."
    #sleep 720


        claude -p "$(cat /workspace/.way/prompts/06_triage.md | sed 's/\[user-story\]/'$USER_STORY'/g')" \
        --model sonnet \
        --add-dir /workspace/.way/anchors \
        --allowedTools "WebSearch,Read,LS,Grep,Bash(rg:*),Bash(mkdir),Bash(mkdir -p),Bash(mv:*),Bash(mv),Write,Edit,TodoWrite,TodoRead,Bash(git log:*)" 
    
    else
        echo "Doing or check folders have tasks. Skipping triage and executing focused task..."
    fi

    # Check for STOP_PRODUCTION.md file before proceeding
    if has_stop_file; then
        echo "STOP_PRODUCTION.md file detected in docs/stories/$USER_STORY/delivery folder. Exiting immediately."
        exit 1
    fi

    echo "Executing task in interactive mode..."
    #claude --dangerously-skip-permissions "execute /workspace/.way/prompts/06_execute.md for user story folder docs/stories/$USER_STORY in project folder $PWD"

    claude -p "$(cat /workspace/.way/prompts/06_execute.md | sed 's/\[user-story\]/'$USER_STORY'/g')" \
        --model sonnet \
        --add-dir /workspace/.way/anchors \
        --dangerously-skip-permissions  

    echo "Validating task in interactive mode..."
    #claude --dangerously-skip-permissions "execute /workspace/.way/prompts/06_validate.md for user story folder docs/stories/$USER_STORY in project folder $PWD"    
    claude -p "$(cat /workspace/.way/prompts/06_validate.md | sed 's/\[user-story\]/'$USER_STORY'/g')" \
        --model sonnet \
        --add-dir /workspace/.way/anchors \
        --dangerously-skip-permissions  

    echo "Current task cycle complete. Checking for remaining files..."
    sleep 1  # Brief pause to avoid rapid looping
done

echo "No more tasks to work on in docs/stories/$USER_STORY/delivery folder. Task management complete."

echo "Committing delivery..."
git add docs/stories/$USER_STORY/delivery
git commit -m "Completed tasks for $USER_STORY"

