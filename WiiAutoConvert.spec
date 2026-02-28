# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for WiiAutoConvert
Merged version:
- Preserves original build logging and robust error handling
- Keeps original optional tools/ bundling behavior
- Adds proper collection of CustomTkinter and tkinterdnd2 assets/hooks
- Adds EXE icon automatically if WiiAutoConvert.ico exists
"""

import sys
import logging
from pathlib import Path
from PyInstaller.utils.hooks import collect_all

# Set up build logging
# Note: Don't use FileHandler here since batch script may already redirect stdout/stderr.
# All print() and logging will be captured by the caller's redirection.
build_logger = logging.getLogger('build')
build_logger.setLevel(logging.DEBUG)

# Remove existing handlers
build_logger.handlers.clear()

# Only use console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
build_logger.addHandler(console_handler)

build_logger.info("=" * 60)
build_logger.info("PyInstaller Build Started")
build_logger.info(f"Python: {sys.version}")
build_logger.info(f"Platform: {sys.platform}")
build_logger.info(f"Working directory: {Path.cwd()}")

block_cipher = None

# Prepare datas list - only include tools directory if it exists and has content.
# Tools will be downloaded automatically at runtime if missing.
datas = []
tools_dir = Path('tools')
try:
    if tools_dir.exists() and any(tools_dir.iterdir()):
        datas.append(('tools', 'tools'))
        build_logger.info(f"Including tools directory: {tools_dir} (has content)")
    else:
        build_logger.info(
            "tools/ directory is empty or missing (expected in many cases). "
            "Tools can be downloaded automatically at runtime."
        )
except Exception as e:
    build_logger.warning(f"Error checking tools directory: {e}")
    build_logger.info("Continuing without bundled tools directory")

# Prepare binaries and collect package assets/hooks
binaries = []
extra_hiddenimports = []

for pkg in ('customtkinter', 'tkinterdnd2'):
    try:
        pkg_datas, pkg_binaries, pkg_hiddenimports = collect_all(pkg)
        datas += pkg_datas
        binaries += pkg_binaries
        extra_hiddenimports += pkg_hiddenimports
        build_logger.info(
            f"Collected PyInstaller assets for {pkg}: "
            f"{len(pkg_datas)} datas, {len(pkg_binaries)} binaries, "
            f"{len(pkg_hiddenimports)} hidden imports"
        )
    except Exception as e:
        build_logger.warning(f"Could not collect assets for {pkg}: {e}")

# Static hidden imports we want regardless of hook auto-detection
hiddenimports = [
    'customtkinter',
    'tkinterdnd2',
    'tkinter',
    'tkinter.filedialog',
    'tkinter.messagebox',
    'tkinter.scrolledtext',
    'src.tool_downloader',
    'urllib.request',
    'urllib.error',
    'zipfile',
    'shutil',
] + extra_hiddenimports

# Optional icon
icon_file = Path('WiiAutoConvert.ico')
if icon_file.exists():
    exe_icon = str(icon_file)
    build_logger.info(f"Using icon: {icon_file}")
else:
    exe_icon = None
    build_logger.info("No WiiAutoConvert.ico found - building without custom icon")

try:
    build_logger.info("Starting Analysis phase...")
    build_logger.debug(f"Data files: {len(datas)} entries")
    build_logger.debug(f"Binary files: {len(binaries)} entries")
    build_logger.debug(f"Hidden imports: {len(hiddenimports)} entries")

    a = Analysis(
        ['main.py'],
        pathex=[],
        binaries=binaries,
        datas=datas,
        hiddenimports=hiddenimports,
        hookspath=[],
        hooksconfig={},
        runtime_hooks=[],
        excludes=[],
        win_no_prefer_redirects=False,
        win_private_assemblies=False,
        cipher=block_cipher,
        noarchive=False,
    )
    build_logger.info("Analysis phase completed successfully")
except Exception as e:
    build_logger.error(f"Analysis phase failed: {e}", exc_info=True)
    raise

try:
    build_logger.info("Building PYZ archive...")
    pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
    build_logger.info("PYZ archive built successfully")
except Exception as e:
    build_logger.error(f"PYZ build failed: {e}", exc_info=True)
    raise

try:
    build_logger.info("Building EXE...")
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.zipfiles,
        a.datas,
        [],
        name='WiiAutoConvert',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        upx_exclude=[],
        runtime_tmpdir=None,
        console=False,  # No console window (GUI mode)
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon=exe_icon,
    )
    build_logger.info("=" * 60)
    build_logger.info("Build completed successfully!")
    build_logger.info("Executable location: dist/WiiAutoConvert.exe")
    build_logger.info("=" * 60)
except Exception as e:
    build_logger.error("=" * 60)
    build_logger.error("Build failed during EXE creation!")
    build_logger.error(f"Error: {e}", exc_info=True)
    build_logger.error("=" * 60)
    raise
