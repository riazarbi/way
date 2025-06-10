# Execute Phase Prompt

## Purpose
To implement a finite set of tasks from the implementation plan, validating each task's completion, and ensuring the tasks meet requirements while maintaining system awareness and learning. This phase is designed to be invoked multiple times until all tasks are complete.

## Input
1. Directory: `.way/output/04_implementation_plan/`
   The directory containing task files from the plan phase, organized as:
   ```
   04_implementation_plan/
   ├── README.md
   ├── todo/                           # Tasks not yet started
   ├── doing/                          # Tasks currently in progress
   └── done/                           # Completed tasks
   ```

2. File: `.way/input/constraints.md`
   The constraints that must be followed in the implementation

3. File: `.way/input/implementation_guidelines.md`
   Guidelines for implementation approach and best practices

4. File: `.way/input/evaluation_criteria.md`
   Criteria for evaluating the implementation

5. File: `.way/output/00_init_state.md`
   The initial state from the initialization phase

6. File: `.way/output/06_validation_results.md` (if exists)
   Results from previous cycle's validation phase

7. File: `.way/output/05_execution_results.md` (if exists)
   Results from previous execution invocations

## Process
1. Read and understand the implementation plan from README.md
2. Review previous cycle learnings if available
3. Review previous execution results if available
4. Select a finite set of tasks to execute in this invocation:
   - Choose tasks that are ready (prerequisites met)
   - Consider system impact and dependencies
   - Limit the number of tasks based on complexity
5. For each selected task:
   a. Move the task file to doing/ directory
   b. Add execution start information to the task file
   c. Execute the task following its process steps
   d. Update the task file with progress and results
   e. Validate the task's completion using its validation criteria
   f. If validation passes:
      - Move the task file to done/ directory
      - Update the task file with completion status
      - Update the README.md with task completion
      - Update the system map with task results
   g. If validation fails:
      - Update the task file with failure information
      - Keep the task in doing/ directory
      - Update the README.md with failure status
      - Document learnings from the failure
6. Handle any issues or deviations
7. Document learnings and observations
8. Prepare feedback for the next invocation
9. Determine if more tasks need to be executed

## Output
1. Updated Directory: `.way/output/04_implementation_plan/`
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

2. File: `.way/output/05_execution_results.md`
   A Markdown file containing:
   ```markdown
   # Execution Results

   ## Rules Applied
   ### Cursor Rules
   - [Rule Name 1]
     - Description: [Rule description]
     - Application: [How the rule was applied]
     - Impact: [Impact on execution]
   - [Rule Name 2]
     - Description: [Rule description]
     - Application: [How the rule was applied]
     - Impact: [Impact on execution]

   ## Current Invocation Summary
   ### Tasks Executed
   - [Task 1]
     - Status: [Completed/Failed]
     - Key Results: [Results summary]
     - System Impact: [Impact on system]
     - Learnings: [Key learnings]

   ## Overall Progress
   ### Task Status
   - Total Tasks: [Number]
   - Completed: [Number]
   - In Progress: [Number]
   - Remaining: [Number]
   - Failed: [Number]

   ### System Map Updates
   ### New Components
   - [Component 1]
   - [Component 2]

   ### Modified Components
   - [Component 1]: [Changes]
   - [Component 2]: [Changes]

   ### Removed Components
   - [Component 1]
   - [Component 2]

   ## Learnings
   ### What Worked Well
   - [Learning 1]
   - [Learning 2]

   ### What Could Be Improved
   - [Improvement 1]
   - [Improvement 2]

   ### Unexpected Findings
   - [Finding 1]
   - [Finding 2]

   ## Next Invocation
   ### Tasks Ready for Execution
   - [Task 1]
     - Prerequisites: [List of prerequisites]
     - Expected Impact: [Impact on system]
   - [Task 2]
     - Prerequisites: [List of prerequisites]
     - Expected Impact: [Impact on system]

   ### System State
   - [State 1]
   - [State 2]

   ### Recommendations
   - [Recommendation 1]
   - [Recommendation 2]

   ## Completion Status
   - All Tasks Complete: [Yes/No]
   - Ready for Next Invocation: [Yes/No]
   - Blockers: [List of any blockers]
   ```

## Notes
- Each invocation should:
  1. Select a manageable set of tasks to execute
  2. Complete those tasks or document why they couldn't be completed
  3. Update the system map and documentation
  4. Prepare for the next invocation
- Task files serve as both specification and execution record
- The README.md provides a quick overview of progress
- Failed tasks remain in doing/ for retry
- All execution history is preserved in the task files
- Follow constraints and guidelines throughout execution
- Update the system map with each task's results
- Document learnings and observations
- Prepare feedback for the next invocation
- Consider previous cycle learnings
- Maintain awareness of the whole system
- Clear entry and exit conditions for each invocation
- Document which Cursor rules were applied during execution
- Explain how each rule influenced the execution process
- Note any rule conflicts or synergies 