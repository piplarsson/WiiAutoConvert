@echo off
REM WiiAutoConvert - Launch CLI
REM Starts the command-line interface

echo ========================================
echo WiiAutoConvert - CLI Mode
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7 or higher
    pause
    exit /b 1
)

REM Check if tools exist
if not exist "tools\dolphin\DolphinTool.exe" (
    echo ERROR: DolphinTool.exe not found!
    echo Please run setup.bat first
    pause
    exit /b 1
)

if not exist "tools\wit\wit.exe" (
    echo ERROR: wit.exe not found!
    echo Please run setup.bat first
    pause
    exit /b 1
)

REM Check if source files exist
if not exist "rvz2wbfs.py" (
    echo ERROR: rvz2wbfs.py not found!
    echo Please ensure you're running from the project root directory
    pause
    exit /b 1
)

REM If no arguments provided, show help
if "%~1"=="" (
    echo No arguments provided. Showing help...
    echo.
    python rvz2wbfs.py --help
    echo.
    echo Example usage:
    echo   start_cli.bat --input game.rvz --output .\wbfs
    echo   start_cli.bat --input .\rvz_folder --output .\wbfs_folder --keep-iso
    pause
    exit /b 0
)

REM Launch CLI with provided arguments
python rvz2wbfs.py %*

REM Check exit code
if errorlevel 1 (
    echo.
    echo ERROR: Conversion failed
    pause
    exit /b 1
)

exit /b 0

