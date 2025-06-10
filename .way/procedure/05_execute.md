# Execute Phase Prompt

## Purpose
To implement the solution by executing the planned tasks in sequence, validating each task's completion, and ensuring the overall solution meets requirements.

## Input
1. Directory: `/output/04_implementation_plan/`
   The directory containing task files from the plan phase, organized as:
   ```
   04_implementation_plan/
   ├── README.md
   ├── todo/                           # Tasks not yet started
   ├── doing/                          # Tasks currently in progress
   └── done/                           # Completed tasks
   ```

2. File: `/input/constraints.md`
   The constraints that must be followed in the implementation

3. File: `/input/implementation_guidelines.md`
   Guidelines for implementation approach and best practices

4. File: `/input/evaluation_criteria.md`
   Criteria for evaluating the implementation

## Process
1. Read and understand the implementation plan from README.md
2. Check the todo/ directory for the next task to execute based on prerequisites
3. Move the selected task file to doing/ directory
4. Add execution start information to the task file
5. Execute the task following its process steps
6. Update the task file with progress and results
7. Validate the task's completion using its validation criteria
8. If validation passes:
   - Move the task file to done/ directory
   - Update the task file with completion status
   - Update the README.md with task completion
9. If validation fails:
   - Update the task file with failure information
   - Keep the task in doing/ directory
   - Update the README.md with failure status
10. Handle any issues or deviations
11. Ensure all tasks are completed successfully

## Output
The same directory structure as input, but with updated task files and organization:

```
04_implementation_plan/
├── README.md                           # Updated with execution progress
├── todo/                              # Remaining tasks
├── doing/                             # Tasks in progress
│   └── [task_name].md                 # Task file with execution details
└── done/                              # Completed tasks
    └── [task_name].md                 # Completed task file
```

Each task file will be modified during execution to include:
```markdown
# Task: [Task Name]

[Original task content...]

## Execution History
### Attempt [Number]
- Status: [In Progress/Completed/Failed]
- Steps Completed:
  1. [Step 1 result]
  2. [Step 2 result]
  3. [Step 3 result]
- Outputs:
  - [List of outputs produced]
  - [File paths or resources created]
- Validation Results:
  - [Validation step 1 result]
  - [Validation step 2 result]
  - [Test results]
- Issues:
  - [Any issues encountered]
  - [How they were resolved]
- Notes:
  - [Additional observations]
  - [Deviations from plan]
  - [Lessons learned]

[Previous execution attempts if any...]
```

The README.md will be updated to include:
```markdown
# Implementation Progress

## Current Status
- Tasks Completed: [Number]
- Tasks In Progress: [Number]
- Tasks Remaining: [Number]

## Recent Activity
- [Task 1]: [Status]
- [Task 2]: [Status]
...

## Critical Path Progress
[Status of tasks on critical path]

## Current Issues
[Any active issues or blockers]

## Next Tasks
[Tasks that can be started next]
```

## Notes
- Each execution of this procedure should:
  1. Find the next available task in todo/
  2. Move it to doing/ and start work
  3. Update the task file with progress
  4. Move to done/ when complete
- Task files serve as both specification and execution record
- The README.md provides a quick overview of progress
- Failed tasks remain in doing/ for retry
- All execution history is preserved in the task files
- Follow constraints and guidelines throughout execution 