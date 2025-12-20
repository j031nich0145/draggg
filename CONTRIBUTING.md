# Contributing to draggg

Thank you for your interest in contributing to draggg! This document provides guidelines and instructions for contributing to the project.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork:**
   ```bash
   git clone https://github.com/your-username/draggg.git
   cd draggg
   ```

3. **Set up development environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Create a branch for your work:**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

## Development Workflow

### Code Style

- Follow **PEP 8** Python style guidelines
- Use **type hints** for all function signatures
- Include **docstrings** for all classes and functions
- Keep lines under 100 characters when possible
- Use meaningful variable and function names

### Testing

- Write tests for new features
- Run existing tests before submitting:
  ```bash
  python3 -m pytest tests/  # If pytest is set up
  ```
- Test on your target platform before submitting PR
- Include test results in your PR description

### Documentation

- Update relevant documentation when adding features
- Add docstrings following Google or NumPy style
- Update README.md if user-facing changes are made
- Add comments for complex logic

## Contribution Areas

### Current Focus (Linux)

- Touchpad driver compatibility improvements
- Wayland support enhancements
- Gesture recognition accuracy
- Performance optimizations
- Configuration system improvements

### Future Platforms

We're planning support for macOS and Windows! See [FUTURE_PLATFORMS.md](FUTURE_PLATFORMS.md) for:
- Architecture design
- Implementation roadmap
- Platform-specific contribution guidelines
- API requirements and challenges

**Priority:** macOS support is planned first, followed by Windows.

## Pull Request Process

1. **Ensure your code works:**
   - Test on your platform
   - Run any existing tests
   - Check for linting errors

2. **Write a clear PR description:**
   - What changes were made
   - Why the changes were needed
   - How to test the changes
   - Platform tested on
   - Screenshots/videos if applicable

3. **Keep PRs focused:**
   - One feature or fix per PR
   - Keep changes reasonably sized
   - Break large features into smaller PRs

4. **Update documentation:**
   - README.md if user-facing
   - Code comments for complex logic
   - Any relevant setup/installation docs

## Platform-Specific Guidelines

### Linux Contributions

- Test with different touchpad drivers if possible
- Consider Wayland vs X11 compatibility
- Test permission scenarios (with/without sudo, input group, etc.)
- Verify hardware detection works correctly

### macOS Contributions (Future)

- See [FUTURE_PLATFORMS.md](FUTURE_PLATFORMS.md) for detailed guidelines
- Test permission prompts
- Verify Quartz Event Tap implementation
- Test on multiple macOS versions

### Windows Contributions (Future)

- See [FUTURE_PLATFORMS.md](FUTURE_PLATFORMS.md) for detailed guidelines
- Test with different touchpad drivers
- Handle UAC/permission requirements
- Test on multiple Windows versions

## Code Structure

When adding new features:

- **Core logic** (platform-agnostic) should be in the main `draggg.py` or future `core/` directory
- **Platform-specific code** should be clearly separated
- **Configuration** should use the existing `config.py` system
- **Hardware detection** should use or extend `detect_hardware.py`

## Reporting Issues

When reporting bugs:

1. **Check existing issues** to avoid duplicates
2. **Include system information:**
   - Linux distribution and version
   - Python version
   - Touchpad model/driver
   - draggg version
3. **Describe the problem:**
   - What you expected to happen
   - What actually happened
   - Steps to reproduce
4. **Include logs:**
   - Run with `--verbose` flag
   - Include relevant error messages

## Feature Requests

For feature requests:

1. **Check if it's already planned** in [FUTURE_PLATFORMS.md](FUTURE_PLATFORMS.md)
2. **Open an issue** with:
   - Clear description of the feature
   - Use case/justification
   - Platform(s) it would benefit
3. **Be patient** - we'll discuss and prioritize

## Questions?

- Open an issue for questions about implementation
- Check [FUTURE_PLATFORMS.md](FUTURE_PLATFORMS.md) for platform-specific questions
- Review existing code for examples

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Celebrate contributions of all sizes

Thank you for contributing to draggg!

