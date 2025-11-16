# CLAUDE.md - AI Assistant Guide for Digital-twin Project

## Project Overview

**Digital-twin** is a project focused on creating digital twin implementations. This repository is designed to support the development of digital twin systems that provide virtual representations of physical assets, processes, or systems.

### Purpose
- Create accurate virtual representations of physical entities
- Enable real-time monitoring, simulation, and analysis
- Support predictive maintenance and optimization workflows
- Facilitate data-driven decision making

## Repository Structure

```
Digital-twin/
├── .git/                   # Git version control
├── CLAUDE.md              # This file - AI assistant guidelines
├── README.md              # Project documentation (to be created)
├── src/                   # Source code (to be created)
│   ├── core/             # Core digital twin engine
│   ├── models/           # Data models and schemas
│   ├── services/         # Business logic and services
│   ├── api/              # API endpoints
│   └── utils/            # Utility functions
├── tests/                 # Test suites
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   └── e2e/              # End-to-end tests
├── docs/                  # Additional documentation
├── config/                # Configuration files
├── scripts/               # Build and deployment scripts
└── examples/              # Example implementations
```

## Technology Stack

### Expected Technologies (To be determined)
- **Backend**: Node.js, Python, or other suitable runtime
- **Database**: PostgreSQL, MongoDB, or time-series database (InfluxDB, TimescaleDB)
- **Real-time Communication**: WebSockets, MQTT, or similar
- **Data Processing**: Stream processing frameworks (Apache Kafka, RabbitMQ)
- **API**: REST or GraphQL
- **Testing**: Jest, Pytest, or framework-specific testing tools
- **DevOps**: Docker, Kubernetes (as needed)

## Development Workflow

### Branch Strategy

1. **Main Branch**: `main` or `master`
   - Production-ready code only
   - Protected branch with required reviews
   - All changes via pull requests

2. **Development Branches**: `claude/*` or `feature/*`
   - Feature development happens here
   - Branch naming: `claude/feature-description-sessionid` or `feature/descriptive-name`
   - Always create from latest main branch

3. **Hotfix Branches**: `hotfix/*`
   - Critical bug fixes
   - Merged directly to main and development branches

### Commit Guidelines

Follow conventional commit format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `perf`: Performance improvements

**Examples**:
```
feat(models): add sensor data model for temperature readings
fix(api): resolve null pointer exception in telemetry endpoint
docs(readme): update installation instructions
```

### Pull Request Process

1. **Create PR** from your feature branch to main
2. **Title**: Clear, descriptive summary of changes
3. **Description**: Include:
   - Summary of changes (2-3 bullet points)
   - Test plan checklist
   - Related issues/tickets
   - Breaking changes (if any)
4. **Review**: Wait for code review approval
5. **Merge**: Squash and merge after approval

## Code Conventions

### General Principles

1. **SOLID Principles**: Follow Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, and Dependency Inversion
2. **DRY**: Don't Repeat Yourself - extract common logic
3. **KISS**: Keep It Simple, Stupid - avoid over-engineering
4. **YAGNI**: You Aren't Gonna Need It - don't add unnecessary features

### Code Style

1. **Naming Conventions**:
   - Variables/Functions: `camelCase` (JavaScript/TypeScript) or `snake_case` (Python)
   - Classes: `PascalCase`
   - Constants: `UPPER_SNAKE_CASE`
   - Files: `kebab-case.ext` or `snake_case.ext`

2. **Code Organization**:
   - One class per file (when possible)
   - Group related functions together
   - Import statements at the top
   - Export statements at the bottom (or use named exports inline)

3. **Comments**:
   - Use JSDoc/docstrings for public APIs
   - Explain "why" not "what"
   - Keep comments up-to-date with code changes

4. **Error Handling**:
   - Always handle errors explicitly
   - Use custom error classes for domain-specific errors
   - Log errors with appropriate context
   - Never swallow exceptions silently

### Security Best Practices

