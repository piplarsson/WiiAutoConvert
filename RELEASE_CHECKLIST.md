# GitHub Release Checklist

Use this checklist when preparing a new release for GitHub.

## Pre-Release

- [ ] Update version number in `src/__init__.py`
- [ ] Update version number in `setup.py` (if different)
- [ ] Update `CHANGELOG.md` with new version and changes
- [ ] Test the application thoroughly
- [ ] Test CLI mode
- [ ] Test GUI mode (all wizard pages)
- [ ] Test watch mode
- [ ] Test network move functionality
- [ ] Verify all bundled tools work correctly

## Building Executable

- [ ] Install PyInstaller: `pip install pyinstaller`
- [ ] Run build: `build_exe.bat` (Windows) or `pyinstaller --clean WiiAutoConvert.spec`
- [ ] Test the executable in a clean directory
- [ ] Verify `tools/` directory is accessible from executable
- [ ] Test both GUI and CLI modes with executable
- [ ] Check file size (should be ~50-100MB)

## Documentation

- [ ] README.md is up to date
- [ ] CHANGELOG.md has latest version
- [ ] BUILD.md has correct instructions
- [ ] All screenshots/demos are current (if applicable)

## Git Preparation

- [ ] All changes committed
- [ ] `.gitignore` excludes build artifacts
- [ ] No sensitive data in repository
- [ ] License file is present and correct

## GitHub Release

- [ ] Create a new release tag (e.g., `v1.1.0`)
- [ ] Write release notes (can copy from CHANGELOG.md)
- [ ] Upload executable as release asset
- [ ] Include `tools/` directory or instructions for users
- [ ] Mark as "Latest release" if appropriate
- [ ] Add release description with:
  - What's new
  - Installation instructions
  - Known issues (if any)

## Post-Release

- [ ] Update any external documentation
- [ ] Announce release (if applicable)
- [ ] Monitor for issues/bug reports

## Release Tag Format

Use semantic versioning: `v1.1.0`

Format: `vMAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

## Example Release Notes Template

```markdown
# WiiAutoConvert v1.1.0

## What's New

- Modern wizard-based UI with dark theme
- Improved user experience with guided workflow
- Enhanced progress tracking
- [List other major features]

## Installation

### Option 1: Standalone Executable
1. Download `WiiAutoConvert.exe` from assets
2. Extract to a folder
3. Ensure `tools/` directory is in the same folder
4. Run `WiiAutoConvert.exe`

### Option 2: Python Installation
1. Clone repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run: `python main.py`

## Changes

[Copy relevant section from CHANGELOG.md]

## Requirements

- Windows 10/11 (for executable)
- Python 3.10+ (for source installation)
- Bundled tools (included in `tools/` directory)

## Known Issues

- [List any known issues]

## Full Changelog

See [CHANGELOG.md](https://github.com/yourusername/wii-autoconvert/blob/main/CHANGELOG.md)
```

