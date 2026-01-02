# Changelog

All notable changes to WiiAutoConvert will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-01-02

### Added
- **Wizard-Based UI**: Complete redesign with modern multi-page workflow
  - Page 1: Input Selection with large drag-and-drop area
  - Page 2: Output Directory selection
  - Page 3: Network & Advanced Options (with progressive disclosure)
  - Page 4: Conversion Progress dashboard
- **Modern Dark Theme**: Card-based design with glassy aesthetic
- **Status Badge**: Real-time status indicator (Idle/Converting/Watching)
- **Progressive Disclosure**: Advanced network options hidden by default
- **Empty States**: Helpful placeholder text when no files are selected
- **Button Tiers**: Visual hierarchy with primary/secondary/destructive button styles
- **Build System**: PyInstaller support for creating standalone executables

### Changed
- **UI Framework**: Migrated from tkinter/ttk to customtkinter
- **Layout**: Switched from single-page form to wizard-based workflow
- **Navigation**: Back/Next buttons with dynamic validation
- **Progress Display**: Enhanced with idle states and better styling
- **Window Size**: Increased default size to 1200x850 for better visibility

### Technical Improvements
- Modular card-based architecture
- Centralized theme system
- Clean separation of UI from conversion logic
- State management via ConversionConfig dataclass
- Improved spacing and visual hierarchy

### Dependencies
- Added `customtkinter>=5.2.0` dependency

## [1.0.0] - 2024-01-XX

### Added
- Initial release of WiiAutoConvert
- ZIP file support: Automatically extracts and converts RVZ files from ZIP archives
- `--keep-extracted` option to preserve extracted RVZ files from ZIP archives
- `--delete-zip` option to delete original ZIP files after successful conversion
- ZIP file detection in both CLI and GUI interfaces
- Game metadata lookup: Automatically organizes output in folders with game title and ID
- Uses bundled GameTDB titles database from WIT tool
- `--no-metadata` option to disable automatic folder organization
- Folder structure matches Wii Backup Manager format: "Game Title [GAMEID]/GAMEID.wbfs"
- Watch mode: Automatically monitors directories for new ZIP/RVZ files and converts them
- `--watch` option for CLI watch mode
- Watch mode toggle in GUI
- Configurable watch interval and file stability time
- File stability detection to prevent processing incomplete downloads
- CLI interface with full argument parsing
- Desktop GUI with drag-and-drop support (file/folder selection)
- RVZ → ISO conversion using bundled Dolphin tool
- ISO → WBFS conversion using bundled WIT tool
- Batch processing for directories (recursive)
- Progress tracking per file
- Real-time logging display
- Error handling and validation
- Support for preserving or flattening directory structure
- Option to keep intermediate ISO files for debugging
- Cross-platform support (Windows, Linux, macOS)
- Comprehensive error messages and logging
- End-of-run summary with success/failure counts
- Unicode and space handling in file paths
- Overwrite protection (never overwrites existing WBFS files)
- Network move functionality with retry logic
- Concurrent conversion control for USB HDD safety

### Technical Details
- Clean architecture with separation of concerns
- Tool runner for subprocess execution
- Conversion engine with pipeline orchestration
- Thread-safe UI updates
- Comprehensive input validation
- File size and existence checks at each step

