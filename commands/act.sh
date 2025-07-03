#!/bin/bash

echo "Running story creation prompt for project: $PWD"


claude "$(cat /workspace/.way/prompts/00_story.md)" \
--add-dir /workspace/.way/anchors --add-dir /workspace/.way/templates \
--allowedTools "Read,LS,Grep,Bash(git checkout *),Bash(git commit *),Bash(rg *),Write(/workspace/docs/*),Edit,TodoWrite,TodoRead"


echo "Story creation step completed successfully." 