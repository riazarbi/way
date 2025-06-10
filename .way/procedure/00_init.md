# Initialization Phase Prompt

## Purpose
To establish the initial state of the system and set up the foundation for the development process.

## Input
1. File: `.way/input/problem.md`
A Markdown file containing the problem description and context.

2. File: `.way/input/constraints.md` (optional)
A Markdown file containing any constraints or limitations for the project.

## Process
1. Analyze the problem description
2. Identify system boundaries
3. Document initial assumptions
4. Create system map
5. Define key components
6. Establish methodology
7. Set up working environment
8. Document initial state

## Output
File: `.way/output/00_init_state.md`
A Markdown file containing:
```markdown
# Initial State

## Rules Applied
### Cursor Rules
- [Rule Name 1]
  - Description: [Rule description]
  - Application: [How the rule was applied]
  - Impact: [Impact on initialization process]
- [Rule Name 2]
  - Description: [Rule description]
  - Application: [How the rule was applied]
  - Impact: [Impact on initialization process]

## System Understanding
### Current System Map
[ASCII diagram or description of system components and relationships]

### Key Components
- [List of key components]

### System Boundaries
- In Scope:
  - [List of in-scope items]
- Out of Scope:
  - [List of out-of-scope items]

## Methodology Application
### Selected Approach
[Description of selected methodology and its application]

### Initial Hypotheses
- [List of initial hypotheses]

## Working Environment
### Directory Structure
[Description of project directory structure]

### Required Resources
- [List of required resources]

## Next Steps
- [List of next steps]
```

## Notes
- Focus on understanding the problem domain
- Document all assumptions clearly
- Consider system boundaries carefully
- Maintain traceability to input data
- Document which Cursor rules were applied
- Explain how each rule influenced the process
- Note any rule conflicts or synergies
- Follow-up questions should only be asked if additional information is required to complete the task
- Do not ask follow-up questions for clarification or discussion unless specifically requested by the user

## AI Assistant Capabilities
The AI assistant has the following capabilities for executing the implementation plan:

1. Code Development
   - Write, modify, and debug code in multiple programming languages
   - Create new files and modify existing files
   - Implement software components and features
   - Set up development environments and infrastructure
   - Write tests and documentation

2. System Integration
   - Integrate different software components
   - Set up APIs and services
   - Configure databases and data storage
   - Implement authentication and security features
   - Set up CI/CD pipelines

3. Project Management
   - Track task progress and status
   - Document issues and resolutions
   - Coordinate implementation steps
   - Update project documentation
   - Manage dependencies and versions

4. Technical Operations
   - Execute terminal commands
   - Manage files and directories
   - Search and analyze codebases
   - Debug technical issues
   - Monitor system performance

5. Communication
   - Provide detailed progress updates
   - Explain technical decisions
   - Document implementation details
   - Coordinate with stakeholders
   - Report issues and blockers

Limitations:
- Cannot directly interact with external systems or APIs without proper configuration
- Cannot access or modify files outside the workspace
- Cannot execute commands that require elevated privileges
- Cannot make network requests without explicit configuration
- Cannot access or store sensitive information 