1. **Input Validation**: Validate and sanitize all user inputs
2. **Authentication**: Implement proper authentication mechanisms
3. **Authorization**: Check permissions before allowing actions
4. **Data Protection**: Encrypt sensitive data at rest and in transit
5. **Dependencies**: Keep dependencies updated and audit regularly
6. **Secrets**: Never commit secrets, API keys, or credentials
   - Use environment variables
   - Use `.env` files (add to `.gitignore`)
   - Use secret management tools in production

## Digital Twin Specific Guidelines

### Data Model Design

1. **Physical Asset Representation**:
   - Create clear models for physical entities
   - Include metadata (location, type, manufacturer, etc.)
   - Version your models for schema evolution

2. **Sensor Data**:
   - Use appropriate data types for measurements
   - Include timestamps (prefer UTC)
   - Store units of measurement explicitly
   - Consider data retention policies

3. **State Management**:
   - Track both current state and historical states
   - Implement state transition validation
   - Log state changes for audit trails

### Real-time Data Handling

1. **Streaming Data**:
   - Handle high-frequency sensor data efficiently
   - Implement buffering and batching strategies
   - Use appropriate message queues

2. **Data Quality**:
   - Validate sensor data ranges
   - Handle missing or corrupted data gracefully
   - Implement outlier detection

3. **Synchronization**:
   - Keep digital twin in sync with physical asset
   - Handle network interruptions gracefully
   - Implement reconciliation mechanisms

### Simulation and Analytics

1. **Predictive Models**:
   - Document model assumptions and limitations
   - Version control model artifacts
   - Track model performance metrics

2. **Simulation**:
   - Provide clear APIs for running simulations
   - Allow parameterization of scenarios
   - Return results in standardized formats

## Testing Strategy

### Test Coverage Requirements

- **Unit Tests**: 80%+ coverage for core logic
- **Integration Tests**: Cover all API endpoints
- **E2E Tests**: Cover critical user workflows

### Test Organization

1. **Test Files**: Place tests alongside source code or in `tests/` directory
2. **Test Naming**: `describe` blocks for components, `it`/`test` for behaviors
3. **Test Data**: Use factories or fixtures for test data
4. **Mocking**: Mock external dependencies appropriately

### Testing Best Practices

1. **Isolation**: Each test should be independent
2. **AAA Pattern**: Arrange, Act, Assert
3. **Edge Cases**: Test boundary conditions
4. **Error Cases**: Test error handling paths
5. **Performance**: Include performance tests for critical paths

## AI Assistant Specific Guidelines

### When Working on This Repository

1. **Understand Context First**:
   - Read relevant code before making changes
   - Check existing patterns and conventions
   - Review recent commits for context

2. **Use TodoWrite Tool**:
   - Always create a todo list for multi-step tasks
   - Mark tasks as in_progress before starting
   - Mark tasks as completed immediately after finishing

3. **Code Quality**:
   - Write clean, readable code
   - Add appropriate comments for complex logic
   - Follow existing code style in the repository
   - Run tests before committing

4. **Security Awareness**:
   - Never introduce security vulnerabilities (SQL injection, XSS, command injection, etc.)
   - Validate inputs properly
   - Use parameterized queries
   - Sanitize outputs

5. **Git Operations**:
   - Always develop on the designated `claude/*` branch
   - Use descriptive commit messages
   - Push changes after completing tasks
   - Use `git push -u origin <branch-name>` for new branches

6. **Communication**:
   - Provide concise, technical responses
   - Explain what you're doing and why
   - Ask for clarification when requirements are ambiguous
   - Report errors and blockers clearly

### Common Tasks

#### Adding a New Feature

1. Create todo list for the feature
2. Review existing code structure
3. Design the implementation
4. Write tests first (TDD approach)
5. Implement the feature
6. Run all tests
7. Commit and push changes
8. Create pull request with comprehensive description

#### Fixing a Bug

1. Reproduce the bug
2. Write a failing test that exposes the bug
3. Fix the bug
4. Verify the test passes
5. Check for similar issues elsewhere
6. Commit and push changes

#### Refactoring Code

1. Ensure existing tests pass
2. Make incremental changes
3. Run tests after each change
4. Maintain backward compatibility (or document breaking changes)
5. Update documentation if needed
6. Commit and push changes

