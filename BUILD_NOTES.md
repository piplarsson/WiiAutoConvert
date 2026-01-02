# Build Notes

## Tools Directory During Build

**IMPORTANT**: The `tools/` directory being empty during and after the build is **EXPECTED and CORRECT**.

### Why the tools folder is empty:

1. **Licensing**: We cannot distribute Dolphin and WIT tools with the executable due to their licenses
2. **Auto-download**: Tools are downloaded automatically when the executable runs for the first time
3. **Build process**: The build only needs the directory structure, not the actual tool binaries

### What happens:

1. **During Build**: 
   - PyInstaller sees the `tools/` directory (even if empty)
   - It includes the directory structure in the build
   - This is fine - empty directories are allowed

2. **When Executable Runs**:
   - Application checks for tools in `tools/dolphin/` and `tools/wit/`
   - If missing, it automatically downloads WIT (Windows)
   - Provides instructions for Dolphin (manual download required)
   - Tools are saved to the same directory as the executable

### Testing the Executable:

1. Copy `dist/WiiAutoConvert.exe` to a test folder
2. Run the executable
3. On first run, it will:
   - Detect missing tools
   - Show a dialog asking to download
   - Download WIT automatically (Windows)
   - Create `tools/wit/wit.exe` in the executable's directory
4. Check `tool_download.log` in the executable's directory for details

### Expected Behavior:

- ✅ Build completes successfully with empty `tools/` folder
- ✅ Executable runs and detects missing tools
- ✅ Tools are downloaded to executable's directory on first run
- ✅ `tools/` folder is populated automatically

If tools are not downloading when you run the executable, check:
- `tool_download.log` in the executable's directory
- Internet connection
- Firewall/antivirus blocking downloads
- File permissions on the executable's directory

