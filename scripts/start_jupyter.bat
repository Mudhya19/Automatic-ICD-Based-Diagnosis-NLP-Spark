@echo off

REM Change to project directory
cd /d "%~dp0\.."

echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo Starting Jupyter Lab...
call jupyter-lab.exe
