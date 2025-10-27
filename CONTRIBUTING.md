# Contributing to Telelinker

Thank you for your interest in contributing to Telelinker! This document will guide you on how to participate in the project's development.

## How to contribute

### Reporting bugs

If you find an error:

1. Check that it hasn't been reported previously in [Issues](../../issues)
2. Create a new issue with:
   - Clear description of the problem
   - Steps to reproduce the error
   - Python version and operating system
   - Logs or screenshots if relevant

### Suggesting improvements

To propose new features:

1. Open an issue with the "enhancement" label
2. Clearly describe the proposed functionality
3. Explain why it would be useful for the project
4. If possible, provide usage examples

### Contributing code

#### Development environment setup

**⚠️ System dependencies:**

Before setting up the environment, install system dependencies:

```bash
# Windows (Scoop - recommended)
scoop install googlechrome chromedriver ffmpeg

# Linux (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install -y chromium chromium-driver ffmpeg

# macOS (Homebrew)
brew install --cask google-chrome
brew install chromedriver ffmpeg
```

**Project setup:**

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/your-username/telelinker.git
   cd telelinker
   ```
3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

#### Development process

1. Create a branch for your feature:
   ```bash
   git checkout -b feature/new-feature
   ```
2. Make your changes following code conventions
3. Ensure your code works correctly
4. Commit your changes:
   ```bash
   git commit -m "feat: clear description of the change"
   ```
5. Push to your fork:
   ```bash
   git push origin feature/new-feature
   ```
6. Create a Pull Request

#### Code conventions

- Use descriptive names for variables and functions
- Keep functions small and focused on one task
- Add comments for complex logic
- Follow PEP 8 for Python code style
- Use type hints when possible

#### Commit conventions

We use [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation changes
- `style:` for formatting changes
- `refactor:` for code refactoring
- `test:` for adding or modifying tests

### Project structure

```
telelinker/
├── src/
│   ├── cli/          # Command line commands
│   ├── scrapers/     # Scrapers for different platforms
│   ├── services/     # Services (Telegram, etc.)
│   └── utils/        # Shared utilities
├── tools/            # Development and testing scripts
└── bucket/           # Scoop configuration
```

### Adding new scrapers

To add support for a new platform:

1. Create a file in `src/scrapers/` with the platform name
2. Implement the scraping function following the pattern of existing scrapers
3. Add URL detection in the corresponding file
4. Update the documentation

### Testing

Before submitting your PR:

1. Test your code manually
2. Verify that it doesn't break existing functionality
3. If possible, add tests for your new functionality

### Documentation

- Update README.md if your change affects tool usage
- Add comments in the code to explain complex logic
- Document new parameters or features

## Code of conduct

This project follows the [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you commit to maintaining a respectful and collaborative environment.

## Need help?

If you have questions about how to contribute:

- Open an issue with the "question" label
- Review existing issues to see if your question has already been answered

We look forward to your contributions!