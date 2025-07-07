#!/bin/bash

# Check if user story name is provided
if [ $# -lt 1 ]; then
    echo "Usage: $0 <user-story-name>"
    echo "Example: $0 hypothesis-feedback-tool"
    exit 1
fi

USER_STORY="$1"

# Check if user story folder exists
if [ ! -d "docs/stories/$USER_STORY" ]; then
    echo "Error: User story folder '$USER_STORY' does not exist in docs/stories/"
    exit 1
fi

# Check for required files in the user story folder
REQUIRED_FILES=("solution-space.md" "solution-specification.md" "target-solution.md" "user-story.md")

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "docs/stories/$USER_STORY/$file" ]; then
        echo "Error: Required file '$file' does not exist in user story folder '$USER_STORY'"
        exit 1
    fi
done


if [ ! -d "docs/stories/$USER_STORY/plan" ]; then
    echo "Error: Delivery folder does not exist for user story '$USER_STORY'"
    echo "Please run the deliver script first to set up the delivery structure."
    exit 1
fi

if [ ! -d "docs/stories/$USER_STORY/delivery" ]; then
    echo "Error: Delivery folder does not exist for user story '$USER_STORY'"
    echo "Please run the deliver script first to set up the delivery structure."
    exit 1
fi

echo "Running check prompt for user story: $USER_STORY"

# Run the check command
claude "$(cat /workspace/.way/prompts/07_check.md | sed 's/\[user-story\]/'$USER_STORY'/g')" \
    --model opus \
    --add-dir /workspace/.way/anchors \
    --dangerously-skip-permissions
    #--allowedTools "WebSearch,Read,LS,Grep,Bash(rg *),Bash(mkdir *),Bash(grep *),Bash(pipenv *),Write,Edit,TodoWrite,TodoRead,Bash(git log:*)"

echo "Check step completed successfully." 
