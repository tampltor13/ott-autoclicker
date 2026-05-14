@echo off

:: Try to find Python — check common install locations if not in PATH
set PYTHON=
where python >nul 2>&1 && set PYTHON=python
if not defined PYTHON (
    for %%P in (
        "%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
        "%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
        "%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
        "%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
        "C:\Python313\python.exe"
        "C:\Python312\python.exe"
        "C:\Python311\python.exe"
        "C:\Python310\python.exe"
    ) do (
        if exist %%P (
            set PYTHON=%%P
            goto :found
        )
    )
)
:found

if not defined PYTHON (
    echo ERROR: Python not found. Please install Python or repair your installation.
    pause
    exit /b 1
)

echo Using Python: %PYTHON%

echo Installing PyInstaller...
%PYTHON% -m pip install pyinstaller >nul 2>&1

echo Building AutoClicker.exe...
%PYTHON% -m PyInstaller --onefile --noconsole --icon=favicon.ico --name=AutoClicker launcher.py

echo Copying exe...
copy /Y dist\AutoClicker.exe AutoClicker.exe

echo Cleaning up...
rmdir /s /q dist
rmdir /s /q build
del AutoClicker.spec

echo.
echo Done! AutoClicker.exe is ready.
pause