## Configuration Management

### Environment Variables

Use `.env` files for local development:

```env
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=digital_twin
DB_USER=user
DB_PASSWORD=password

# API
API_PORT=3000
API_HOST=0.0.0.0

# External Services
MQTT_BROKER_URL=mqtt://localhost:1883
MQTT_USERNAME=user
MQTT_PASSWORD=password
```

**Important**: Always add `.env` to `.gitignore`

### Configuration Files

1. **package.json** (Node.js) / **pyproject.toml** (Python): Dependencies and scripts
2. **.gitignore**: Exclude build artifacts, dependencies, secrets
3. **tsconfig.json** (TypeScript): Compiler options
4. **.eslintrc** / **.pylintrc**: Linting rules
5. **.prettierrc**: Code formatting rules
6. **docker-compose.yml**: Local development environment

## Documentation Standards

### Code Documentation

1. **README.md**: Project overview, setup instructions, usage examples
2. **API Documentation**: OpenAPI/Swagger or similar
3. **Architecture Docs**: System design, data flow diagrams
4. **Inline Comments**: Complex algorithms, business logic

### Documentation Updates

- Update docs when changing functionality
- Keep examples up-to-date
- Document breaking changes clearly
- Maintain changelog for releases

## Continuous Integration / Continuous Deployment

### CI/CD Pipeline (To be implemented)

1. **On Pull Request**:
   - Run linting
   - Run all tests
   - Check test coverage
   - Build the project
   - Run security scans

2. **On Merge to Main**:
   - Run full test suite
   - Build production artifacts
   - Deploy to staging environment
   - Run smoke tests

3. **On Release Tag**:
   - Deploy to production
   - Generate release notes
   - Update documentation

## Performance Considerations

1. **Database Queries**:
   - Use indexes appropriately
   - Avoid N+1 queries
   - Use pagination for large datasets
   - Consider caching strategies

2. **API Design**:
   - Implement rate limiting
   - Use appropriate HTTP caching headers
   - Support pagination, filtering, and sorting
   - Return only necessary data

3. **Real-time Processing**:
   - Use efficient data structures
   - Consider time-series optimizations
   - Implement backpressure handling
   - Monitor resource usage

## Monitoring and Observability

### Logging

1. **Log Levels**: DEBUG, INFO, WARN, ERROR, FATAL
2. **Structured Logging**: Use JSON format for production
3. **Context**: Include request IDs, user IDs, timestamps
4. **Sensitive Data**: Never log passwords, tokens, or PII

### Metrics

1. **Application Metrics**: Request rates, response times, error rates
2. **Business Metrics**: Twin synchronization status, prediction accuracy
3. **Infrastructure Metrics**: CPU, memory, disk, network usage

### Tracing

1. Implement distributed tracing for complex workflows
2. Track request flow across services
3. Identify performance bottlenecks

## Troubleshooting Guide

### Common Issues

1. **Build Failures**:
   - Check dependency versions
   - Clear node_modules/cache and reinstall
   - Verify environment variables

2. **Test Failures**:
   - Check for test isolation issues
   - Verify test data setup
   - Check for timing issues in async tests

3. **Runtime Errors**:
   - Check logs for stack traces
   - Verify configuration
   - Check external service connectivity

## Resources and References

### Digital Twin Concepts
- [Digital Twin Consortium](https://www.digitaltwinconsortium.org/)
- Industry-specific digital twin standards
- Best practices for IoT and sensor integration

### Development Resources
- Project wiki (to be created)
- API documentation (to be created)
- Architecture decision records (ADRs)

## Changelog

### Version History

- **v0.1.0** (2025-11-16): Initial CLAUDE.md creation
  - Established project structure guidelines
  - Defined development workflows
  - Set code conventions and best practices

## Contact and Support

- **Repository**: mdomarsaleem1/Digital-twin
- **Issues**: Use GitHub issues for bug reports and feature requests
- **Discussions**: Use GitHub discussions for questions and ideas

---

**Last Updated**: 2025-11-16
**Maintained By**: Project Contributors
**Version**: 0.1.0
