# Contributing to ZenithOne Explorer

Thank you for your interest in contributing to ZenithOne Explorer! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)
- [Issue Guidelines](#issue-guidelines)

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors, regardless of experience level, gender, gender identity and expression, sexual orientation, disability, personal appearance, body size, race, ethnicity, age, religion, or nationality.

### Our Standards

**Positive behavior includes:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints and experiences
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

**Unacceptable behavior includes:**
- Trolling, insulting/derogatory comments, and personal or political attacks
- Public or private harassment
- Publishing others' private information without explicit permission
- Other conduct which could reasonably be considered inappropriate

## Getting Started

### Prerequisites

- Python 3.14+
- Node.js 22+
- Podman
- Ollama
- Git
- Basic understanding of FastAPI, SQLAlchemy, and containerization

### Fork and Clone

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR_USERNAME/zenithone-explorer.git
cd zenithone-explorer

# Add upstream remote
git remote add upstream https://github.com/paulmmoore3416/zenithone-explorer.git
```

## Development Setup

### Backend Setup

```bash
cd backend

# Create virtual environment
python3.14 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-cov black flake8 mypy

# Copy environment file
cp ../.env.example .env

# Initialize database
python -c "from database.connection import init_db; init_db()"

# Run backend
uvicorn main:app --reload
```

### CLI Setup

```bash
cd cli

# Install dependencies
npm install

# Install development dependencies
npm install --save-dev jest eslint prettier

# Link CLI locally
npm link

# Run tests
npm test
```

### UI Setup

```bash
cd ui

# Serve locally
python3 -m http.server 8080
```

## How to Contribute

### Types of Contributions

1. **Bug Reports**: Report bugs via GitHub Issues
2. **Feature Requests**: Suggest new features via GitHub Issues
3. **Code Contributions**: Submit pull requests for bug fixes or features
4. **Documentation**: Improve or add documentation
5. **Testing**: Add or improve tests
6. **Design**: Improve UI/UX design

### Contribution Workflow

1. **Check existing issues**: Look for existing issues or create a new one
2. **Discuss**: Comment on the issue to discuss your approach
3. **Create branch**: Create a feature branch from `main`
4. **Make changes**: Implement your changes
5. **Test**: Ensure all tests pass
6. **Commit**: Write clear commit messages
7. **Push**: Push to your fork
8. **Pull Request**: Create a pull request

## Coding Standards

### Python (Backend)

#### Style Guide

Follow PEP 8 with these specifics:

```python
# Use 4 spaces for indentation
# Maximum line length: 100 characters
# Use double quotes for strings

# Good
def create_workload(name: str, workload_type: str) -> Workload:
    """Create a new workload.
    
    Args:
        name: Workload name
        workload_type: Type of workload (batch, interactive, etc.)
        
    Returns:
        Created workload instance
        
    Raises:
        ValueError: If workload_type is invalid
    """
    if workload_type not in VALID_TYPES:
        raise ValueError(f"Invalid workload type: {workload_type}")
    
    return Workload(name=name, type=workload_type)
```

#### Type Hints

Always use type hints:

```python
from typing import List, Optional, Dict, Any

def get_workloads(
    status: Optional[str] = None,
    limit: int = 20
) -> List[Dict[str, Any]]:
    """Get list of workloads."""
    pass
```

#### Docstrings

Use Google-style docstrings:

```python
def process_data(data: List[int], threshold: int = 10) -> Dict[str, Any]:
    """Process data and return statistics.
    
    Args:
        data: List of integers to process
        threshold: Minimum value threshold (default: 10)
        
    Returns:
        Dictionary containing:
            - count: Number of items
            - average: Average value
            - filtered: Items above threshold
            
    Raises:
        ValueError: If data is empty
        
    Example:
        >>> process_data([1, 5, 15, 20], threshold=10)
        {'count': 4, 'average': 10.25, 'filtered': [15, 20]}
    """
    pass
```

#### Code Formatting

```bash
# Format code with Black
black backend/

# Check with flake8
flake8 backend/

# Type check with mypy
mypy backend/
```

### JavaScript (CLI & UI)

#### Style Guide

Follow Airbnb JavaScript Style Guide:

```javascript
// Use 2 spaces for indentation
// Use single quotes for strings
// Use semicolons

// Good
const createWorkload = async (name, type) => {
  try {
    const response = await api.post('/workloads', { name, type });
    return response.data;
  } catch (error) {
    console.error('Failed to create workload:', error);
    throw error;
  }
};
```

#### Code Formatting

```bash
# Format with Prettier
npm run format

# Lint with ESLint
npm run lint
```

### Git Commit Messages

Follow Conventional Commits:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**

```bash
# Feature
git commit -m "feat(workload): Add AI-powered scheduling"

# Bug fix
git commit -m "fix(api): Resolve container status race condition"

# Documentation
git commit -m "docs(readme): Update installation instructions"

# With body
git commit -m "feat(cli): Add workload export command

- Add export command to CLI
- Support JSON and YAML formats
- Include tests and documentation

Closes #123"
```

## Testing Guidelines

### Backend Tests

```python
# tests/unit/test_workload_manager.py
import pytest
from core.workload_manager import WorkloadManager

class TestWorkloadManager:
    """Test WorkloadManager class."""
    
    @pytest.fixture
    def manager(self):
        """Create WorkloadManager instance."""
        return WorkloadManager()
    
    def test_create_workload(self, manager):
        """Test workload creation."""
        workload = manager.create_workload(
            name="test",
            workload_type="batch"
        )
        assert workload.name == "test"
        assert workload.type == "batch"
    
    def test_invalid_workload_type(self, manager):
        """Test invalid workload type raises error."""
        with pytest.raises(ValueError):
            manager.create_workload(
                name="test",
                workload_type="invalid"
            )
```

### Running Tests

```bash
# Backend tests
cd backend
pytest

# With coverage
pytest --cov=. --cov-report=html

# Specific test file
pytest tests/unit/test_workload_manager.py

# CLI tests
cd cli
npm test

# With coverage
npm test -- --coverage
```

### Test Coverage

Maintain minimum 80% test coverage:

```bash
# Check coverage
pytest --cov=. --cov-report=term-missing

# Generate HTML report
pytest --cov=. --cov-report=html
open htmlcov/index.html
```

## Documentation

### Code Documentation

- Add docstrings to all functions, classes, and modules
- Include type hints
- Provide examples where helpful
- Keep documentation up-to-date with code changes

### User Documentation

When adding features, update:
- README.md
- API_REFERENCE.md
- CLI_GUIDE.md
- UI_GUIDE.md
- CONFIGURATION.md

### Documentation Style

- Use clear, concise language
- Include code examples
- Add screenshots for UI features
- Provide troubleshooting tips

## Pull Request Process

### Before Submitting

1. **Update from upstream**:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run tests**:
   ```bash
   pytest
   npm test
   ```

3. **Format code**:
   ```bash
   black backend/
   npm run format
   ```

4. **Update documentation**: Ensure docs reflect your changes

5. **Update CHANGELOG.md**: Add entry for your changes

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] Tests pass locally
- [ ] No new warnings

## Related Issues
Closes #123
```

### Review Process

1. **Automated checks**: CI/CD runs tests and linting
2. **Code review**: Maintainers review your code
3. **Feedback**: Address review comments
4. **Approval**: PR approved by maintainer
5. **Merge**: PR merged into main branch

## Issue Guidelines

### Bug Reports

Use the bug report template:

```markdown
**Describe the bug**
Clear description of the bug

**To Reproduce**
Steps to reproduce:
1. Go to '...'
2. Click on '...'
3. See error

**Expected behavior**
What you expected to happen

**Screenshots**
If applicable, add screenshots

**Environment:**
- OS: [e.g., Ubuntu 22.04]
- Python version: [e.g., 3.14]
- ZenithOne version: [e.g., 1.0.0]

**Additional context**
Any other relevant information
```

### Feature Requests

Use the feature request template:

```markdown
**Is your feature request related to a problem?**
Clear description of the problem

**Describe the solution you'd like**
Clear description of desired solution

**Describe alternatives you've considered**
Alternative solutions or features

**Additional context**
Any other relevant information
```

## Development Tips

### Debugging

```python
# Use logging instead of print
import logging
logger = logging.getLogger(__name__)

logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
```

### Performance

- Profile code before optimizing
- Use appropriate data structures
- Cache expensive operations
- Minimize database queries

### Security

- Never commit secrets or credentials
- Validate all user input
- Use parameterized queries
- Follow OWASP guidelines

## Getting Help

- **Documentation**: Check existing documentation
- **Issues**: Search existing issues
- **Discussions**: Use GitHub Discussions
- **Email**: paulmmoore3416@gmail.com

## Recognition

Contributors will be recognized in:
- CHANGELOG.md
- GitHub contributors page
- Project documentation

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT License).

## Thank You!

Thank you for contributing to ZenithOne Explorer! Your contributions help make this project better for everyone.
