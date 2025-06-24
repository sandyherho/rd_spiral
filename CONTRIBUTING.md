# Contributing to rd_spiral

First off, thank you for considering contributing to rd_spiral! It's people like you that make rd_spiral such a great tool.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Style Guidelines](#style-guidelines)
- [Commit Messages](#commit-messages)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to sandy.herho@email.ucr.edu.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Create a new branch for your feature or bugfix
4. Make your changes
5. Push to your fork and submit a pull request

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

* Use a clear and descriptive title
* Describe the exact steps to reproduce the problem
* Provide specific examples to demonstrate the steps
* Describe the behavior you observed after following the steps
* Explain which behavior you expected to see instead and why
* Include plots or screenshots if relevant
* Include your configuration file

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

* Use a clear and descriptive title
* Provide a step-by-step description of the suggested enhancement
* Provide specific examples to demonstrate the steps
* Describe the current behavior and explain which behavior you expected to see instead
* Explain why this enhancement would be useful
* List some other packages where this enhancement exists (if applicable)

### Pull Requests

* Fill in the required template
* Do not include issue numbers in the PR title
* Follow the [style guidelines](#style-guidelines)
* Include thoughtfully-worded, well-structured tests
* Document new code
* End all files with a newline

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/rd_spiral.git
cd rd_spiral

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode with dev dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Development Dependencies

The `[dev]` extras include:
- `pytest` - Testing framework
- `pytest-cov` - Coverage reporting
- `black` - Code formatting
- `flake8` - Code linting
- `mypy` - Type checking
- `pre-commit` - Git hooks
- `sphinx` - Documentation generation

## Style Guidelines

### Python Style

We use [Black](https://github.com/psf/black) for code formatting and [PEP 8](https://www.python.org/dev/peps/pep-0008/) as our base style guide.

```bash
# Format your code
black rd_spiral/

# Check style
flake8 rd_spiral/

# Type checking
mypy rd_spiral/
```

### Documentation Style

* Use Google-style docstrings
* Include type hints for all function arguments
* Add examples in docstrings where helpful
* Keep line length to 88 characters (Black default)

Example:
```python
def solve_reaction_diffusion(
    u0: np.ndarray,
    v0: np.ndarray, 
    params: Dict[str, float]
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Solve reaction-diffusion system.
    
    Args:
        u0: Initial condition for species u
        v0: Initial condition for species v
        params: Dictionary of parameters including:
            - d1: Diffusion coefficient for u
            - d2: Diffusion coefficient for v
            - beta: Reaction parameter
    
    Returns:
        Tuple of solution arrays (u, v)
    
    Example:
        >>> u, v = solve_reaction_diffusion(u0, v0, {'d1': 0.1, 'd2': 0.1, 'beta': 1.0})
    """
```

### Testing

* Write tests for any new functionality
* Ensure all tests pass before submitting PR
* Aim for >90% code coverage
* Use pytest for all tests

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=rd_spiral --cov-report=html
```

## Commit Messages

* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 72 characters or less
* Reference issues and pull requests liberally after the first line
* Consider starting the commit message with an applicable emoji:
    * 🎨 `:art:` - Improving structure/format of the code
    * ⚡ `:zap:` - Improving performance
    * 🔥 `:fire:` - Removing code or files
    * 🐛 `:bug:` - Fixing a bug
    * ✨ `:sparkles:` - Introducing new features
    * 📝 `:memo:` - Writing docs
    * 🚀 `:rocket:` - Deploying stuff
    * 💄 `:lipstick:` - Updating the UI and style files
    * ✅ `:white_check_mark:` - Adding tests
    * 🔒 `:lock:` - Fixing security issues
    * ⬆️ `:arrow_up:` - Upgrading dependencies
    * ⬇️ `:arrow_down:` - Downgrading dependencies

Example:
```
✨ Add support for custom reaction terms

- Allow users to define custom f(u,v) and g(u,v) functions
- Add validation for user-provided functions
- Include example in documentation
- Add comprehensive tests

Fixes #123
```

## Pull Request Process

1. Ensure any install or build dependencies are removed before the end of the layer when doing a build
2. Update the README.md with details of changes to the interface, this includes new environment variables, exposed ports, useful file locations and container parameters
3. Increase the version numbers in any examples files and the README.md to the new version that this Pull Request would represent. The versioning scheme we use is [SemVer](http://semver.org/)
4. You may merge the Pull Request in once you have the sign-off of two other developers, or if you do not have permission to do that, you may request the second reviewer to merge it for you

## Attribution

This Contributing Guide is adapted from the open-source contribution guidelines for [Facebook's Draft](https://github.com/facebook/draft-js/blob/master/CONTRIBUTING.md).
