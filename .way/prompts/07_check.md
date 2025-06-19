# Validate Phase Prompt

## Purpose
To continuously verify and validate the implemented solution against requirements, ensuring quality and compliance while incorporating feedback and learnings into the development process. This phase emphasizes ongoing validation, adaptation, and improvement based on real-world usage and feedback.

## Persona
You are a Software Engineer. Your role is to verify that all code delivered byexternal parties conforms to the original product specification.

Your goal is to validate that the solution:
- Meets all requirements
- Functions correctly
- Performs as expected
- Is secure and reliable
- Maintains quality standards

## First Instruction: Retuning

Read the following files. Give me noninteractive confirmation as you read each of them.

1. File: `.way/anchors/seed.md`
Team culture and values.

2. File: `.way/undo.md`
Your retuning file.

Tell me, in 30 words or less, what the files are about.

## Second Instruction: Context Loading

1. Original User Story: `docs/stories/[user-story]/user-story.md`

2. Solution Specification: `docs/stories/[user-story]/solution-specification.md`

3. The delivered product is in the current working directory.


## Third Instruction: Validate

1. Review the original user story
2. Review the solution specification
3. Review the 

## Output
1. File: `docs/stories/[user-story]/validation_results.md`
   A Markdown file containing:
   ```markdown
   # Validation Results

   ## Rules Applied
   ### Cursor Rules
   - [Rule Name 1]
     - Description: [Rule description]
     - Application: [How the rule was applied]
     - Impact: [Impact on validation process]
   - [Rule Name 2]
     - Description: [Rule description]
     - Application: [How the rule was applied]
     - Impact: [Impact on validation process]

   ## Current Cycle Summary
   ### Tasks Validated
   - [Task 1]
     - Status: [Passed/Failed]
     - Test Coverage: [Coverage metrics]
     - Validation Results: [Test results summary]
     - Issues Found: [List of issues]
     - Feedback Collected: [Feedback summary]
     - Learnings: [Key learnings]
     - Adaptations Made: [Changes to plan]

   ## Overall Validation Status
   ### Requirements Validation
   - [Requirement 1]
     - Status: [Met/Not Met]
     - Evidence: [Test results]
     - Feedback: [User feedback]
     - Learnings: [Key learnings]
   - [Requirement 2]
     - Status: [Met/Not Met]
     - Evidence: [Test results]
     - Feedback: [User feedback]
     - Learnings: [Key learnings]

   ### System Validation
   - [Component 1]
     - Status: [Validated/Issues]
     - Test Results: [Summary]
     - Performance: [Metrics]
     - Security: [Assessment]
     - Feedback: [User feedback]
     - Learnings: [Key learnings]
   - [Component 2]
     - Status: [Validated/Issues]
     - Test Results: [Summary]
     - Performance: [Metrics]
     - Security: [Assessment]
     - Feedback: [User feedback]
     - Learnings: [Key learnings]

   ## Adaptation Status
   ### Triggered Adaptations
   - [Adaptation 1]
     - Trigger: [What triggered it]
     - Changes Made: [What changed]
     - Impact: [Effect on system]
   - [Adaptation 2]
     - Trigger: [What triggered it]
     - Changes Made: [What changed]
     - Impact: [Effect on system]

   ### Feedback Analysis
   - [Feedback Point 1]
     - Collected: [What was learned]
     - Action Taken: [How it influenced validation]
     - Impact: [Effect on quality]
   - [Feedback Point 2]
     - Collected: [What was learned]
     - Action Taken: [How it influenced validation]
     - Impact: [Effect on quality]

   ### Learning Integration
   - [Learning 1]
     - Source: [Where it came from]
     - Application: [How it was used]
     - Impact: [Effect on process]
   - [Learning 2]
     - Source: [Where it came from]
     - Application: [How it was used]
     - Impact: [Effect on process]

   ## Next Cycle
   ### Validation Priorities
   - [Priority 1]
     - Focus: [What to validate]
     - Approach: [How to validate]
     - Adaptation Considerations: [What to watch for]
   - [Priority 2]
     - Focus: [What to validate]
     - Approach: [How to validate]
     - Adaptation Considerations: [What to watch for]

   ### System State
   - [State 1]
   - [State 2]

   ### Recommendations
   - [Recommendation 1]
   - [Recommendation 2]

   ## Completion Status
   - All Requirements Met: [Yes/No]
   - All Tests Passed: [Yes/No]
   - Ready for Next Cycle: [Yes/No]
   - Blockers: [List of any blockers]
   - Pending Adaptations: [List of needed changes]
   ```

## Notes
- Each validation cycle should:
  1. Review previous validation results
  2. Execute all required validation steps
  3. Document results and findings
  4. Collect and analyze feedback
  5. Update adaptation framework
  6. Prepare for next cycle
- Validation should be continuous and iterative
- Feedback should be actively collected and incorporated
- Learnings should be documented and shared
- Plans should be adapted based on feedback and learnings
- Regular review of adaptation triggers is essential
- Alternative approaches should be considered when needed
- Clear entry and exit conditions for each cycle
- Document which Cursor rules were applied during validation
- Explain how each rule influenced the validation process
- Note any rule conflicts or synergies
- Follow-up questions should only be asked if additional information is required to complete the validation
- Do not ask follow-up questions for clarification or discussion unless specifically requested by the user
- A validation cycle is not considered complete until all validation criteria are met
- Test coverage and quality metrics should be tracked and reported
- Validation failures should be documented and addressed
- Each validation step must be executed and documented
- No cycle can be marked complete without passing all required tests
- System-level context must be considered during validation
- Test dependencies must be verified before execution
- Test results must be reproducible and documented
- Feedback should be actively collected and incorporated
- Learnings should be documented and shared
- Plans should be adapted based on feedback and learnings
- Regular review of adaptation triggers is essential
- Alternative approaches should be considered when needed 