#!/bin/bash

# Get the current branch name
BRANCH_NAME=$(git rev-parse --abbrev-ref HEAD)
echo $BRANCH_NAME
# Create the history directory if it doesn't exist
#mkdir -p ../history

# Copy the current results to history with the branch name
#cp -r ../current/results "../history/${BRANCH_NAME}"

#echo "Archived current results to ../history/${BRANCH_NAME}" 