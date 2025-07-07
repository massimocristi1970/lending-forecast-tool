@echo off
echo.
echo ================================================
echo    Setting up Lending Forecast Tool
echo ================================================
echo.

REM Change to the script's directory
cd /d "%~dp0"

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo Python found: 
python --version
echo.

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created successfully!
    echo.
) else (
    echo Virtual environment already exists.
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
if exist "requirements.txt" (
    echo Installing dependencies from requirements.txt...
    pip install -r requirements.txt
) else (
    echo Installing dependencies manually...
    pip install streamlit pandas matplotlib numpy xlsxwriter
)

if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo ================================================
echo    Setup Complete!
echo ================================================
echo.
echo Next steps:
echo 1. Make sure app.py is in this directory
echo 2. Double-click start_app.bat to run the application
echo.
echo Or run manually:
echo   venv\Scripts\activate
echo   streamlit run app.py
echo.
pause