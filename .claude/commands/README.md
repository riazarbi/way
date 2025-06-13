# Development Procedure

## Overview
This procedure defines the steps for developing software solutions, with built-in validation to ensure complete coverage and quality between steps.

## Procedure Flow
1. Initialize (00_init.md)
2. Search (01_search.md)
3. Select (02_select.md)
4. Define (03_define.md)
5. Plan (04_plan.md)
6. Execute (05_execute.md)
7. Validate (06_validate.md)

## Using the Validation Step
The validation step (`validate_step.md`) should be run after each main step to ensure complete coverage. Here's how to use it:

### When to Run
- After completing any main step (00-06)
- Before moving to the next step
- When reviewing or updating previous work

### How to Run
1. Identify the steps to validate:
   ```
   Step N: [Previous Step Output]
   Step N+1: [Current Step Output]
   ```

2. Run the validation procedure:
   ```
   /way/procedure/validate_step.md
   ```

3. Review the validation output:
   ```
   /output/validation/step_N_to_N+1/
   ```

4. Address any gaps or issues before proceeding

### Example Flow
```
00_init.md → validate_step.md (00_to_01) → 01_search.md
01_search.md → validate_step.md (01_to_02) → 02_select.md
02_select.md → validate_step.md (02_to_03) → 03_define.md
03_define.md → validate_step.md (03_to_04) → 04_plan.md
04_plan.md → validate_step.md (04_to_05) → 05_execute.md
05_execute.md → validate_step.md (05_to_06) → 06_validate.md
```

### Validation Output
Each validation run creates a directory structure:
```
validation/
└── step_N_to_N+1/
    ├── README.md                      # Validation overview
    ├── requirements/                   # Extracted requirements
    ├── coverage/                      # Coverage analysis
    ├── dependencies/                  # Dependency analysis
    └── recommendations/               # Improvement suggestions
```

### Using Validation Results
1. Review the validation README.md for an overview
2. Check requirements/ for any missed requirements
3. Examine coverage/ for gaps in implementation
4. Review dependencies/ for potential issues
5. Implement recommendations/ before proceeding

## Best Practices
1. Always run validation before moving to the next step
2. Address all gaps before proceeding
3. Document any accepted risks
4. Keep validation results for future reference
5. Use validation findings to improve the process

## Notes
- Validation should be independent of step implementation
- All gaps should be addressed or explicitly accepted
- Validation results should be shared with stakeholders
- Lessons learned should be incorporated into future steps
- Regular validation helps maintain quality and completeness 