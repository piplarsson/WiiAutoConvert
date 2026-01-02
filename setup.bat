@echo off
REM WiiAutoConvert Setup Script
REM Verifies environment and tools are ready

echo ========================================
echo WiiAutoConvert Setup
echo ========================================
echo.

REM Check Python installation
echo [1/4] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7 or higher
    pause
    exit /b 1
)
python --version
echo Python found!
echo.

REM Check Python version (3.7+)
echo [2/4] Checking Python version...
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Python version: %PYTHON_VERSION%
echo.

REM Check bundled tools
echo [3/4] Checking bundled tools...
set TOOLS_OK=1

if not exist "tools\dolphin\DolphinTool.exe" (
    echo WARNING: DolphinTool.exe not found at tools\dolphin\DolphinTool.exe
    set TOOLS_OK=0
) else (
    echo [OK] DolphinTool.exe found
)

if not exist "tools\wit\wit.exe" (
    echo WARNING: wit.exe not found at tools\wit\wit.exe
    set TOOLS_OK=0
) else (
    echo [OK] wit.exe found
)

if %TOOLS_OK%==0 (
    echo.
    echo ERROR: Required tools are missing!
    echo Please ensure tools are bundled in the tools\ directory
    pause
    exit /b 1
)
echo.

REM Check source files
echo [4/4] Checking source files...
if not exist "src\conversion_engine.py" (
    echo ERROR: Source files not found!
    pause
    exit /b 1
)
if not exist "src\ui\app_wizard.py" (
    echo ERROR: UI module not found!
    pause
    exit /b 1
)
if not exist "src\cli.py" (
    echo ERROR: CLI module not found!
    pause
    exit /b 1
)
echo [OK] Source files found
echo.

echo ========================================
echo Setup complete! Everything looks good.
echo ========================================
echo.
echo You can now run:
echo   - start_ui.bat     to launch the GUI
echo   - rvz2wbfs.py     for CLI usage
echo.
pause

