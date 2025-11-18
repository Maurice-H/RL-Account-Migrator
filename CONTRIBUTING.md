# Contributing to RL-Account-Migrator

First off, thank you for considering contributing to RL-Account-Migrator! 🎉

The following is a set of guidelines for contributing to this project. These are mostly guidelines, not rules. Use your best judgment, and feel free to propose changes to this document in a pull request.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
  - [Reporting Bugs](#reporting-bugs)
  - [Suggesting Features](#suggesting-features)
  - [Code Contributions](#code-contributions)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Style Guidelines](#style-guidelines)

---

## Code of Conduct

This project and everyone participating in it is governed by basic principles of respect and professionalism. By participating, you are expected to uphold these standards:

- Be respectful and inclusive
- Accept constructive criticism gracefully
- Focus on what is best for the community
- Show empathy towards other community members

---

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When you create a bug report, include as many details as possible:

- **Clear title** - Use a descriptive title for the issue
- **Steps to reproduce** - Detailed steps to reproduce the problem
- **Expected behavior** - What you expected to happen
- **Actual behavior** - What actually happened
- **Environment details**:
  - OS (Windows/Linux/macOS)
  - Python version
  - Poetry version
  - Game launcher (Steam/Epic)
- **Screenshots** - If applicable, add screenshots
- **Error messages** - Include full error messages or logs

**Example:**
```
Title: Settings not loading from Steam account

Description:
When I try to load my settings from my Steam account, the tool crashes with an error.

Steps to reproduce:
1. Open RL-Account-Migrator
2. Select "Load from Steam"
3. Click "Load Settings"
4. Application crashes

Expected: Settings should be loaded
Actual: Application crashes with KeyError

Environment:
- Windows 11
- Python 3.12.1
- Poetry 2.0.0
- Steam version of Rocket League

Error message: [paste error here]
```

### Suggesting Features

Feature suggestions are welcome! To suggest a feature:

- **Use a clear title** - Describe the feature concisely
- **Provide detailed description** - Explain what the feature should do
- **Explain the use case** - Why would this feature be useful?
- **Consider alternatives** - Have you considered any alternative solutions?

### Code Contributions

You can contribute by:

- Fixing bugs
- Implementing new features
- Improving documentation
- Optimizing code performance
- Adding tests

---

## Development Setup

1. **Fork the repository** on GitHub

2. **Clone your fork**
   ```bash
   git clone https://github.com/YOUR-USERNAME/RL-Account-Migrator.git
   cd RL-Account-Migrator
   ```

3. **Create a new branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
   Use prefixes:
   - `feature/` for new features
   - `fix/` for bug fixes
   - `docs/` for documentation
   - `refactor/` for code refactoring

4. **Install Poetry** (if not already installed)
   ```bash
   pip install poetry
   ```

5. **Install dependencies**
   ```bash
   poetry install
   ```
   This will create a virtual environment (if it doesn't exist) and install all required dependencies.

6. **Make your changes**
   - Write clean, readable code
   - Follow existing code style
   - Add comments for complex logic
   - Test your changes thoroughly

7. **Test locally**
   ```bash
   poetry run python src/main.py
   ```
   Or activate the virtual environment manually:
   ```bash
   # Windows
   .venv\Scripts\activate
   python src/main.py
   
   # Linux/macOS
   source .venv/bin/activate
   python src/main.py
   ```

8. **Build and test executable** (for significant changes)
   ```bash
   poetry run pyinstaller RLAccountMigrator.spec
   ```

---

## Pull Request Process

1. **Update documentation** - If you changed functionality, update the README.md

2. **Test thoroughly** - Make sure your changes work on your system

3. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add support for custom config paths"
   ```
   
   Use conventional commit messages:
   - `feat:` - New feature
   - `fix:` - Bug fix
   - `docs:` - Documentation changes
   - `refactor:` - Code refactoring
   - `test:` - Adding tests
   - `chore:` - Maintenance tasks

4. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create a Pull Request**
   - Go to the original repository
   - Click "New Pull Request"
   - Select your fork and branch
   - Fill out the PR template with:
     - Description of changes
     - Related issue numbers (if applicable)
     - Testing performed
     - Screenshots (if UI changes)

6. **Wait for review** - Maintainers will review your PR and may request changes

7. **Address feedback** - Make requested changes and push updates

---

## Style Guidelines

### Python Code Style

- Follow **PEP 8** guidelines
- Use **type hints** where appropriate
- Keep functions focused and small
- Use meaningful variable names
- Add docstrings for functions and classes

**Example:**
```python
def load_config_from_path(config_path: str) -> dict:
    """
    Load Rocket League configuration from specified path.
    
    Args:
        config_path: Full path to the config file
        
    Returns:
        Dictionary containing parsed configuration
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If config file is invalid
    """
    # Implementation here
    pass
```

### Git Commit Messages

- Use present tense ("add feature" not "added feature")
- Use imperative mood ("move cursor to..." not "moves cursor to...")
- Limit first line to 72 characters
- Reference issues and pull requests when relevant

**Good:**
```
feat: add Epic Games account detection
fix: resolve Steam config path issue on Linux
docs: update installation instructions
```

**Bad:**
```
Added stuff
Fixed bug
Updates
```

---

## Questions?

If you have questions or need help:

- 💬 Open a [Discussion](https://github.com/Maurice-H/RL-Account-Migrator/discussions)
- 💬 Contact via Discord: **maizu_u**
- 📧 Create an [Issue](https://github.com/Maurice-H/RL-Account-Migrator/issues) with the "question" label

---

## License

By contributing to RL-Account-Migrator, you agree that your contributions will be licensed under the MIT License (see LICENSE file).

---

Thank you for contributing! 🚀
