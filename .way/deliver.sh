#!/bin/bash

# Maximum number of retries
MAX_RETRIES=3
RETRY_COUNT=0
# Add 10 minutes (600 seconds) buffer to retry time
RETRY_BUFFER=600

# Function to check for STOP_PRODUCTION.md file
has_stop_file() {
    local plan_dir=".way/output/04_plan"
    [[ -f "$plan_dir/STOP_PRODUCTION.md" ]]
}

# Function to check if there are non-README files in the plan folder
has_non_readme_files() {
    local plan_dir=".way/output/04_plan"
    
    # Check if directory exists
    if [[ ! -d "$plan_dir" ]]; then
        return 1  # Directory doesn't exist, so no files
    fi
    
    # Count non-README files (case-insensitive)
    local file_count=$(find "$plan_dir" -type f ! -iname "readme*" | wc -l)
    
    # Return 0 (true) if there are files, 1 (false) if no files
    [[ $file_count -gt 0 ]]
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
while has_non_readme_files; do
    # Check for STOP_PRODUCTION.md file before proceeding
    if has_stop_file; then
        echo "STOP_PRODUCTION.md file detected in .way/output/04_plan folder. Exiting immediately."
        exit 1
    fi
    
    echo "Files found in .way/output/04_plan folder. Running task management..."

    echo "Triaging in noninteractive mode..."
    if ! run_claude_command "claude -p \"execute .claude/commands/06_triage.md\""; then
        RETRY_COUNT=$((RETRY_COUNT + 1))
        if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
            echo "Maximum retry attempts reached. Please try again later."
            exit 1
        fi
        continue
    fi

    # Check for STOP_PRODUCTION.md file before proceeding
    if has_stop_file; then
        echo "STOP_PRODUCTION.md file detected in .way/output/04_plan folder. Exiting immediately."
        exit 1
    fi

    echo "Executing task in noninteractive mode..."    
    if ! run_claude_command "claude -p --dangerously-skip-permissions \"execute .claude/commands/06_execute_focused.md\""; then
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

echo "No more files in .way/output/04_plan folder. Task management complete."