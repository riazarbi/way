#!/usr/bin/env python3

import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

def run_way_command(command: str, project: str, story_name: str) -> Dict[str, Any]:
    """Run a .way command and return the result"""
    try:
        # Get the path to the .way commands
        way_dir = Path(__file__).parent
        command_path = way_dir / "commands" / command
        
        if not command_path.exists():
            return {"success": False, "error": f"Command {command} not found"}
        
        # Run the command
        result = subprocess.run(
            [str(command_path), project, story_name],
            capture_output=True,
            text=True,
            cwd=way_dir
        )
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr if result.returncode != 0 else None
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def main():
    """Simple MCP server that wraps .way commands"""
    
    # Read the request from stdin
    request = json.loads(sys.stdin.readline())
    
    if request["method"] == "initialize":
        # Send initialization response
        response = {
            "jsonrpc": "2.0",
            "id": request["id"],
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "way-mcp",
                    "version": "1.0.0"
                }
            }
        }
        print(json.dumps(response))
        
    elif request["method"] == "tools/list":
        # List available tools
        response = {
            "jsonrpc": "2.0",
            "id": request["id"],
            "result": {
                "tools": [
                    {
                        "name": "plan",
                        "description": "Create a complete project plan for a user story",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "project": {"type": "string", "description": "Project name"},
                                "story_name": {"type": "string", "description": "User story name"}
                            },
                            "required": ["project", "story_name"]
                        }
                    },
                    {
                        "name": "do",
                        "description": "Execute development tasks from the plan",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "project": {"type": "string", "description": "Project name"},
                                "story_name": {"type": "string", "description": "User story name"}
                            },
                            "required": ["project", "story_name"]
                        }
                    },
                    {
                        "name": "check",
                        "description": "Validate completed work and generate test plans",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "project": {"type": "string", "description": "Project name"},
                                "story_name": {"type": "string", "description": "User story name"}
                            },
                            "required": ["project", "story_name"]
                        }
                    },
                    {
                        "name": "act",
                        "description": "Execute focused tasks with specific prompts",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "project": {"type": "string", "description": "Project name"},
                                "story_name": {"type": "string", "description": "User story name"}
                            },
                            "required": ["project", "story_name"]
                        }
                    }
                ]
            }
        }
        print(json.dumps(response))
        
    elif request["method"] == "tools/call":
        # Execute a tool
        tool_name = request["params"]["name"]
        args = request["params"]["arguments"]
        
        project = args.get("project")
        story_name = args.get("story_name")
        
        if not project or not story_name:
            response = {
                "jsonrpc": "2.0",
                "id": request["id"],
                "error": {
                    "code": -32602,
                    "message": "Missing required arguments: project and story_name"
                }
            }
            print(json.dumps(response))
            return
        
        # Map tool names to .way commands
        command_map = {
            "plan": "plan.sh",
            "do": "do.sh", 
            "check": "check.sh",
            "act": "act.sh"
        }
        
        if tool_name not in command_map:
            response = {
                "jsonrpc": "2.0",
                "id": request["id"],
                "error": {
                    "code": -32601,
                    "message": f"Unknown tool: {tool_name}"
                }
            }
            print(json.dumps(response))
            return
        
        # Run the command
        result = run_way_command(command_map[tool_name], project, story_name)
        
        if result["success"]:
            response = {
                "jsonrpc": "2.0",
                "id": request["id"],
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": result["output"]
                        }
                    ]
                }
            }
        else:
            response = {
                "jsonrpc": "2.0",
                "id": request["id"],
                "error": {
                    "code": -32000,
                    "message": result["error"]
                }
            }
        
        print(json.dumps(response))
    
    else:
        # Unknown method
        response = {
            "jsonrpc": "2.0",
            "id": request["id"],
            "error": {
                "code": -32601,
                "message": f"Unknown method: {request['method']}"
            }
        }
        print(json.dumps(response))

if __name__ == "__main__":
    main() 