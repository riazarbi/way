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

# Check if there's a task file in the doing directory and move one if needed
echo "Checking for active tasks..."

DOING_DIR=".way/output/04_plan/doing"
TODO_DIR=".way/output/04_plan/todo"

# Function to check if there are task files in doing directory
has_task_in_doing() {
    if [ -d "$DOING_DIR" ]; then
        local task_count=$(find "$DOING_DIR" -type f -name "*.md" -not -name "README.md" | wc -l)
        [ "$task_count" -gt 0 ]
    else
        return 1
    fi
}

# Function to find and move a task from todo to doing
move_task_to_doing() {
    if [ -d "$TODO_DIR" ]; then
        # Look for task files in all subdirectories of todo
        for epic_dir in "$TODO_DIR"/*; do
            if [ -d "$epic_dir" ]; then
                # Find the first task file (not README.md) in this epic
                local task_file=$(find "$epic_dir" -type f -name "*.md" -not -name "README.md" | head -n 1)
                if [ -n "$task_file" ]; then
                    echo "Moving task file: $(basename "$task_file") from $(basename "$epic_dir") to doing..."
                    mv "$task_file" "$DOING_DIR/"
                    return 0
                fi
            fi
        done
    fi
    return 1
}

# Check if there's already a task in doing
if has_task_in_doing; then
    echo "Active task found in doing directory."
else
    echo "No active task found. Looking for a task to move from todo..."
    if move_task_to_doing; then
        echo "Task moved to doing directory successfully."
    else
        echo "No available tasks found in todo directories."
    fi
fi

claude --dangerously-skip-permissions "execute /06_execute_focused"

echo "Task management complete."