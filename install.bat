@echo off
echo ======================================
echo   OTT AutoClicker - Setup
echo ======================================
echo.

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found. Downloading installer...
    curl -L -o python_installer.exe https://www.python.org/ftp/python/3.12.9/python-3.12.9-amd64.exe
    echo.
    echo Python installer downloaded: python_installer.exe
    echo Please install it ^(check "Add Python to PATH"^) then run install.bat again.
    start python_installer.exe
    pause
    exit /b
)

echo Installing dependencies...
python -m pip install --upgrade pip
python -m pip install selenium webdriver-manager
echo.
echo ======================================
echo   Done! Starting app...
echo ======================================
python ott_autoclicker.py
