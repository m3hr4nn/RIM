# Contributing to RIM (RedFish Infrastructure Monitor)

Thank you for your interest in contributing to RIM! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Workflow](#development-workflow)
4. [Adding Vendor Support](#adding-vendor-support)
5. [Coding Standards](#coding-standards)
6. [Testing Guidelines](#testing-guidelines)
7. [Documentation](#documentation)
8. [Pull Request Process](#pull-request-process)
9. [Reporting Bugs](#reporting-bugs)
10. [Feature Requests](#feature-requests)

## Code of Conduct

This project adheres to a code of conduct that all contributors are expected to follow:

- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on constructive feedback
- Respect differing viewpoints and experiences
- Accept responsibility for mistakes

## Getting Started

### Prerequisites

Before contributing, ensure you have:

- Python 3.7 or higher
- Git
- A GitHub account
- Access to Redfish-enabled hardware or simulator (for vendor contributions)

### Setting Up Development Environment

```bash
# Fork the repository on GitHub
# Clone your fork
git clone https://github.com/YOUR_USERNAME/RIM.git
cd RIM

# Add upstream remote
git remote add upstream https://github.com/m3hr4nn/RIM.git

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-cov black flake8 pylint mypy

# Run tests to verify setup
pytest tests/
```

## Development Workflow

### 1. Create a Branch

Always create a new branch for your work:

```bash
# Update your fork
git fetch upstream
git checkout main
git merge upstream/main

# Create a feature branch
git checkout -b feature/vendor-hpe-support
# or
git checkout -b fix/thermal-parsing-bug
# or
git checkout -b docs/update-installation-guide
```

Branch naming conventions:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Test additions or updates

### 2. Make Your Changes

Follow these guidelines:

- Write clean, readable code
- Follow PEP 8 style guide
- Add docstrings to all functions and classes
- Include type hints where appropriate
- Keep commits atomic and focused

### 3. Test Your Changes

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=core tests/

# Run linters
black core/ --check
flake8 core/
pylint core/

# Run type checker
mypy core/
```

### 4. Commit Your Changes

Write clear commit messages:

```bash
git add .
git commit -m "Add HPE ProLiant vendor support

- Implement HPE vendor class with iLO-specific endpoints
- Add thermal and power metric extraction
- Include OEM extension handling
- Add unit tests for HPE implementation

Resolves #123"
```

Commit message format:
- First line: Brief summary (50 chars or less)
- Blank line
- Detailed explanation if needed
- Reference issue numbers

### 5. Push and Create Pull Request

```bash
git push origin feature/vendor-hpe-support
```

Then create a Pull Request on GitHub.

## Adding Vendor Support

Adding support for a new vendor is one of the most valuable contributions. Follow these steps:

### Step 1: Research

1. Read the [VENDOR_GUIDE.md](VENDOR_GUIDE.md)
2. Gather vendor documentation
3. Access vendor hardware or simulator
4. Document Redfish endpoints and responses

### Step 2: Create Vendor Class

Create a new file in `core/vendors/`:

```python
# core/vendors/hpe.py

from typing import Dict, Any, List
from loguru import logger
from .base_vendor import BaseVendor


class HPEVendor(BaseVendor):
    """
    HPE specific implementation for ProLiant servers.
    """

    def get_vendor_name(self) -> str:
        return "HPE"

    def get_supported_models(self) -> List[str]:
        return [
            "ProLiant DL380 Gen10",
            "ProLiant DL360 Gen10",
            # Add more models
        ]

    def get_thermal_metrics(self) -> Dict[str, Any]:
        # Implement HPE-specific thermal metric collection
        pass

    def get_power_metrics(self) -> Dict[str, Any]:
        # Implement HPE-specific power metric collection
        pass

    def get_storage_metrics(self) -> Dict[str, Any]:
        # Implement HPE-specific storage metric collection
        pass

    def get_network_metrics(self) -> Dict[str, Any]:
        # Implement HPE-specific network metric collection
        pass
```

### Step 3: Add Tests

Create test file in `tests/`:

```python
# tests/test_vendors_hpe.py

import pytest
from core import RedfishClient
from core.vendors.hpe import HPEVendor


def test_hpe_vendor_initialization():
    """Test HPE vendor class initialization."""
    # Mock client
    client = MockRedfishClient()
    vendor = HPEVendor(client)

    assert vendor.get_vendor_name() == "HPE"
    assert len(vendor.get_supported_models()) > 0


def test_hpe_thermal_metrics():
    """Test HPE thermal metric collection."""
    # Test implementation
    pass
```

### Step 4: Generate Templates

Create Zabbix and Grafana templates:

```bash
python tools/generate_zabbix_template.py --vendor hpe --model "ProLiant DL380 Gen10"
python tools/generate_grafana_dashboard.py --vendor hpe --model "ProLiant DL380 Gen10"
```

### Step 5: Documentation

Update documentation:

1. Add vendor to README.md support matrix
2. Create vendor-specific guide in `docs/vendors/hpe.md`
3. Document any unique features or limitations

### Step 6: Submit Pull Request

Include in your PR:
- Vendor implementation
- Tests
- Documentation updates
- Example configurations
- Testing notes (hardware tested, firmware versions)

## Coding Standards

### Python Style

Follow PEP 8 with these specific guidelines:

```python
# Import order: stdlib, third-party, local
import json
from typing import Dict, Any

import requests
from loguru import logger

from .base_vendor import BaseVendor


# Class naming: PascalCase
class VendorImplementation:
    """
    Class docstring explaining purpose.

    Detailed description if needed.
    """

    # Function naming: snake_case
    def get_thermal_data(self, chassis_id: str) -> Dict[str, Any]:
        """
        Function docstring with Args and Returns.

        Args:
            chassis_id: Chassis identifier

        Returns:
            Dictionary containing thermal data
        """
        # Implementation with type hints
        pass


# Constants: UPPER_SNAKE_CASE
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30
```

### Code Formatting

Use Black for formatting:

```bash
black core/ --line-length 100
```

### Type Hints

Always include type hints:

```python
from typing import Dict, List, Any, Optional

def process_data(
    input_data: Dict[str, Any],
    options: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Process the input data."""
    pass
```

### Logging

Use loguru for logging:

```python
from loguru import logger

logger.debug("Detailed information for debugging")
logger.info("General information")
logger.warning("Warning messages")
logger.error("Error messages")
```

### Error Handling

Implement proper error handling:

```python
try:
    result = client.get(endpoint)
    if not result:
        logger.warning(f"No data returned from {endpoint}")
        return {}
except requests.exceptions.RequestException as e:
    logger.error(f"Failed to fetch data: {e}")
    return {"error": str(e)}
```

## Testing Guidelines

### Test Structure

```
tests/
├── __init__.py
├── conftest.py                 # Pytest fixtures
├── test_redfish_client.py      # Client tests
├── test_health_checker.py      # Health checker tests
├── test_exporters/             # Exporter tests
│   ├── test_csv_exporter.py
│   ├── test_zabbix_exporter.py
│   └── ...
└── test_vendors/               # Vendor tests
    ├── test_dell.py
    ├── test_hpe.py
    └── ...
```

### Writing Tests

```python
import pytest
from unittest.mock import Mock, patch


@pytest.fixture
def mock_client():
    """Create mock Redfish client."""
    client = Mock()
    client.get_vendor_info.return_value = {
        "vendor": "TestVendor",
        "model": "TestModel"
    }
    return client


def test_vendor_initialization(mock_client):
    """Test vendor class initialization."""
    vendor = VendorClass(mock_client)
    assert vendor.vendor_name == "TestVendor"


def test_thermal_metrics_success(mock_client):
    """Test successful thermal metric collection."""
    # Setup mock
    mock_client.get_thermal.return_value = {
        "Temperatures": [{"Name": "CPU", "ReadingCelsius": 45}]
    }

    vendor = VendorClass(mock_client)
    metrics = vendor.get_thermal_metrics()

    assert len(metrics["temperatures"]) == 1
    assert metrics["temperatures"][0]["reading_celsius"] == 45


def test_thermal_metrics_failure(mock_client):
    """Test thermal metric collection when API fails."""
    mock_client.get_thermal.return_value = None

    vendor = VendorClass(mock_client)
    metrics = vendor.get_thermal_metrics()

    assert "error" in metrics
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_vendors/test_dell.py

# Run with coverage
pytest --cov=core --cov-report=html

# Run with verbose output
pytest -v

# Run tests matching pattern
pytest -k "thermal"
```

## Documentation

### Code Documentation

All public functions and classes must have docstrings:

```python
def complex_function(param1: str, param2: int) -> Dict[str, Any]:
    """
    Brief description of what the function does.

    More detailed explanation if needed. Can span multiple
    lines and include examples.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When param2 is negative
        ConnectionError: When connection fails

    Examples:
        >>> result = complex_function("test", 42)
        >>> print(result["status"])
        "OK"
    """
    pass
```

### README Updates

When adding features, update README.md:

- Add to features list
- Update usage examples
- Update support matrix
- Add to roadmap if applicable

### Vendor Documentation

Create vendor-specific docs in `docs/vendors/`:

```markdown
# HPE ProLiant Integration Guide

## Supported Models
- ProLiant DL380 Gen10
- ProLiant DL360 Gen10

## Prerequisites
- iLO 5 firmware 2.30 or higher
- Redfish API enabled
- Valid iLO credentials

## Configuration
...

## Troubleshooting
...
```

## Pull Request Process

### Before Submitting

Checklist:
- [ ] Code follows project style guidelines
- [ ] All tests pass
- [ ] New tests added for new functionality
- [ ] Documentation updated
- [ ] Commit messages are clear
- [ ] No merge conflicts with main branch

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Related Issues
Closes #123
Related to #456

## Testing
Describe testing performed:
- Tested on Dell PowerEdge R740 with iDRAC 4.40
- All unit tests pass
- Manual testing completed

## Screenshots (if applicable)
Add screenshots here

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added to complex code
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tests added
- [ ] All tests pass
```

### Review Process

1. Automated checks run (tests, linters)
2. Maintainer review
3. Feedback addressed
4. Approval and merge

## Reporting Bugs

### Before Reporting

- Check existing issues
- Test with latest version
- Gather detailed information

### Bug Report Template

```markdown
**Describe the bug**
Clear description of the bug

**To Reproduce**
Steps to reproduce:
1. Initialize client with...
2. Call function...
3. See error

**Expected behavior**
What you expected to happen

**Actual behavior**
What actually happened

**Environment:**
- RIM Version: [e.g., 1.0.0]
- Python Version: [e.g., 3.9.5]
- OS: [e.g., Ubuntu 20.04]
- Vendor/Model: [e.g., Dell PowerEdge R740]
- Firmware Version: [e.g., iDRAC 4.40.00.00]

**Logs:**
```
Include relevant logs
```

**Additional context**
Any other relevant information
```

## Feature Requests

Use GitHub Issues with the "enhancement" label:

```markdown
**Is your feature request related to a problem?**
Description of the problem

**Describe the solution you'd like**
Clear description of desired functionality

**Describe alternatives you've considered**
Alternative solutions or features

**Additional context**
Any other relevant information
```

## Community

- **Discussions**: Use GitHub Discussions for questions
- **Issues**: Use GitHub Issues for bugs and features
- **Pull Requests**: Submit contributions via PR

## License

By contributing to RIM, you agree that your contributions will be licensed under the MIT License.

## Questions?

If you have questions about contributing:
- Check existing documentation
- Search closed issues
- Open a discussion on GitHub
- Contact maintainers

---

Thank you for contributing to RIM! Your efforts help make infrastructure monitoring easier for everyone.