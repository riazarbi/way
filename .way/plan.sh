#!/bin/bash

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

# Check workflow steps and run if needed

echo "Checking workflow steps..."

# Check if research results exist
if [ ! -f ".way/output/01_research_results.md" ]; then
    echo "Running search step..."
    if ! run_claude_command "claude -p \"execute .claude/commands/01_search.md\""; then
        echo "Search step failed. Exiting."
        exit 1
    fi
    sleep 2
fi

if [ ! -f ".way/output/01_research_results.md" ]; then
    echo "No output generated. Exiting"
    exit 1
fi

# Check if selected solution exists
if [ ! -f ".way/output/02_selected_solution.md" ]; then
    echo "Running select step..."
    if ! run_claude_command "claude -p \"execute .claude/commands/02_select.md\""; then
        echo "Select step failed. Exiting."
        exit 1
    fi
    sleep 2
fi

if [ ! -f ".way/output/02_selected_solution.md" ]; then
    echo "No output generated. Exiting"
    exit 1
fi

# Check if solution specification exists
if [ ! -f ".way/output/03_solution_specification.md" ]; then
    echo "Running define step..."
    if ! run_claude_command "claude -p \"execute .claude/commands/03_define.md\""; then
        echo "Define step failed. Exiting."
        exit 1
    fi
    sleep 2
fi

if [ ! -f ".way/output/03_solution_specification.md" ]; then
    echo "No output generated. Exiting"
    exit 1
fi

# Check if plan folder exists
if [ ! -d ".way/output/04_plan" ]; then
    echo "Running plan step..."
    if ! run_claude_command "claude -p \"execute .claude/commands/04_plan.md\""; then
        echo "Plan step failed. Exiting."
        exit 1
    fi
    sleep 2
fi

if [ ! -d ".way/output/04_plan" ]; then
    echo "No output generated. Exiting"
    exit 1
fi

echo "All workflow steps complete. Proceeding with decomposition..."

# Path to the epics directory
EPICS_DIR=".way/output/04_plan/todo"

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
    if ! run_claude_command "claude -p \"execute .claude/commands/05_decompose.md\""; then
        echo "Decomposition step failed. Exiting."
        exit 1
    fi
    
    # Add delay to prevent rapid looping
    sleep 2
done

echo "Epic decomposition process finished."

