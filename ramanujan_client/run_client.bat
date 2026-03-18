@echo off
echo ==================================================
echo       Ramanujan@Home - One-Click Compute Node      
echo ==================================================

:: Fast-check if the isolated virtual environment exists
if not exist "client_env\Scripts\python.exe" (
    echo [*] First-time standalone setup detected. Bootstrapping AI Environment...
    :: We use the system Python to trigger the auto-installer wrapper
    python setup\autoinstaller.py
    if %errorlevel% neq 0 (
        echo [!] Autoinstaller failed. Please check your system Python installation.
        pause
        exit /b %errorlevel%
    )
)

echo [*] Launching Client Application...
client_env\Scripts\python.exe ramanujan_client.py

pause
