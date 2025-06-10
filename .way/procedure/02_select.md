# Select Phase Prompt

## Purpose
To evaluate potential implementation approaches and select the optimal solution that best fits the problem requirements while considering the AI assistant's capabilities and defined constraints.

## Input
1. File: `/output/01_search_results.json`
   The output JSON file from the search phase

2. File: `/input/constraints.md`
   The constraints that must be followed in the implementation

3. File: `/input/implementation_guidelines.md`
   Guidelines for implementation approach and best practices

4. File: `/input/evaluation_criteria.md`
   Criteria for evaluating potential solutions

## Process
1. Review and validate search phase outputs
2. Evaluate implementation approaches against constraints
3. Assess implementation complexity and feasibility
4. Compare performance characteristics using evaluation criteria
5. Evaluate resource requirements
6. Consider maintainability using implementation guidelines
7. Assess integration requirements
8. Select optimal implementation approach

## Output
File: `/output/02_selected_solution.md`
A Markdown file containing:
```markdown
# Selected Solution Report

## Evaluation

### Approach Analysis
#### Solution [ID]
- **Approach Type**: [Type of approach]
- **Architecture**: [Architecture description]
- **Performance Metrics**
  - Efficiency: [Efficiency assessment]
  - Reliability: [Reliability assessment]
  - Maintainability: [Maintainability assessment]
- **Implementation Requirements**
  - Complexity: [Complexity assessment]
  - Resources: [Resource requirements]
- **Constraint Compliance**
  [Results of validation against constraints.md]

### Implementation Analysis
#### Solution [ID]
- **Complexity**: [Complexity assessment]
- **Maintenance Effort**: [Effort assessment]
- **Integration Points**:
  - [Integration point 1]
  - [Integration point 2]
- **Guideline Compliance**
  [Results of validation against implementation_guidelines.md]

### Resource Requirements
#### Solution [ID]
- **Compute Resources**
  - Type: [Resource type]
  - Specifications: [Resource specifications]
- **Storage Requirements**: [Storage needs]
- **Network Requirements**: [Network needs]

### Maintainability Analysis
#### Solution [ID]
- **Code Quality**: [Quality assessment]
- **Documentation Needs**: [Documentation requirements]
- **Update Frequency**: [Update schedule]

### Evaluation Metrics
#### Solution [ID]
- **Code Metrics**
  - Size: [Size metrics]
  - Complexity: [Complexity metrics]
  - Quality: [Quality metrics]
- **Performance Metrics**
  - Application: [Application performance]
  - User Experience: [UX assessment]
- **Maintenance Metrics**
  - Development: [Development metrics]
  - Operational: [Operational metrics]

## Selected Solution
- **ID**: [Solution identifier]
- **Description**: [Solution description]
- **Implementation Approach**: [Approach description]
- **Key Features**:
  - [Feature 1]
  - [Feature 2]
- **Expected Performance**
  - Metrics:
    - [Metric 1]
    - [Metric 2]
  - Targets:
    - [Target 1]
    - [Target 2]
- **Resource Requirements**
  - Development: [Development requirements]
  - Deployment: [Deployment requirements]
  - Maintenance: [Maintenance requirements]
- **Constraint Compliance**
  [Results of validation against constraints.md]

## Rejected Solutions
### Solution [ID]
- **Reason**: [Rejection reason]
- **Potential Improvements**:
  - [Improvement 1]
  - [Improvement 2]
- **Constraint Violations**:
  [Results of validation against constraints.md]
```

## Notes
- All solutions must comply with the constraints defined in constraints.md
- Implementation approaches should follow the guidelines in implementation_guidelines.md
- Solutions should be evaluated against the criteria in evaluation_criteria.md
- Focus on implementation approaches within AI capabilities
- Consider performance and resource requirements
- Evaluate maintainability and integration needs
- Document clear performance targets
- Consider development and deployment complexity 