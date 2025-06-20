#!/bin/bash

# Maximum number of turns for a single Claude execution
MAX_EXECUTE_TURNS=10

# Check if both project repo and user story name are provided
if [ $# -lt 2 ]; then
    echo "Usage: $0 <project-repo> <user-story-name>"
    echo "Example: $0 feedback-engine hypothesis-feedback-tool"
    exit 1
fi

PROJECT_REPO="$1"
USER_STORY="$2"

# Check if delivery folder exists, create it if it doesn't
if [ ! -d "$PROJECT_REPO/stories/$USER_STORY/delivery" ]; then
    echo "Delivery folder does not exist. Creating delivery structure..."
    mkdir -p "$PROJECT_REPO/stories/$USER_STORY/delivery/todo"
    mkdir -p "$PROJECT_REPO/stories/$USER_STORY/delivery/doing"
    mkdir -p "$PROJECT_REPO/stories/$USER_STORY/delivery/done"
    mkdir -p "$PROJECT_REPO/stories/$USER_STORY/delivery/check"
    mkdir -p "$PROJECT_REPO/stories/$USER_STORY/delivery/blocked"
    
    # Copy plan contents to todo
    if [ -d "$PROJECT_REPO/stories/$USER_STORY/plan" ]; then
        echo "Copying plan contents to delivery/todo..."
        cp -r "$PROJECT_REPO/stories/$USER_STORY/plan"/* "$PROJECT_REPO/stories/$USER_STORY/delivery/todo/"
    else
        echo "Warning: Plan directory does not exist. Todo folder is empty."
        exit 1
    fi
fi

# Maximum number of retries
MAX_RETRIES=3
RETRY_COUNT=0
# Add 10 minutes (600 seconds) buffer to retry time
RETRY_BUFFER=600

# Function to check for STOP_PRODUCTION.md file
has_stop_file() {
    local delivery_dir="$PROJECT_REPO/stories/$USER_STORY/delivery"
    [[ -f "$delivery_dir/STOP_PRODUCTION.md" ]]
}

# Function to check if there are non-README files in the delivery folder
has_non_readme_files() {
    local delivery_dir="$PROJECT_REPO/stories/$USER_STORY/delivery"
    
    # Check if directory exists
    if [[ ! -d "$delivery_dir" ]]; then
        return 1  # Directory doesn't exist, so no files
    fi
    
    # Count non-README files (case-insensitive)
    local file_count=$(find "$delivery_dir" -type f ! -iname "readme*" | wc -l)
    
    # Return 0 (true) if there are files, 1 (false) if no files
    [[ $file_count -gt 0 ]]
}

# Function to check if there are any tasks left to work on
has_tasks_to_work_on() {
    local delivery_dir="$PROJECT_REPO/stories/$USER_STORY/delivery"
    
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
    local delivery_dir="$PROJECT_REPO/stories/$USER_STORY/delivery"
    
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

# Function to check for Claude AI usage limit error and extract retry time
get_retry_time() {
    local output="$1"
    
    # Check if output contains rate limit message
    if echo "$output" | grep -q "Claude AI usage limit reached"; then
        # Extract timestamp using grep and cut
        local timestamp=$(echo "$output" | grep -o "[0-9]*$")
        if [ ! -z "$timestamp" ]; then
            echo "$timestamp"
            return
        fi
    fi
    
    echo ""
}

# Function to run claude command and handle rate limits
run_claude_command() {
    local cmd="$1"
    local output
    local retry_time
    
    # Use tee to both capture and display output
    output=$(eval "$cmd" 2>&1 | tee /dev/tty)
    local exit_code=$?
    
    retry_time=$(get_retry_time "$output")
    if [ ! -z "$retry_time" ]; then
        current_time=$(date +%s)
        # Add buffer to retry time
        retry_time=$((retry_time + RETRY_BUFFER))
        wait_time=$((retry_time - current_time))
        
        if [ $wait_time -gt 0 ]; then
            echo "Claude AI usage limit reached. Waiting until $(date -d @$retry_time) (added 10 min buffer) before retrying..."
            sleep $wait_time
            return 1
        fi
    fi
    
    if [ $exit_code -ne 0 ]; then
        return 1
    fi
    
    return 0
}

# Main loop
while has_tasks_to_work_on; do
    # Check for STOP_PRODUCTION.md file before proceeding
    if has_stop_file; then
        echo "STOP_PRODUCTION.md file detected in $PROJECT_REPO/stories/$USER_STORY/delivery folder. Exiting immediately."
        exit 1
    fi
    
    # Check if both doing and check folders are empty
    if are_doing_and_check_empty; then
        echo "Both doing and check folders are empty. Invoking triage to select next task..."
        
        echo "Triaging in noninteractive mode..."
        if ! run_claude_command "claude -p --add-dir $PROJECT_REPO --add-dir .way \"execute .way/prompts/06_triage.md against user story folder $USER_STORY in project folder $PROJECT_REPO\""; then
            RETRY_COUNT=$((RETRY_COUNT + 1))
            if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
                echo "Maximum retry attempts reached. Please try again later."
                exit 1
            fi
            continue
        fi
    else
        echo "Doing or check folders have tasks. Skipping triage and executing focused task..."
    fi

    # Check for STOP_PRODUCTION.md file before proceeding
    if has_stop_file; then
        echo "STOP_PRODUCTION.md file detected in $PROJECT_REPO/stories/$USER_STORY/delivery folder. Exiting immediately."
        exit 1
    fi

    echo "Executing task in noninteractive mode..."    
    if ! run_claude_command "claude -p --max-turns $MAX_EXECUTE_TURNS --add-dir $PROJECT_REPO --add-dir .way --dangerously-skip-permissions \"execute .way/prompts/06_execute_focused.md against user story folder $USER_STORY in project folder $PROJECT_REPO\""; then
        RETRY_COUNT=$((RETRY_COUNT + 1))
        if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
            echo "Maximum retry attempts reached. Please try again later."
            exit 1
        fi
        continue
    fi

    echo "Current task cycle complete. Checking for remaining files..."
    sleep 1  # Brief pause to avoid rapid looping
    RETRY_COUNT=0  # Reset retry count on successful execution
done

echo "No more tasks to work on in $PROJECT_REPO/stories/$USER_STORY/delivery folder. Task management complete."