@echo off
echo Installing PyInstaller...
python -m pip install pyinstaller >nul 2>&1

echo Building AutoClicker.exe...
python -m PyInstaller --onefile --noconsole --icon=favicon.ico --name=AutoClicker launcher.py

echo Copying exe...
copy /Y dist\AutoClicker.exe AutoClicker.exe

echo Cleaning up...
rmdir /s /q dist
rmdir /s /q build
del AutoClicker.spec

echo.
echo Done! AutoClicker.exe is ready.
pause
