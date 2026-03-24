@echo off
setlocal DisableDelayedExpansion
cd /d "%~dp0"

echo ==================================================
echo        Ramanujan@Home - One-Click Compute Node          
echo ==================================================

set "PYTHON_CMD="

:: 1. Check Local AppData Python installation
if exist "%LOCALAPPDATA%\ParamPython\python.exe" (
    "%LOCALAPPDATA%\ParamPython\python.exe" -c "import sys; sys.exit(0 if sys.version_info.major == 3 and sys.version_info.minor == 13 else 1)" >nul 2>&1
    if not errorlevel 1 set "PYTHON_CMD=%LOCALAPPDATA%\ParamPython\python.exe"
)

:: 2. Download and Install Micromamba Python 3.13 if missing
if not "%PYTHON_CMD%"=="" goto :INSTALL_DONE

echo [*] Python 3.13 isolated runtime not found.
echo [*] Downloading portable MicroMamba engine for clean installation...
if not exist "micromamba.tar.bz2" (
    curl.exe -k -L -o micromamba.tar.bz2 https://micro.mamba.pm/api/micromamba/win-64/latest
)

echo [*] Extracting MicroMamba...
tar -xf micromamba.tar.bz2
if not exist "Library\bin\micromamba.exe" (
    echo [!] Failed to extract MicroMamba container.
    pause
    exit /b 1
)

echo [*] Resolving flawless Python 3.13 environment via Conda-Forge...
Library\bin\micromamba.exe create -p "%LOCALAPPDATA%\ParamPython" python=3.13 pip -c conda-forge -y

if exist "%LOCALAPPDATA%\ParamPython\python.exe" (
    set "PYTHON_CMD=%LOCALAPPDATA%\ParamPython\python.exe"
    :: Cleanup
    if exist micromamba.tar.bz2 del micromamba.tar.bz2
    if exist Library rmdir /s /q Library
    if exist info rmdir /s /q info
) else (
    echo [!] MicroMamba Python 3.13 resolution failed.
    pause
    exit /b 1
)

:INSTALL_DONE
echo [*] Enforcing Python Runtime: "%PYTHON_CMD%"

:: 4. Fast-check and Setup Virtual Environment
if not exist "%USERPROFILE%\.param_env\Scripts\python.exe" (
    echo [*] First-time standalone setup detected. Bootstrapping AI Environment...
    "%PYTHON_CMD%" setup\autoinstaller.py
    if errorlevel 1 (
        echo [!] Autoinstaller failed. Please check your system Python installation.
        pause
        exit /b 1
    )
)

:: 5. Generate Target Math Database if Missing
if not exist "..\euler_mascheroni.db" (
    echo [*] Generating Local LHS Verification Database ^(One-time math setup, takes ~10s^)...
    "%USERPROFILE%\.param_env\Scripts\python.exe" ..\scripts\seed_euler_mascheroni_db.py
)

echo [*] Launching Client Application...
"%USERPROFILE%\.param_env\Scripts\python.exe" edge_node.py

pause
