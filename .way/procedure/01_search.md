# Search Phase Prompt

## Purpose
To explore the solution space for a given problem through systematic observation and hypothesis formation, considering the system as a whole.

## Input
1. File: `.way/input/problem.md`
A Markdown file containing the problem description and context.

2. File: `.way/output/00_init_state.md`
The initial state from the initialization phase.

## Process
1. Analyze the problem description and context
2. Identify key system components and their relationships
3. Formulate specific, testable questions
4. Generate multiple hypotheses
5. Explore potential solutions
6. Document patterns and trends
7. Consider system-wide implications
8. Update the system map

## Output
File: `.way/output/01_search_results.md`
A Markdown file containing:
```markdown
# Search Results

## Rules Applied
### Cursor Rules
- [Rule Name 1]
  - Description: [Rule description]
  - Application: [How the rule was applied]
  - Impact: [Impact on search process]
- [Rule Name 2]
  - Description: [Rule description]
  - Application: [How the rule was applied]
  - Impact: [Impact on search process]

## Analysis
### Key Components
- [List of key components]

### Relationships
- [List of relationships between components]

### System Boundaries
[Description of system boundaries]

## Questions
- [List of specific, testable questions]

## Hypotheses
### Hypothesis 1
- **Statement**: [Hypothesis statement]
- **Rationale**: [Explanation of reasoning]
- **Testability**: [How to test this hypothesis]

### Hypothesis 2
- **Statement**: [Hypothesis statement]
- **Rationale**: [Explanation of reasoning]
- **Testability**: [How to test this hypothesis]

## Potential Solutions
### Solution 1
- **Description**: [Solution description]
- **Key Features**: 
  - [Feature 1]
  - [Feature 2]
- **System Impact**: [Impact on the system]
- **Feasibility**: [Assessment of feasibility]

### Solution 2
- **Description**: [Solution description]
- **Key Features**: 
  - [Feature 1]
  - [Feature 2]
- **System Impact**: [Impact on the system]
- **Feasibility**: [Assessment of feasibility]

## Patterns
- [List of observed patterns]

## Trends
- [List of identified trends]

## System Implications
- [List of system-wide implications]
```

## Notes
- Focus on understanding the system as a whole
- Generate multiple diverse hypotheses
- Consider both direct and indirect system impacts
- Document all assumptions and observations
- Maintain traceability to input data
- Update the system map with new findings
- Consider feedback from previous cycles if any
- Document which Cursor rules were applied during search
- Explain how each rule influenced the search process
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