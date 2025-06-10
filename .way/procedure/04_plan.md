# Plan Phase Prompt

## Purpose
To create a detailed plan for implementing the solution, including development, testing, deployment, and monitoring phases, while adhering to the defined constraints and following implementation guidelines.

## Input
1. File: `/output/03_solution_specification.md`
   The output Markdown file from the define phase

2. File: `/input/constraints.md`
   The constraints that must be followed in the implementation

3. File: `/input/implementation_guidelines.md`
   Guidelines for implementation approach and best practices

4. File: `/input/evaluation_criteria.md`
   Criteria for evaluating the implementation

## Process
1. Review solution specification
2. Plan development tasks
3. Plan testing and validation
4. Plan deployment and infrastructure
5. Plan monitoring and maintenance
6. Sequence implementation phases
7. Allocate resources
8. Plan validation and testing
9. Ensure constraint compliance
10. Apply implementation guidelines
11. Define evaluation checkpoints

## Output
Directory: `/output/04_implementation_plan/`
A directory containing task files organized by the AI assistant based on the implementation needs. The AI assistant should:

1. Break down the implementation into discrete, independently testable tasks
2. Create a folder structure that reflects the logical organization of these tasks
3. Name files to indicate sequence and parallel execution possibilities
4. Include a README.md that provides an overview of the implementation plan

The directory structure should be:
```
04_implementation_plan/
├── README.md                           # Overview of the implementation plan
├── todo/                              # Initial tasks to be executed
├── doing/                             # Empty directory for in-progress tasks
└── done/                              # Empty directory for completed tasks
```

Each task file in the todo/ directory should follow this format:
```markdown
# Task: [Task Name]

## Purpose
[Clear description of what this task accomplishes]

## Prerequisites
- [List of tasks that must be completed before this task]
- [Any other prerequisites]

## Input
- [List of required inputs]
- [File paths or resources needed]

## Process
1. [Step 1]
2. [Step 2]
3. [Step 3]

## Output
- [Expected outputs]
- [File paths or resources produced]

## Validation
- [How to validate the task was completed successfully]
- [Test cases or verification steps]

## Resources Required
- [Compute resources]
- [Storage resources]
- [Other resources]

## Notes
- [Additional information]
- [Potential challenges]
- [Alternative approaches]
```

The README.md should contain:
```markdown
# Implementation Plan

## Rules Applied
### Cursor Rules
- [Rule Name 1]
  - Description: [Rule description]
  - Application: [How the rule was applied]
  - Impact: [Impact on planning process]
- [Rule Name 2]
  - Description: [Rule description]
  - Application: [How the rule was applied]
  - Impact: [Impact on planning process]

## Overview
[High-level description of the implementation plan]

## Task Dependencies
[Visual representation of task dependencies]

## Critical Path
[List of tasks on the critical path]

## Resource Allocation
[Resource allocation across tasks]

## Risk Management
[Key risks and mitigation strategies]

## Validation Strategy
[Overall validation approach]
```

## Notes
- Each task should be small enough for an AI assistant to complete reliably
- Tasks should be independently testable
- File naming should indicate sequence and parallel execution possibilities
- Tasks should have clear inputs and outputs
- Each task should be validated independently
- Resource requirements should be clearly specified
- Dependencies should be explicitly stated
- The todo/ directory should contain all initial tasks
- The doing/ and done/ directories should be empty initially
- Task files should be ready to be modified by the execute phase
- Document which Cursor rules were applied during planning
- Explain how each rule influenced the planning process
- Note any rule conflicts or synergies
- Follow-up questions should only be asked if additional information is required to complete the task
- Do not ask follow-up questions for clarification or discussion unless specifically requested by the user 