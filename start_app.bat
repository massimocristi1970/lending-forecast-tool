@echo off
echo.
echo ================================================
echo    Starting Lending Forecast Tool
echo ================================================
echo.

REM Change to the script's directory
cd /d "%~dp0"

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please run setup_project.bat first or create venv manually
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if app.py exists
if not exist "app.py" (
    echo ERROR: app.py not found!
    echo Please ensure app.py is in the project directory
    echo.
    pause
    exit /b 1
)

REM Start Streamlit app
echo Starting Streamlit application...
echo.
echo The app will open in your browser at: http://localhost:8501
echo.
echo To stop the app, press Ctrl+C in this window
echo ================================================
echo.

streamlit run app.py

REM If streamlit command fails
if errorlevel 1 (
    echo.
    echo ERROR: Failed to start Streamlit
    echo Make sure all dependencies are installed
    echo Try running: pip install -r requirements.txt
    echo.
)

echo.
echo App stopped. Press any key to close...
pause >nul