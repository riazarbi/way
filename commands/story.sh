#!/bin/bash

echo "Running story creation prompt for project: $PWD"

# Store the list of existing story folders before running Claude
EXISTING_STORIES=$(find docs/stories -maxdepth 1 -type d -name "*" -not -name "stories" 2>/dev/null | sort)

claude "$(cat /workspace/.way/prompts/00_story.md)" \
--model sonnet \
--add-dir /workspace/.way/anchors --add-dir /workspace/.way/templates \
--allowedTools "Read,LS,Grep,Bash(git checkout *),Bash(rg *),Write(/workspace/docs/*),Edit,TodoWrite,TodoRead"

# Get the list of story folders after running Claude
CURRENT_STORIES=$(find docs/stories -maxdepth 1 -type d -name "*" -not -name "stories" 2>/dev/null | sort)

# Find newly created story folders
NEW_STORIES=$(comm -13 <(echo "$EXISTING_STORIES") <(echo "$CURRENT_STORIES"))

if [ -n "$NEW_STORIES" ]; then
    echo "Found newly created story folders:"
    echo "$NEW_STORIES"
    
    # Process each new story folder
    while IFS= read -r story_path; do
        if [ -n "$story_path" ]; then
            STORY_FOLDER=$(basename "$story_path")
            echo "Processing story folder: $STORY_FOLDER"
            
            # Check if user-story.md exists in the folder
            if [ -f "$story_path/user-story.md" ]; then
                echo "  - user-story.md found in $STORY_FOLDER"
                
                # Check if we're in a git repository
                if git rev-parse --git-dir > /dev/null 2>&1; then
                    echo "  - Git repository detected. Handling branch operations..."
                    
                    # Check if branch already exists
                    if git show-ref --verify --quiet refs/heads/"$STORY_FOLDER"; then
                        echo "  - Branch '$STORY_FOLDER' already exists, switching to it..."
                        git checkout "$STORY_FOLDER"
                    else
                        echo "  - Creating new branch '$STORY_FOLDER' and switching to it..."
                        git checkout -b "$STORY_FOLDER"
                    fi
                    
                    # Stage and commit the user story
                    echo "  - Staging user story files..."
                    git add "$story_path/"
                    
                    echo "  - Committing user story to branch '$STORY_FOLDER'..."
                    git commit -m "Add user story: $STORY_FOLDER"
                    
                    echo "  - Successfully committed user story to branch '$STORY_FOLDER'"
                else
                    echo "  - Not in a git repository. Skipping branch operations."
                fi
            else
                echo "  - Warning: user-story.md not found in $STORY_FOLDER"
            fi
        fi
    done <<< "$NEW_STORIES"
else
    echo "No new story folders found in docs/stories"
fi

echo "Story creation step completed successfully." 