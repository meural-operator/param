@echo off
setlocal DisableDelayedExpansion
cd /d "%~dp0"

echo ==================================================
echo           Param@Home - One-Click Launcher          
echo ==================================================
echo.

if not exist "clients\run_node.bat" (
    echo [!] Error: clients\run_node.bat not found.
    echo [!] Please ensure you are running this from the repository root.
    pause
    exit /b 1
)

echo [*] Initializing Param Node from root...
cd clients
call run_node.bat
