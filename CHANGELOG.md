# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Open source project configuration files
- MIT License
- Contribution guide (CONTRIBUTING.md)
- Code of conduct (CODE_OF_CONDUCT.md)
- Templates for issues and pull requests
- Badges in README.md
- Contribution section in README.md

## [1.0.0] - 2024-XX-XX

### Added
- CLI tool for extracting links from Telegram groups
- Support for multiple export formats (CSV, PostgreSQL)
- Scrapers for different social platforms:
  - Instagram
  - LinkedIn
  - Medium
  - Dev.to
  - TikTok
  - YouTube
- Main commands:
  - `telelinker setup` - Initial configuration
  - `telelinker login` - Telegram authentication
  - `telelinker groups` - List available groups
  - `telelinker fetch` - Extract links and metadata
- Support for installation via Scoop (Windows)
- Dockerfile for containerization
- Utilities for date normalization and counts

### Security
- .env.example file for secure configuration
- Credentials exclusion in .gitignore

---

## Types of changes

- `Added` for new features
- `Changed` for changes in existing functionality
- `Deprecated` for soon-to-be removed features
- `Removed` for removed features
- `Fixed` for bug fixes
- `Security` for vulnerabilities