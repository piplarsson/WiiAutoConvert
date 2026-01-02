#!/usr/bin/env python3
"""
WiiAutoConvert - Main Entry Point
RVZ to WBFS Converter for Nintendo Wii ROMs
"""

import sys
from pathlib import Path

# Add project root to path so we can import src as a package
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

if __name__ == "__main__":
    # Check for required tools on startup (non-blocking for CLI)
    try:
        from src.tool_downloader import ToolDownloader
        import sys
        from pathlib import Path
        
        # Determine project root (works for both script and executable)
        if getattr(sys, 'frozen', False):
            project_root = Path(sys.executable).parent
        else:
            project_root = Path(__file__).parent
        
        downloader = ToolDownloader(project_root)
        dolphin_ok = downloader.check_dolphin_tool()
        wit_ok = downloader.check_wit()
        
        if not dolphin_ok or not wit_ok:
            missing = []
            if not dolphin_ok:
                missing.append("Dolphin Tool")
            if not wit_ok:
                missing.append("WIT")
            
            print(f"WARNING: Missing required tools: {', '.join(missing)}")
            print("The application will attempt to download them automatically.")
            print(f"Check tool_download.log in {project_root} for details.")
            print("If download fails, please install manually:")
            if not dolphin_ok:
                print("  • Dolphin: https://dolphin-emu.org/download/")
            if not wit_ok:
                print("  • WIT: https://wit.wiimm.de/")
            print()
    except Exception as e:
        # Don't block startup if tool check fails, but log it
        import traceback
        error_log_path = Path(__file__).parent / "tool_download_error.txt"
        try:
            with open(error_log_path, 'a', encoding='utf-8') as f:
                f.write(f"Error during tool check: {e}\n")
                f.write(traceback.format_exc())
        except:
            pass
        print(f"Note: Could not check for tools: {e}")
        print(f"Error details saved to: {error_log_path}")
    
    # Check if running with CLI flag or if arguments suggest CLI mode
    if len(sys.argv) > 1:
        # Check for CLI-specific arguments
        cli_args = ["--input", "-i", "--output", "-o", "--help", "-h"]
        if any(arg in sys.argv for arg in cli_args) or sys.argv[1] == "--cli":
            # CLI mode
            from src.cli import main
            main()
        else:
            # Try GUI mode
            try:
                from src.ui import main
                main()
            except ImportError as e:
                print(f"Error importing GUI: {e}")
                print("Falling back to CLI mode...")
                from src.cli import main
                main()
    else:
        # GUI mode (default when no arguments)
        try:
            from src.ui import main
            main()
        except ImportError as e:
            print(f"Error importing GUI: {e}")
            print("Falling back to CLI mode...")
            from src.cli import main
            main()

