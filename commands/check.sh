#!/bin/bash

# Check if both project repo and user story name are provided
if [ $# -lt 2 ]; then
    echo "Usage: $0 <project-repo> <user-story-name>"
    echo "Example: $0 feedback-engine hypothesis-feedback-tool"
    exit 1
fi

PROJECT_REPO="$1"
USER_STORY="$2"

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
if [ ! -d "$PROJECT_REPO" ]; then
    echo "Error: Project repo directory '$PROJECT_REPO' does not exist"
    exit 1
fi

if [ ! -d "$PROJECT_REPO/stories/$USER_STORY" ]; then
    echo "Error: User story folder '$USER_STORY' does not exist in project '$PROJECT_REPO'"
    exit 1
fi

if [ ! -d "$PROJECT_REPO/stories/$USER_STORY/delivery" ]; then
    echo "Error: Delivery folder does not exist for user story '$USER_STORY' in project '$PROJECT_REPO'"
    echo "Please run the deliver script first to set up the delivery structure."
    exit 1
fi

echo "Running check prompt for user story: $USER_STORY in project: $PROJECT_REPO"

# Run the check command
claude  --dangerously-skip-permissions "execute .way/prompts/07_check.md against user story folder $USER_STORY in project folder $PROJECT_REPO"
#if ! run_claude_command "claude -p  \"execute .way/prompts/07_check.md against user story folder $USER_STORY in project folder $PROJECT_REPO\""; then
#    RETRY_COUNT=$((RETRY_COUNT + 1))
#    if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
#        echo "Maximum retry attempts reached. Please try again later."
#        exit 1
#    fi
#    echo "Check step failed. Retrying..."
#    exit 1
#fi

echo "Check step completed successfully." 