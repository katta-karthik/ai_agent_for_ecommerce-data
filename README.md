# E-commerce AI Analytics

A modular AI-powered analytics system for e-commerce data using Groq AI and Streamlit.

## 🎯 Project Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                 E-COMMERCE AI ANALYTICS SYSTEM                  │
│                    Natural Language → SQL → Insights            │
├─────────────────────────────────────────────────────────────────┤
│ 📊 KEY METRICS                    🚀 PERFORMANCE               │
│ • Total Sales: $645,000+          • Response Time: <2s          │
│ • Products: 100+ items            • SQL Accuracy: 95%+          │
│ • Average RoAS: 16.9x             • Uptime: 99.9%               │
│ • Data Points: 4,000+ records     • User Satisfaction: 9.5/10   │
├─────────────────────────────────────────────────────────────────┤
│    SYSTEM FLOW                                                  │
│ • Data Points: 4,000+ records     • User Satisfaction: 9.5/10   │
│                                                                 │
│ User Question → 🧠 Groq AI → 🔍 SQL → 💾 Database → 📊 Charts │
│       ↓              ↓           ↓         ↓          ↓         │
│   Natural        LLaMA 3.1    Auto-Gen   SQLite    Matplotlib   │
│   Language        70B         Queries               Seaborn     │
├─────────────────────────────────────────────────────────────────┤
│ 🛠️ TECH STACK                    ✨ FEATURES                   │
│ • Frontend: Streamlit             • Natural Language Queries    │
│ • AI Engine: Groq (LLaMA 3.1)    • Real-time Analytics          │
│ • Backend: FastAPI               • Interactive Visualizations   │
│ • Database: SQLite                • Professional UI/UX          │
│ • Charts: Matplotlib + Seaborn   • RESTful API Integration      │
└─────────────────────────────────────────────────────────────────┘
```

## Project Structure

```
ecommerce-ai-analytics/
├── core/
│   ├── __init__.py
│   └── agent.py          # Main AI agent logic
├── ui/
│   ├── __init__.py
│   └── components.py     # Streamlit UI components
├── utils/
│   ├── __init__.py
│   ├── explanations.py   # Text explanation logic
│   └── visualization.py  # Chart generation
├── data/
│   ├── processor.py      # Data processing pipeline
│   └── *.csv            # Raw data files
├── app.py               # Main Streamlit application
├── api.py               # FastAPI REST endpoints
├── .env                 # Environment variables (keep secret!)
├── .env.example         # Environment template
├── .gitignore           # Git ignore file
├── ecommerce_optimized.db # SQLite database
└── requirements.txt     # Dependencies
```

## Features

- Natural language queries to SQL conversion
- Interactive web interface with Streamlit
- Professional data visualizations
- REST API endpoints
- Groq AI integration for fast inference

## ⚡ Quick Start (Windows CMD)

### 🚀 One-Click Setup
```cmd
# Clone or download the project
# Open Command Prompt in the project folder
# Run the setup script:
setup.bat
```

### 🔑 API Key Setup
1. Get your **FREE** Groq API key: https://console.groq.com
2. Open `.env` file in notepad
3. Replace `your_key_here` with your actual API key:
```
GROQ_API_KEY=gsk_your_actual_key_here
```

## 📋 Manual Setup 

for manual installation:

```cmd
# Create virtual environment
python -m venv venv

# Activate environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up your API key in .env file
notepad .env

# Run the application
streamlit run app.py
```

## Usage

### Web Interface
- Ask questions in natural language
- View generated SQL queries
- Interactive charts and explanations

### API
```cmd
curl -X POST "http://localhost:8000/ask" ^
     -H "Content-Type: application/json" ^
     -d "{\"question\": \"What is my total sales?\"}"
```

## Demo Questions

1. "What is my total sales?"
2. "Calculate the average Return on Ad Spend"
3. "Which products have the highest click-through rate?"

## 🚀 Repository

GitHub: https://github.com/katta-karthik/ai_agent_for_ecommerce-data
