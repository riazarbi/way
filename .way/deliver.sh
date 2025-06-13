#!/bin/bash

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

# Main loop
while has_non_readme_files; do
    # Check for STOP_PRODUCTION.md file before proceeding
    if has_stop_file; then
        echo "STOP_PRODUCTION.md file detected in .way/output/04_plan folder. Exiting immediately."
        exit 1
    fi
    
    echo "Files found in .way/output/04_plan folder. Running task management..."

    echo "Triaging in noninteractive mode..."
    claude -p  "execute .claude/commands/06_triage.md"

    echo "Executing task in interactive mode. You'll have to exit the prompt when I'm done to release me to start the next task."    
    claude -p --dangerously-skip-permissions "execute .claude/commands/06_execute_focused.md"

    echo "Current task cycle complete. Checking for remaining files..."
    sleep 1  # Brief pause to avoid rapid looping
done

echo "No more files in .way/output/04_plan folder. Task management complete."