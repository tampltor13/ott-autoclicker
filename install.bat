@echo off
echo ======================================
echo   OTT AutoClicker - Setup
echo ======================================
echo.
echo Installing dependencies...
python -m pip install --upgrade pip
python -m pip install selenium
echo.
echo ======================================
echo   Done! Starting app...
echo ======================================
python ott_autoclicker.py
