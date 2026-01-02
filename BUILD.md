# Building WiiAutoConvert Executable

This guide explains how to build a standalone executable for WiiAutoConvert.

## Prerequisites

- Python 3.10 or higher
- PyInstaller (will be installed automatically by build script)

## Quick Build (Windows)

Simply run:
```batch
build_exe.bat
```

This will:
1. Check for PyInstaller and install it if needed
2. Build the executable using the spec file
3. Output `WiiAutoConvert.exe` in the `dist/` folder

## Manual Build

### Step 1: Install PyInstaller

```bash
pip install pyinstaller
```

### Step 2: Build Executable

**Windows:**
```bash
python -m PyInstaller --clean WiiAutoConvert.spec
```

**Linux/macOS:**
```bash
python -m PyInstaller --clean WiiAutoConvert.spec
```

**Note**: Using `python -m PyInstaller` instead of `pyinstaller` ensures it works even if PyInstaller isn't in your PATH.

### Step 3: Locate Output

The executable will be in the `dist/` directory:
- Windows: `dist/WiiAutoConvert.exe`
- Linux: `dist/WiiAutoConvert`
- macOS: `dist/WiiAutoConvert.app`

## Distribution

### Single-File Executable

The current spec file creates a single-file executable that includes:
- Python runtime
- All dependencies (customtkinter, etc.)
- Application code
- Automatic tool downloader

**Important**: The executable includes automatic tool downloading. When you run it for the first time, it will automatically download WIT (Windows) if missing. Dolphin must be downloaded manually (instructions provided in-app).

**Note**: The `tools/` directory is NOT required at build time. Tools will be downloaded automatically on first run.

### Tool Downloading

The executable includes automatic tool downloading functionality:

- **WIT (Windows)**: Automatically downloads and installs on first run
- **Dolphin**: Provides instructions for manual download (no direct API available)

No need to bundle or distribute the `tools/` directory. The executable will create it automatically and download tools as needed.

## File Size

The executable is smaller (~12-15MB) because it doesn't bundle the tools:
- Python interpreter
- customtkinter and dependencies
- Application code
- Automatic tool downloader

Tools are downloaded separately on first run (WIT ~5MB, Dolphin varies).

## Troubleshooting

### "Tool not found" errors

If tools are not found:
1. The application will automatically attempt to download WIT (Windows)
2. For Dolphin, follow the instructions provided in the error message
3. Ensure you have an internet connection for automatic downloads
4. Check that the `tools/` directory is writable (the executable will create it)

### Import errors

If you see import errors, add missing modules to `hiddenimports` in `WiiAutoConvert.spec`:

```python
hiddenimports=[
    'customtkinter',
    'tkinter',
    # Add other missing modules here
],
```

### Large file size

To reduce size, you can:
1. Use `--exclude-module` to exclude unused modules
2. Use UPX compression (already enabled in spec)
3. Consider using `--onedir` instead of `--onefile` (creates a folder instead)

## Advanced: Custom Icon

To add a custom icon:

1. Create or obtain an `.ico` file (Windows) or `.icns` (macOS)
2. Update `WiiAutoConvert.spec`:
   ```python
   icon='path/to/icon.ico',  # or .icns for macOS
   ```
3. Rebuild

## Testing the Executable

After building, test the executable:

1. Copy `dist/WiiAutoConvert.exe` to a test folder (no `tools/` directory needed)
2. Run the executable
3. On first run, it will check for tools and offer to download them
4. Test both GUI and CLI modes
5. Verify that tools are downloaded to `tools/` directory automatically

