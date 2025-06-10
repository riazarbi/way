# Validate Phase Prompt

## Purpose
To validate the implemented solution through comprehensive testing, performance evaluation, and quality assessment, ensuring it effectively solves the original problem while meeting all constraints and following implementation guidelines.

## Input
1. Directory: `/output/04_implementation_plan/`
   The directory containing task files and execution results:
   ```
   04_implementation_plan/
   ├── README.md
   ├── todo/                           # Remaining tasks
   ├── doing/                          # Tasks in progress
   └── done/                           # Completed tasks with execution history
   ```

2. File: `/input/constraints.md`
   The constraints that must be followed in the implementation

3. File: `/input/implementation_guidelines.md`
   Guidelines for implementation approach and best practices

4. File: `/input/evaluation_criteria.md`
   Criteria for evaluating the implementation

## Process
1. Review all completed tasks in the done/ directory
2. Analyze task execution history and validation results
3. Validate functionality against requirements
4. Assess code quality and implementation approach
5. Test against edge cases
6. Evaluate system performance
7. Analyze resource utilization
8. Assess scalability
9. Monitor system health
10. Document validation results
11. Validate constraint compliance
12. Assess guideline adherence
13. Apply evaluation criteria

## Output
File: `/output/06_validation_results.md`
A Markdown file containing:
```markdown
# Validation Results

## Task Validation
### Completed Tasks
- [Task 1]
  - Status: [Passed/Failed]
  - Validation Results: [Results from task execution]
  - Issues Found: [Any issues discovered]
  - Recommendations: [Improvement suggestions]

- [Task 2]
  - Status: [Passed/Failed]
  - Validation Results: [Results from task execution]
  - Issues Found: [Any issues discovered]
  - Recommendations: [Improvement suggestions]

### Task Dependencies
- [List of task dependencies and their validation status]
- [Any dependency-related issues]

## Functional Validation
### Test Results
- [Test 1]
  - Description: [Test description]
  - Status: [Passed/Failed]
  - Expected: [Expected result]
  - Actual: [Actual result]

- [Test 2]
  - Description: [Test description]
  - Status: [Passed/Failed]
  - Expected: [Expected result]
  - Actual: [Actual result]

### Edge Cases
- [Edge Case 1]
  - Description: [Case description]
  - Input: [Test input]
  - Expected Output: [Expected result]
  - Actual Output: [Actual result]
  - Status: [Passed/Failed]

## Code Quality
### Metrics
- [Metric 1]: [Value] ([Status])
- [Metric 2]: [Value] ([Status])

### Recommendations
- [List of code quality improvements]

## System Validation
### Performance
- Response Time: [Results]
- Throughput: [Results]
- Resource Utilization: [Results]

### Scalability
- Horizontal Scaling: [Results]
- Vertical Scaling: [Results]

### Reliability
- Uptime: [Results]
- Error Rates: [Results]
- Recovery Time: [Results]

## Constraint Compliance
[Results of validation against constraints.md]

## Guideline Compliance
[Results of validation against implementation_guidelines.md]

## System Health
### Health Metrics
- [Metric 1]: [Value] ([Status])
- [Metric 2]: [Value] ([Status])

### Data Quality
- [Metric 1]: [Value] ([Status])
- [Metric 2]: [Value] ([Status])

## Validation Summary
### Overall Status
[Pass/Fail/Partial]

### Key Findings
- [Finding 1]
- [Finding 2]

### Critical Issues
- [Issue 1]
  - Description: [Issue description]
  - Impact: [Impact assessment]
  - Recommendation: [Suggested fix]
  - Constraint Impact: [Impact on constraints]

### Improvement Opportunities
- [Opportunity 1]
  - Area: [Area for improvement]
  - Current State: [Current state]
  - Target State: [Desired state]
  - Recommendation: [Suggested improvement]
  - Guideline Relation: [Related guidelines]

### Next Steps
- [Step 1]
- [Step 2]
```

## Notes
- Review all completed tasks in the done/ directory
- Validate each task's execution history and results
- Ensure comprehensive functional validation
- Assess code quality thoroughly
- Test against edge cases
- Monitor system performance and health
- Evaluate scalability and reliability
- Document all findings and recommendations
- Maintain quality standards throughout
- Validate all constraints from constraints.md
- Assess adherence to implementation_guidelines.md
- Apply evaluation criteria from evaluation_criteria.md 