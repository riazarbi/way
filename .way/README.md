# Way Prompt System

This directory contains the prompt system that guides the development process of the task management system. The system is organized into several key components that work together to maintain context, enforce rules, and track progress.

## Directory Structure

### Root Files
- `README.md` - This file, explaining the prompt system
- `seed.md` - Contains the core principles and commitments of the human engineer to the AI agent
- `undo.md` - Personal retuning file for the AI agent to maintain context across prompts. Owned by the AI agent.
- `unified_methodology.md` - Defines the problem-solving approach and methodology

### Folders
- `input/` - Contains input files that define constraints and guidelines
  - `constraints.md` - Technical and architectural constraints
  - `implementation_guidelines.md` - Development guidelines and best practices

- `output/` - Contains the results of each phase of development
  - `00_init_state.md` - Initial system understanding and requirements
  - `01_search_results.md` - Results of initial technology search
  - `02_technology_selection.md` - Selected technology stack and rationale
  - `03_solution_specification.md` - Detailed solution architecture
  - `04_implementation_plan/` - Implementation tasks and progress tracking
    - `todo/` - Tasks not yet started
    - `doing/` - Tasks currently in progress
    - `check/` - Tasks ready for validation
    - `done/` - Completed tasks

- `procedure/` - Contains templates and procedures for each phase
  - `00_init.md` - Initialization procedure
  - `01_search.md` - Technology search procedure
  - `02_select.md` - Technology selection procedure
  - `03_define.md` - Solution definition procedure
  - `04_plan.md` - Implementation planning procedure

- `validation/` - Contains validation results between phases
  - `step_01_to_02/` - Validation between init and search
  - `step_02_to_03/` - Validation between search and select
  - `step_03_to_04/` - Validation between define and plan

- `system/` - Contains system-level files
  - `unified_methodology_simple.md` - Simplified version of the methodology

## How It Works

1. **Initialization**
   - The system starts with `seed.md` which establishes the core principles
   - `undo.md` allows the AI to maintain context across prompts
   - `unified_methodology.md` provides the problem-solving framework

2. **Development Phases**
   - Each phase follows a procedure from the `procedure/` directory
   - Input files from `input/` guide the development
   - Output is stored in `output/` with phase-specific files
   - Validation between phases is stored in `validation/`

3. **Implementation Tracking**
   - Tasks are organized in `04_implementation_plan/`
   - Tasks move through states: todo → doing → check → done
   - Each task has clear acceptance criteria and validation steps

4. **Context Maintenance**
   - The AI agent uses `undo.md` to maintain context
   - Each prompt includes relevant files from the `.way` directory
   - The system ensures consistent application of rules and methodology

## Key Principles

1. **System Thinking**
   - Understand the system as a whole
   - Recognize interdependencies between components
   - Consider the impact of changes across the system
   - Maintain awareness of system boundaries

2. **Methodical Problem Solving**
   - Break down complex problems into manageable steps
   - Follow a structured approach to solution development
   - Validate each step before proceeding
   - Document decisions and rationale

3. **Context Preservation**
   - Maintain system context across sessions
   - Track the evolution of understanding
   - Preserve decision-making history
   - Enable consistent application of rules

4. **Continuous Validation**
   - Validate understanding at each step
   - Verify alignment with system goals
   - Ensure quality and consistency
   - Document validation results

5. **Clear Boundaries**
   - Define system scope explicitly
   - Identify what's in and out of scope
   - Maintain clear interfaces between components
   - Document system constraints

## Usage

1. Each development session starts with the relevant files from `.way/`
2. The AI agent maintains context through `undo.md`
3. Tasks are tracked through the implementation plan
4. Validation ensures quality at each step
5. Documentation is maintained throughout the process

This system ensures a structured, maintainable, and high-quality development process while maintaining context and consistency across sessions.

