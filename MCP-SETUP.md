# Way MCP Server Setup

## What it does
The `way-mcp.py` file creates a simple MCP server that wraps the existing `.way` shell commands, making them available to AI assistants like Claude.

## Setup (Already done!)
- ✅ MCP config created at `~/.claude/mcp-config.json`
- ✅ Way MCP server ready at `/home/riaz/projects/.way/way-mcp.py`

## Available Tools
- `plan` - Create a complete project plan for a user story
- `do` - Execute development tasks from the plan  
- `check` - Validate completed work and generate test plans
- `act` - Execute focused tasks with specific prompts

## Usage Examples
Once configured, you can use it in Claude like:

```
plan a project called "my-app" with story "user-auth"
do the tasks for "my-app" story "user-auth"
check the progress of "my-app" story "user-auth"
```

## How it works
The MCP server simply calls the existing `.way` shell commands:
- `plan` → runs `plan.sh`
- `do` → runs `do.sh`
- `check` → runs `check.sh` 
- `act` → runs `act.sh`

No complexity, just a simple wrapper around what already works! 