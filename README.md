# WiiAutoConvert

**Convert Nintendo Wii RVZ ROMs to WBFS format** for use with USB Loader GX and other Wii homebrew loaders.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)]()

---

## ✨ Features

- 🎯 **RVZ → WBFS Conversion**: Full pipeline using official Dolphin and WIT tools
- 📦 **ZIP Support**: Automatically extracts and converts RVZ files from ZIP archives
- 🎮 **Auto Metadata**: Organizes output with game titles and IDs (e.g., `Super Mario Galaxy [SM2E52]/SM2E52.wbfs`)
- 👀 **Watch Mode**: Monitors directories for new files and converts automatically
- 🖥️ **Modern GUI**: Wizard-based interface with dark theme and guided workflow
- 💻 **CLI Support**: Full command-line interface for batch processing
- 🔄 **Batch Processing**: Convert entire directories recursively
- 📊 **Real-time Progress**: Live status updates and detailed logs
- 🌐 **Network Move**: Optional automatic file transfer after conversion
- 🔧 **Auto Tool Download**: Automatically downloads WIT and Dolphin tools if missing

---

## 🚀 Quick Start

### Windows (Executable)

1. Download `WiiAutoConvert.exe` from [Releases](https://github.com/yourusername/wii-autoconvert/releases)
2. Run `WiiAutoConvert.exe`
3. Tools will be downloaded automatically on first run

### Python Installation

```bash
# Clone repository
git clone https://github.com/yourusername/wii-autoconvert.git
cd wii-autoconvert

# Install dependencies
pip install -r requirements.txt

# Run GUI
python main.py

# Or use CLI
python main.py --input game.rvz --output ./wbfs
```

---

## 📖 Usage

### GUI Mode

Launch the application and follow the 4-step wizard:

1. **Select Input**: Drag and drop RVZ/ZIP files or folders
2. **Choose Output**: Select destination directory for WBFS files
3. **Configure Options**: Set up network move and cleanup options (optional)
4. **Monitor Progress**: Watch real-time conversion status and logs

### CLI Mode

```bash
# Convert single file
python main.py --input game.rvz --output ./wbfs

# Convert ZIP file
python main.py --input game.zip --output ./wbfs

# Batch convert directory
python main.py --input ./rvz_collection --output ./wbfs_collection

# Watch mode (auto-convert new files)
python main.py --input ./downloads --output ./wbfs --watch
```

**Common Options:**
- `--keep-iso` - Keep intermediate ISO files
- `--delete-zip` - Delete original ZIP files after conversion
- `--flat` - Flatten output directory structure
- `--no-metadata` - Disable automatic folder organization
- `--verbose` - Enable detailed output

---

## 🛠️ How It Works

WiiAutoConvert uses a two-step conversion process:

1. **RVZ → ISO** (Dolphin Tool)
   - Uses official `dolphin-tool` to convert RVZ to ISO format
   - Validates output and handles errors

2. **ISO → WBFS** (WIT)
   - Uses `wit` (Wiimms ISO Toolset) to convert ISO to WBFS
   - Automatically organizes files with game metadata

3. **Cleanup**
   - Removes intermediate ISO files by default
   - Optional cleanup of original ZIP files

---

## 📋 Requirements

- **Python 3.10+** (for source installation)
- **7-Zip** (for Dolphin tool extraction on Windows)
- **Tools** (auto-downloaded if missing):
  - Dolphin Tool (`DolphinTool.exe` / `dolphin-tool`)
  - WIT (`wit.exe` / `wit`)

---

## 🎨 GUI Features

- **Wizard-Based Workflow**: Step-by-step guided process
- **Dark Theme**: Modern card-based design with glassy aesthetic
- **Drag & Drop**: Easy file selection
- **Progress Dashboard**: Real-time per-file status and logs
- **Watch Mode**: Automatic conversion of new files
- **Network Integration**: Optional file transfer after conversion

---

## 📦 Installation Options

### Option 1: Standalone Executable (Windows)
- Download `WiiAutoConvert.exe` from releases
- No Python installation required
- Tools auto-download on first run

### Option 2: Python Source
- Clone repository
- Install dependencies: `pip install -r requirements.txt`
- Run: `python main.py`

### Option 3: Build from Source
- See [BUILD.md](BUILD.md) for detailed instructions
- Uses PyInstaller for executable creation

---

## 🔧 Automatic Tool Download

WiiAutoConvert automatically detects and downloads required tools:

- ✅ **WIT (Windows)**: Fully automatic download and extraction
- ✅ **Dolphin (Windows)**: Automatic download (requires 7-Zip installed)
- ⚠️ **Linux/macOS**: Manual download required (instructions provided)

Tools are downloaded to `tools/` directory on first run.

---

## 📝 Examples

```bash
# Single file conversion
python main.py --input "Super Mario Galaxy.rvz" --output ./wbfs
# Output: ./wbfs/Super Mario Galaxy [SM2E52]/SM2E52.wbfs

# Batch conversion with cleanup
python main.py --input ./rvz_collection --output ./wbfs --delete-zip

# Watch mode for automatic processing
python main.py --input ./downloads --output ./wbfs --watch
```

---

## 🐛 Troubleshooting

**Tool Not Found?**
- Tools are auto-downloaded on first run
- Check `tools/` directory exists
- Ensure 7-Zip is installed (Windows, for Dolphin extraction)

**Conversion Fails?**
- Check log output for detailed errors
- Verify input RVZ files are not corrupted
- Ensure sufficient disk space for intermediate files

**Permission Errors?**
- On Linux/macOS: `chmod +x tools/dolphin/dolphin-tool tools/wit/wit`

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

Contributions welcome! Please feel free to submit a Pull Request.

---

## 📚 Documentation

- [CHANGELOG.md](CHANGELOG.md) - Version history
- [BUILD.md](BUILD.md) - Build instructions
- [RELEASE_NOTES_v1.1.0.md](RELEASE_NOTES_v1.1.0.md) - Latest release details

---

## ⚠️ Disclaimer

This tool is for converting your own legally obtained ROM files. It does not:
- Download ROMs
- Bypass DRM
- Include emulator features
- Scrape metadata from external sources

---

## 🙏 Acknowledgments

WiiAutoConvert relies on excellent open-source tools:

- **[Dolphin Emulator](https://dolphin-emu.org/)** - Provides `dolphin-tool` for RVZ to ISO conversion
- **[WIT (Wiimms ISO Toolset)](https://wit.wiimm.de/)** - Provides `wit` for ISO to WBFS conversion

Thank you to the Dolphin and WIT development teams for their incredible work!

---

**Made with ❤️ for the Wii homebrew community**
