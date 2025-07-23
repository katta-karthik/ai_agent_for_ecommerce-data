@echo off
echo ===============================================
echo Pushing E-commerce AI Analytics to GitHub
echo Repository: https://github.com/katta-karthik/ecommerce_data_agent
echo ===============================================

echo.
echo [1/6] Initializing Git repository...
git init

echo.
echo [2/6] Adding remote repository...
git remote add origin https://github.com/katta-karthik/ecommerce_data_agent.git

echo.
echo [3/6] Adding all files to staging...
git add .

echo.
echo [4/6] Creating initial commit...
git commit -m "Initial commit: E-commerce AI Analytics System

Features:
- Natural language to SQL conversion using Groq AI
- Streamlit web interface with professional UI
- FastAPI REST endpoints
- Modular architecture (core/ui/utils/data)
- Professional data visualizations
- CMD-friendly setup scripts
- Secure environment variable management

Tech Stack:
- Groq AI (Llama 3.1-70B)
- Streamlit + FastAPI
- SQLite database
- Matplotlib + Seaborn
- LangChain integration"

echo.
echo [5/6] Pushing to GitHub...
git branch -M main
git push -u origin main

echo.
echo [6/6] Complete!
echo Your code is now available at:
echo https://github.com/katta-karthik/ecommerce_data_agent
echo.
pause
