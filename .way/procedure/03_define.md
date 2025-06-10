# Define Phase Prompt

## Purpose
To create a detailed specification for the selected implementation, including architecture, components, and deployment specifications, while adhering to the defined constraints and following implementation guidelines.

## Input
1. File: `/output/02_selected_solution.md`
   The output Markdown file from the select phase

2. File: `/input/constraints.md`
   The constraints that must be followed in the implementation

3. File: `/input/implementation_guidelines.md`
   Guidelines for implementation approach and best practices

4. File: `/input/evaluation_criteria.md`
   Criteria for evaluating the implementation

## Process
1. Review selected solution details
2. Define system architecture and components
3. Specify implementation requirements
4. Detail deployment architecture
5. Define monitoring requirements
6. Establish performance metrics
7. Document integration specifications
8. Ensure compliance with constraints
9. Apply implementation guidelines
10. Define evaluation criteria

## Output
File: `/output/03_solution_specification.md`
A Markdown file containing:
```markdown
# Solution Specification

## Rules Applied
### Cursor Rules
- [Rule Name 1]
  - Description: [Rule description]
  - Application: [How the rule was applied]
  - Impact: [Impact on definition process]
- [Rule Name 2]
  - Description: [Rule description]
  - Application: [How the rule was applied]
  - Impact: [Impact on definition process]

## System Architecture
### Type
[Architecture type]

### Components
#### Component [ID]
- **Name**: [Component name]
- **Type**: [Component type]
- **Description**: [Component description]
- **Parameters**:
  - [Parameter name]: [Parameter value] - [Parameter description]
- **Constraint Compliance**:
  [Results of validation against constraints.md]

### Data Flow
- **From**: [Source component]
- **To**: [Target component]
- **Transformation**: [Transformation description]

## Implementation Specification
### Requirements
#### Code
- **Language**: [Programming language]
- **Frameworks**:
  - [Framework 1]
  - [Framework 2]
- **Dependencies**:
  - [Dependency 1]
  - [Dependency 2]
- **Constraint Compliance**:
  [Results of validation against constraints.md]

#### Data
- **Format**: [Data format]
- **Storage**: [Storage requirements]
- **Processing**: [Processing requirements]

### Development Methodology
- **Approach**: [Development approach]
- **Tools**:
  - [Tool 1]
  - [Tool 2]
- **Testing Strategy**: [Testing approach]
- **Guideline Compliance**:
  [Results of validation against implementation_guidelines.md]

### Resource Requirements
- **Compute**:
  - Type: [Compute type]
  - Specifications: [Compute specifications]
- **Storage**: [Storage requirements]
- **Network**: [Network requirements]

## Deployment Architecture
### Infrastructure
- **Compute**:
  - Type: [Compute type]
  - Specifications: [Compute specifications]
- **Storage**: [Storage configuration]
- **Network**: [Network configuration]

### Scaling Configuration
- **Horizontal**: [Horizontal scaling details]
- **Vertical**: [Vertical scaling details]

### Monitoring
- **Metrics**:
  - [Metric 1]
  - [Metric 2]
- **Alerts**:
  - [Alert 1]
  - [Alert 2]
- **Logging**: [Logging configuration]

## Performance Requirements
### Metrics
#### Metric [Name]
- **Target**: [Target value]
- **Measurement Method**: [Measurement approach]
- **Evaluation Criteria**: [Evaluation method]

### SLAs
#### SLA [Metric]
- **Threshold**: [Threshold value]
- **Consequence**: [Consequence description]

## Integration Specifications
### Interface [Name]
- **Protocol**: [Protocol details]
- **Data Format**: [Format specification]
- **Authentication**: [Authentication method]
- **Rate Limits**: [Rate limiting details]

## Validation Plan
### Functional Testing
- **Test Cases**:
  - [Test case 1]
  - [Test case 2]
- **Acceptance Criteria**:
  - [Criterion 1]
  - [Criterion 2]
- **Edge Cases**:
  - [Edge case 1]
  - [Edge case 2]

### Integration Testing
#### Test Case [ID]
- **Description**: [Test description]
- **Test Steps**:
  - [Step 1]
  - [Step 2]
- **Expected Results**:
  - [Result 1]
  - [Result 2]

### Performance Testing
- **Load Tests**:
  - [Load test 1]
  - [Load test 2]
- **Stress Tests**:
  - [Stress test 1]
  - [Stress test 2]
- **Scalability Tests**:
  - [Scalability test 1]
  - [Scalability test 2]

### Constraint Validation
[Results of validation against constraints.md]
```

## Notes
- Ensure all specifications are clear and implementable
- Document all implementation requirements
- Include detailed deployment specifications
- Define clear performance metrics
- Consider monitoring requirements
- Document all integration points
- All components must comply with constraints.md
- Implementation must follow guidelines in implementation_guidelines.md
- Performance metrics must align with evaluation_criteria.md
- Document which Cursor rules were applied during definition
- Explain how each rule influenced the definition process
- Note any rule conflicts or synergies
- Follow-up questions should only be asked if additional information is required to complete the task
- Do not ask follow-up questions for clarification or discussion unless specifically requested by the user 