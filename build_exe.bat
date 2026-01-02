@echo off
REM Build script for creating WiiAutoConvert executable (Windows)
REM This script uses PyInstaller to create a standalone .exe file

echo ========================================
echo Building WiiAutoConvert Executable
echo ========================================
echo.

REM Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    echo.
    python -m pip install pyinstaller
    if errorlevel 1 (
        echo.
        echo ========================================
        echo Failed to install PyInstaller
        echo ========================================
        echo.
        echo Please install manually with:
        echo   pip install pyinstaller
        echo.
        pause
        exit /b 1
    )
    echo.
    echo PyInstaller installed successfully!
    echo.
) else (
    echo PyInstaller is already installed.
    echo.
)

echo.
echo Building executable...
echo.

REM Create tools directory structure if it doesn't exist (for build, tools will be auto-downloaded)
if not exist "tools" mkdir tools
if not exist "tools\dolphin" mkdir tools\dolphin
if not exist "tools\wit" mkdir tools\wit

REM Create build log file (use unique name to avoid locks)
set BUILD_LOG=build_%date:~-4,4%%date:~-7,2%%date:~-10,2%_%time:~0,2%%time:~3,2%%time:~6,2%.log
set BUILD_LOG=%BUILD_LOG: =0%
echo ======================================== > %BUILD_LOG%
echo Build started: %date% %time% >> %BUILD_LOG%
echo ======================================== >> %BUILD_LOG%
echo. >> %BUILD_LOG%

REM Run PyInstaller with the spec file (using python -m to ensure it works)
echo Running PyInstaller... >> %BUILD_LOG%
python -m PyInstaller --clean WiiAutoConvert.spec >> %BUILD_LOG% 2>&1
set BUILD_EXIT=%ERRORLEVEL%

echo. >> %BUILD_LOG%
echo Build finished: %date% %time% >> %BUILD_LOG%
echo Exit code: %BUILD_EXIT% >> %BUILD_LOG%

if %BUILD_EXIT% neq 0 (
    echo.
    echo ========================================
    echo Build failed!
    echo ========================================
    echo.
    echo Build log saved to: %BUILD_LOG%
    echo Please check the log file for details.
    echo.
    type %BUILD_LOG% | findstr /C:"ERROR" /C:"Error" /C:"error" /C:"Traceback" /C:"Exception"
    echo.
    pause
    exit /b 1
) else (
    echo.
    echo ========================================
    echo Build successful!
    echo Executable: dist\WiiAutoConvert.exe
    echo Build log: %BUILD_LOG%
    echo ========================================
    echo.
    echo NOTE: The executable includes automatic tool downloading.
    echo Tools (Dolphin and WIT) will be downloaded automatically on first run.
    echo.
    echo IMPORTANT: The tools/ folder being empty is EXPECTED and CORRECT.
    echo - We cannot distribute Dolphin/WIT due to licensing
    echo - Tools will be auto-downloaded when you run the executable
    echo - The tools/ folder will be populated automatically on first run
    echo.
)

pause

