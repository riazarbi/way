#!/bin/bash

# Check if project repo is provided
if [ $# -lt 1 ]; then
    echo "Usage: $0 <project-repo>"
    echo "Example: $0 feedback-engine"
    exit 1
fi

PROJECT_REPO="$1"

# Check if project repo exists
if [ ! -d "$PROJECT_REPO" ]; then
    echo "Error: Project repo directory '$PROJECT_REPO' does not exist in the current working directory"
    exit 1
fi

echo "Running story creation prompt for project: $PROJECT_REPO"

claude "execute /workspace/.way/prompts/00_story.md against project folder $PROJECT_REPO"

echo "Story creation step completed successfully." 