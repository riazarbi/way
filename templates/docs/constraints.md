# Implementation Constraints

## Overview
These constraints define the boundaries and requirements for implementation. Understanding these limitations is crucial for successful project delivery.

## Technical Constraints

### Technology Stack
- **Programming Languages**: Must use Python, SQL, JavaScript, or TypeScript
- **Web Technologies**: Must use modern web technologies
- **Architecture**: Must be scalable and maintainable
- **Security**: Must follow security best practices
- **Deployment**: Must be cloud-native and support containerization

### Codebase Requirements
- **Size**: Minimize total lines of code
- **Dependencies**: Maximum of 5 direct dependencies
- **Libraries**: Prefer built-in language features over external libraries
- **Abstractions**: Avoid unnecessary abstractions
- **Focus**: Keep the codebase as small and focused as possible

### Dependency Management
- **Count**: Maximum of 5 direct dependencies
- **Type**: Must use only free and open source software (FOSS)
- **Compatibility**: All dependencies must be FOSS-compatible
- **Proprietary**: No proprietary or commercial software components
- **Maintenance**: Each dependency must be actively maintained
- **Stability**: Dependencies must be widely used and stable

## Resource Constraints

### Infrastructure
- **Cost**: Must be cost-effective
- **Cloud**: Must be deployable on standard cloud infrastructure
- **Dependencies**: Must have minimal external dependencies
- **Hardware**: Must run without degraded functionality on single machine with 8GB RAM

### Development Resources
- **Time**: Must be implementable within reasonable timeframe
- **Iteration**: Must allow for iterative development
- **Prototyping**: Must support rapid prototyping

## Software Licensing
- **License Type**: Must use only free and open source software
- **Compatibility**: All dependencies must be FOSS-compatible
- **Restrictions**: No proprietary or commercial software components

## Performance Constraints
- **Response Time**: < 200ms for 95% of requests
- **Throughput**: Support 1000 requests per second
- **Resource Usage**: CPU < 70%, Memory < 80%
- **Availability**: 99.9% uptime target

## Quality Constraints
- **Test Coverage**: > 80% test coverage
- **Bug Rate**: < 1% defect rate
- **Technical Debt**: < 5% of codebase
- **Error Rate**: < 0.1% error rate

## What You Cannot Do
1. **Use proprietary software** - All components must be FOSS
2. **Exceed dependency limits** - Maximum 5 direct dependencies
3. **Ignore performance targets** - Must meet defined metrics
4. **Skip testing** - Must maintain >80% test coverage
5. **Use deprecated technologies** - Must use modern web technologies
6. **Ignore security** - Must follow security best practices
7. **Create complex abstractions** - Keep code simple and focused

## What You Must Do
1. **Follow FOSS licensing** - Use only open source components
2. **Minimize code size** - Keep implementations lean
3. **Meet performance targets** - Achieve defined metrics
4. **Maintain quality** - Follow quality standards
5. **Document essentials** - Document only essential complexity
6. **Test thoroughly** - Maintain comprehensive test coverage
7. **Follow security practices** - Implement proper security measures

## Related Documentation
- **[Development Guide](development.md)** - How to work within these constraints
- **[Evaluation Criteria](evaluation.md)** - How compliance will be measured
- **[Capabilities](capabilities.md)** - What tools are available to you 