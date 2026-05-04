@echo off
setlocal enabledelayedexpansion
echo ======================================
echo   OTT AutoClicker - Setup
echo ======================================
echo.

:: 1) Check if python is already on PATH
set PYTHON=
python --version >nul 2>&1
if %errorlevel% equ 0 set PYTHON=python

:: 2) If not on PATH, check registry (works even if PATH not updated yet)
if "!PYTHON!"=="" (
    for %%V in (3.13 3.12 3.11 3.10 3.9 3.8 3.7) do (
        if "!PYTHON!"=="" (
            for /f "tokens=2*" %%A in ('reg query "HKCU\SOFTWARE\Python\PythonCore\%%V\InstallPath" /ve 2^>nul') do (
                if exist "%%Bpython.exe" set PYTHON=%%Bpython.exe
            )
        )
    )
    for %%V in (3.13 3.12 3.11 3.10 3.9 3.8 3.7) do (
        if "!PYTHON!"=="" (
            for /f "tokens=2*" %%A in ('reg query "HKLM\SOFTWARE\Python\PythonCore\%%V\InstallPath" /ve 2^>nul') do (
                if exist "%%Bpython.exe" set PYTHON=%%Bpython.exe
            )
        )
    )
)

:: 3) If still not found - download and run installer, then wait for it to finish
if "!PYTHON!"=="" (
    echo Python not found. Downloading installer...
    curl -L -o python_installer.exe https://www.python.org/ftp/python/3.12.9/python-3.12.9-amd64.exe
    echo.
    echo Python installer launched.
    echo Click Install Now and make sure "Add python.exe to PATH" is checked.
    echo Setup will continue automatically when the installer finishes...
    echo.
    start /wait python_installer.exe
    del python_installer.exe >nul 2>&1

    :: Re-check registry after install
    for %%V in (3.13 3.12 3.11 3.10 3.9 3.8 3.7) do (
        if "!PYTHON!"=="" (
            for /f "tokens=2*" %%A in ('reg query "HKCU\SOFTWARE\Python\PythonCore\%%V\InstallPath" /ve 2^>nul') do (
                if exist "%%Bpython.exe" set PYTHON=%%Bpython.exe
            )
        )
    )
    for %%V in (3.13 3.12 3.11 3.10 3.9 3.8 3.7) do (
        if "!PYTHON!"=="" (
            for /f "tokens=2*" %%A in ('reg query "HKLM\SOFTWARE\Python\PythonCore\%%V\InstallPath" /ve 2^>nul') do (
                if exist "%%Bpython.exe" set PYTHON=%%Bpython.exe
            )
        )
    )

    if "!PYTHON!"=="" (
        echo.
        echo Python not detected after installation. Please run install.bat again.
        pause
        exit /b 1
    )
    echo Python installed: !PYTHON!
)

echo Python: !PYTHON!
echo.
echo Installing dependencies...
"!PYTHON!" -m pip install --upgrade pip >nul 2>&1
"!PYTHON!" -m pip install selenium webdriver-manager
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to install dependencies.
    pause
    exit /b 1
)
echo.
echo ======================================
echo   Done! Starting app...
echo ======================================
"!PYTHON!" ott_autoclicker.py
if %errorlevel% neq 0 (
    echo.
    echo ERROR: App crashed or failed to start. See error above.
    pause
)
