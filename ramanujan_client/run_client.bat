@echo off
setlocal
cd /d "%~dp0"

echo ==================================================
echo       Ramanujan@Home - One-Click Compute Node      
echo ==================================================

:: Fast-check if the globally rooted virtual environment exists
if not exist "%USERPROFILE%\.ramanujan_env\Scripts\python.exe" (
    echo [*] First-time standalone setup detected. Bootstrapping AI Environment...
    :: We dynamically execute python so it natively grabs your active Conda environment or Global installation.
    python setup\autoinstaller.py
    if %errorlevel% neq 0 (
        echo [!] Autoinstaller failed. Please check your system Python installation.
        pause
        exit /b 1
    )
)

echo [*] Launching Client Application...
"%USERPROFILE%\.ramanujan_env\Scripts\python.exe" ramanujan_client.py

pause
