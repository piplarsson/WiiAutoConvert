@echo off
REM WiiAutoConvert - Launch GUI
REM Starts the desktop user interface

echo ========================================
echo WiiAutoConvert - Starting GUI...
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
if not exist "main.py" (
    echo ERROR: main.py not found!
    echo Please ensure you're running from the project root directory
    pause
    exit /b 1
)

REM Launch the GUI
echo Launching WiiAutoConvert GUI...
echo.
python main.py

REM Check exit code
if errorlevel 1 (
    echo.
    echo ERROR: Application exited with an error
    pause
    exit /b 1
)

exit /b 0

