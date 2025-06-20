#!/bin/bash

# Check if user story name is provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 <user-story-name>"
    echo "Example: $0 hypothesis-feedback-tool"
    exit 1
fi

USER_STORY="$1"

# Maximum number of retries
MAX_RETRIES=3
RETRY_COUNT=0
# Add 10 minutes (600 seconds) buffer to retry time
RETRY_BUFFER=600

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

# Check if delivery folder exists
if [ ! -d "docs/stories/$USER_STORY/delivery" ]; then
    echo "Error: Delivery folder does not exist for user story '$USER_STORY'"
    echo "Please run the deliver script first to set up the delivery structure."
    exit 1
fi

echo "Running check prompt for user story: $USER_STORY"

# Run the check command
if ! run_claude_command "claude -p \"execute .way/prompts/07_check.md against user story folder $USER_STORY\""; then
    RETRY_COUNT=$((RETRY_COUNT + 1))
    if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
        echo "Maximum retry attempts reached. Please try again later."
        exit 1
    fi
    echo "Check step failed. Retrying..."
    exit 1
fi

echo "Check step completed successfully." 