#!/bin/bash

# Check workflow steps and run if needed

echo "Checking workflow steps..."

# Check if research results exist
if [ ! -f ".way/output/01_research_results.md" ]; then
    echo "Running search step..."
    claude -p --dangerously-skip-permissions "execute /01_search"
    sleep 2
fi

# Check if selected solution exists
if [ ! -f ".way/output/02_selected_solution.md" ]; then
    echo "Running select step..."
    claude -p --dangerously-skip-permissions "execute /02_select"
    sleep 2
fi

# Check if solution specification exists
if [ ! -f ".way/output/03_solution_specification.md" ]; then
    echo "Running define step..."
    claude -p --dangerously-skip-permissions "execute /03_define"
    sleep 2
fi

# Check if plan folder exists
if [ ! -d ".way/output/04_plan" ]; then
    echo "Running plan step..."
    claude -p --dangerously-skip-permissions "execute /04_plan"
    sleep 2
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
    claude  -p --dangerously-skip-permissions "execute /05_decompose"
    

    # Check if the command succeeded
    if [ $? -ne 0 ]; then
        echo "Error: 05_decompose command failed. Exiting."
        exit 1
    fi

    
    
    # Add delay to prevent rapid looping
    sleep 2
done

echo "Epic decomposition process finished."

