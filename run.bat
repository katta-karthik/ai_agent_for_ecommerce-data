@echo off
echo ================================
echo Starting E-commerce AI Analytics
echo ================================

echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Starting Streamlit application...
echo Open your browser to: http://localhost:8501
echo Press Ctrl+C to stop the application
echo.

streamlit run app.py
