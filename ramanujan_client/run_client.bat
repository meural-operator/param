@echo off
setlocal
cd /d "%~dp0"

echo ==================================================
echo       Ramanujan@Home - One-Click Compute Node      
echo ==================================================

:: 1. Check if the dedicated Python 3.13 runtime exists locally
if not exist "python_313\python.exe" (
    echo [*] Dedicated Python 3.13 Runtime not found.
    echo [*] Downloading Python 3.13.0 directly from python.org...
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.13.0/python-3.13.0-amd64.exe' -OutFile 'python-installer.exe'"
    if not exist "python-installer.exe" (
        echo [!] Failed to download Python. Check your internet connection.
        pause
        exit /b 1
    )
    
    echo [*] Installing isolated Python 3.13 baseline...
    start /wait python-installer.exe /quiet InstallAllUsers=0 Include_pip=1 TargetDir="%~dp0python_313"
    del python-installer.exe
    
    if not exist "python_313\python.exe" (
        echo [!] Python 3.13 installation failed.
        pause
        exit /b 1
    )
)

:: 2. Fast-check if the isolated virtual environment exists
if not exist "client_env\Scripts\python.exe" (
    echo [*] First-time standalone setup detected. Bootstrapping AI Environment...
    :: We use our newly isolated Python 3.13 baseline to trigger the auto-installer wrapper
    python_313\python.exe setup\autoinstaller.py
    if %errorlevel% neq 0 (
        echo [!] Autoinstaller failed.
        pause
        exit /b 1
    )
)

echo [*] Launching Client Application...
client_env\Scripts\python.exe ramanujan_client.py

pause
