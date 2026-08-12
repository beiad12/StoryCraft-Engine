@echo off
setlocal

rem One-shot dependency installer for Windows. Double-click to run, or
rem execute from CMD/PowerShell. Prefers `uv`; falls back to a plain
rem .venv + pip install when `uv` isn't available.

set "CURRENT_DIR=%~dp0"
cd /d "%CURRENT_DIR%"

echo ***** MoneyPrinterTurbo dependency installer *****

where uv >nul 2>nul
if not errorlevel 1 (
    echo ***** uv found, installing dependencies with 'uv sync --frozen' *****
    uv sync --frozen
    if errorlevel 1 goto :failed
    goto :config
)

set "PYTHON_CMD="
where python >nul 2>nul
if not errorlevel 1 set "PYTHON_CMD=python"
if not defined PYTHON_CMD (
    where py >nul 2>nul
    if not errorlevel 1 set "PYTHON_CMD=py -3"
)
if not defined PYTHON_CMD (
    echo ***** No Python interpreter found. Install Python 3.10+ (or uv: https://docs.astral.sh/uv/) and re-run this script. *****
    goto :failed
)

echo ***** uv not found, falling back to %PYTHON_CMD% + pip *****

if not exist "%CURRENT_DIR%\.venv\Scripts\python.exe" (
    echo ***** Creating virtual environment in .venv *****
    %PYTHON_CMD% -m venv .venv
)

"%CURRENT_DIR%\.venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 goto :failed
"%CURRENT_DIR%\.venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto :failed

:config
if not exist "%CURRENT_DIR%\config.toml" (
    echo ***** Creating config.toml from config.example.toml *****
    copy /y "%CURRENT_DIR%\config.example.toml" "%CURRENT_DIR%\config.toml" >nul
)

echo ***** Install complete! Run webui.bat to start the WebUI. *****
pause
exit /b 0

:failed
echo ***** Install failed, see the errors above. *****
pause
exit /b 1
