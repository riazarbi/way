#!/bin/bash

# Path to the epics directory
EPICS_DIR=".way/output/04_plan/todo"

# Check if epics directory exists, exit if not
if [ ! -d "$EPICS_DIR" ]; then
    echo "Error: Epics directory '$EPICS_DIR' does not exist. Exiting."
    exit 1
fi

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
    for epic_dir in "$EPICS_DIR"/*; do
        if [ -d "$epic_dir" ] && ! is_decomposed "$epic_dir"; then
            undecomposed+=("$(basename "$epic_dir")")
        fi
    done
    echo "${undecomposed[@]}"
}

# Main loop
echo "Starting epic decomposition process..."

while true; do
    # Get list of undecomposed epics
    undecomposed_epics=($(get_undecomposed_epics))
    
    # Check if all epics are decomposed
    if [ ${#undecomposed_epics[@]} -eq 0 ]; then
        echo "All epics have been decomposed. Process complete!"
        break
    fi
    
    echo "Remaining epics to decompose: ${undecomposed_epics[*]}"
    
    # Run the decomposition command
    echo "Running decomposition prompt..."
    ./05_decompose
    
    # Check if the command succeeded
    if [ $? -ne 0 ]; then
        echo "Error: 05_decompose command failed. Exiting."
        exit 1
    fi
    
    # Optional: Add a small delay to prevent rapid looping
    sleep 1
done

echo "Epic decomposition process finished."