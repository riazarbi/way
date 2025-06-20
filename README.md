# Way - AI-Powered Development Workflow Tool

Way is a containerized development environment that provides AI-powered project planning and execution workflows using Claude AI. It helps you break down user stories, create implementation plans, and manage development tasks.

## Quick Setup

1. **Clone the repository** into your projects directory:
   ```bash
   cd ~/projects
   git clone <way-repo-url> .way
   ```

2. **Add the alias** to your `.bashrc`:
   ```bash
   echo 'alias dev="~/.way/docker/dev.sh"' >> ~/.bashrc
   source ~/.bashrc
   ```

3. **Start the development environment**:
   ```bash
   dev
   ```

## Prerequisites

- **Podman**: The container runtime used by way
- **Git**: For cloning the repository
- **Claude CLI**: Installed automatically in the container

**If you do not use podman, modify docker/dev.sh for compatibility with your container runtime**

## How It Works

The `dev` alias runs a containerized development environment that:
- Mounts your current project directory to `/workspace` in the container
- Provides access to way commands in `/workspace/.way/commands/`
- Uses your host user ID/GID for proper file permissions
- Includes Python, Node.js, and development tools

## Available Commands

Once inside the container, you can use these commands from `/workspace/.way/commands/`:

### `plan.sh <project-repo> <user-story-name>`
Creates a complete project plan for a user story:
- Generates user story documentation
- Researches solution space
- Selects target solution
- Creates solution specification
- Breaks down into epics and tasks

**Example:**
```bash
plan.sh feedback-engine hypothesis-feedback-tool
```

### `do.sh <project-repo> <user-story-name>`
Executes development tasks from the plan:
- Moves tasks from `todo/` to `doing/`
- Executes tasks using Claude AI
- Moves completed tasks to `done/`
- Handles task failures and retries

**Example:**
```bash
do.sh feedback-engine hypothesis-feedback-tool
```

### `check.sh <project-repo> <user-story-name>`
Validates completed work and generates test plans:
- Reviews completed tasks
- Creates validation documentation
- Generates test scenarios

**Example:**
```bash
check.sh feedback-engine hypothesis-feedback-tool
```

### `act.sh <project-repo> <user-story-name>`
Executes focused tasks with specific prompts:
- Runs individual tasks with custom prompts
- Useful for targeted development work

**Example:**
```bash
act.sh feedback-engine hypothesis-feedback-tool
```

### `pdc`
Project Development Cycle - runs the complete workflow:
- Combines plan, do, and check phases
- Automates the full development cycle

## Project Structure

When you run way commands, they create this structure in your project:

```
project-repo/
└── stories/
    └── user-story-name/
        ├── user-story.md              # Story definition
        ├── solution-space.md          # Research results
        ├── target-solution.md         # Selected solution
        ├── solution-specification.md  # Detailed specification
        ├── plan/                      # Implementation plan
        │   ├── README.md             # Overall plan
        │   └── epic-name/            # Epic breakdowns
        │       ├── README.md         # Epic overview
        │       └── task-files.md     # Individual tasks
        └── delivery/                 # Execution tracking
            ├── todo/                 # Pending tasks
            ├── doing/                # Active tasks
            ├── done/                 # Completed tasks
            └── check/                # Validation tasks
```

## Workflow

1. **Plan**: Use `plan.sh` to create a complete project plan
2. **Do**: Use `do.sh` to execute development tasks
3. **Check**: Use `check.sh` to validate and test
4. **Repeat**: Iterate through the cycle as needed

## Configuration

The container includes:
- Ubuntu 22.04 base
- Python 3 with pip
- Node.js 20.x with npm
- Claude CLI for AI interactions
- Git and development tools
- Proper user permissions matching your host

## Troubleshooting

### Permission Issues
The container runs with your host user ID/GID, so file permissions should work correctly. If you encounter issues, check that the container is running with the correct user.

### Claude AI Rate Limits
The commands handle Claude AI rate limits automatically by:
- Detecting rate limit errors
- Waiting for the specified retry time
- Automatically retrying failed requests

### Container Build Issues
If the container build fails:
1. Ensure podman is installed and running
2. Check your internet connection
3. Try rebuilding: `podman build --no-cache -t dev-environment .way/docker/`

## Development

To modify way:
1. Edit files in `.way/commands/` for new commands
2. Update `.way/docker/Dockerfile` for container changes
3. Modify `.way/prompts/` for AI prompt changes
4. Test changes by rebuilding the container

## License

[Add your license information here] 