@echo off
echo ================================
echo E-commerce AI Analytics Setup
echo ================================

echo.
echo [1/4] Creating virtual environment...
python -m venv venv

echo.
echo [2/4] Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo [3/4] Installing dependencies...
pip install -r requirements.txt

echo.
echo [4/4] Setup complete!
echo.
echo Next steps:
echo 1. Get your free Groq API key from: https://console.groq.com
echo 2. Add it to the .env file: GROQ_API_KEY=your_key_here
echo 3. Run the application with: run.bat
echo.
pause
