@echo off
cd backend
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate
    echo Installing dependencies...
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate
)

if not exist ".env" (
    echo WARNING: .env file not found! Please copy .env.example to .env and add your API key.
    copy .env.example .env
)

echo Starting Server...
uvicorn main:app --reload --host 127.0.0.1 --port 8000
pause
