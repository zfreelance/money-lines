@echo off

:: Check if .venv directory exists
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
) else (
    echo .venv already exists.
)

:: Activate the virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

:: Wait for user input
echo Virtual environment is active.

pip install -r requirements.txt

python src/main.py

echo Press any key to exit...
pause >nul