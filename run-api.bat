@echo off
echo ================================
echo Starting E-commerce AI Analytics API
echo ================================

echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Starting FastAPI server...
echo API will be available at: http://localhost:8000
echo API docs at: http://localhost:8000/docs
echo Press Ctrl+C to stop the server
echo.

python api.py
