# WiiAutoConvert v1.1.0

## 🎉 What's New

This release introduces a complete UI redesign with a modern wizard-based interface, making the conversion process more intuitive and user-friendly.

### Major Features

- **✨ Modern Wizard-Based UI**: Complete redesign with a 4-page guided workflow
  - Page 1: Input Selection with large drag-and-drop area
  - Page 2: Output Directory selection
  - Page 3: Network & Advanced Options (with progressive disclosure)
  - Page 4: Conversion Progress dashboard with real-time updates

- **🎨 Modern Dark Theme**: Beautiful card-based design with glassy aesthetic
  - Dark mode optimized for comfortable viewing
  - Rounded corners and soft contrast borders
  - Teal/cyan accent colors
  - Consistent spacing and padding

- **📦 Standalone Executable**: Pre-built Windows executable available
  - No Python installation required
  - Bundles all dependencies
  - Simply download and run

### UI Improvements

- **Progressive Disclosure**: Advanced options hidden by default, reducing visual clutter
- **Empty States**: Helpful placeholder text when no files are selected
- **Button Tiers**: Clear visual hierarchy with primary/secondary/destructive styles
- **Status Badge**: Real-time status indicator (Idle/Converting/Watching)
- **Enhanced Progress Display**: Better styling with idle states and improved readability

### Technical Improvements

- Migrated from tkinter/ttk to customtkinter for modern UI components
- Modular card-based architecture for better maintainability
- Centralized theme system for consistent styling
- Clean separation of UI from conversion logic
- State management via ConversionConfig dataclass
- Improved spacing and visual hierarchy

## 📥 Installation

### Option 1: Standalone Executable (Recommended for Windows)

1. Download `WiiAutoConvert.exe` from the [Releases](https://github.com/yourusername/wii-autoconvert/releases) page
2. Extract to a folder
3. Ensure the `tools/` directory is in the same folder as the executable
4. Run `WiiAutoConvert.exe`

**Note**: The executable must be run from a location where the `tools/` directory is accessible. Either:
- Place the executable in the project root directory, OR
- Copy the `tools/` directory to the same folder as the executable

### Option 2: Python Installation

1. Clone or download this repository
2. Ensure Python 3.10+ is installed
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run: `python main.py`

## 📋 Requirements

- **Windows**: Windows 10/11 (for executable) or Python 3.10+
- **Linux/macOS**: Python 3.10+
- **Bundled Tools**: Included in `tools/` directory (Dolphin Tool and WIT)

## 🔄 Changes from v1.0.0

### Added
- Wizard-based UI with 4-page workflow
- Modern dark theme with card-based design
- Status badge for real-time status indication
- Progressive disclosure for advanced options
- Empty states with helpful placeholder text
- Button tiers with visual hierarchy
- PyInstaller build system for creating executables

### Changed
- UI framework: tkinter/ttk → customtkinter
- Layout: Single-page form → Multi-page wizard
- Navigation: Simple buttons → Back/Next with validation
- Progress display: Enhanced with idle states
- Window size: Increased to 1200x850 for better visibility

### Dependencies
- Added `customtkinter>=5.2.0` requirement

## 🐛 Known Issues

None at this time. If you encounter any issues, please report them on the [Issues](https://github.com/yourusername/wii-autoconvert/issues) page.

## 📚 Documentation

- [README.md](README.md) - Full documentation and usage guide
- [CHANGELOG.md](CHANGELOG.md) - Complete version history
- [BUILD.md](BUILD.md) - Instructions for building from source

## 🙏 Thank You

Thank you for using WiiAutoConvert! If you find this tool useful, please consider:
- ⭐ Starring the repository
- 🐛 Reporting bugs
- 💡 Suggesting features
- 📖 Improving documentation

## 🔗 Links

- [Full Changelog](CHANGELOG.md)
- [Issue Tracker](https://github.com/yourusername/wii-autoconvert/issues)
- [Repository](https://github.com/yourusername/wii-autoconvert)

---

**Full Changelog**: [v1.0.0...v1.1.0](https://github.com/yourusername/wii-autoconvert/compare/v1.0.0...v1.1.0)

