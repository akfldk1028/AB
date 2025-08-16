@echo off
echo ===========================================
echo    A2A Multi-Agent System Starter v2.0
echo    Official Google A2A Protocol
echo ===========================================
echo.

REM Change to project directory
cd /d "D:\Data\05_CGXR\A2A\LangGrpah"

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please run: python -m venv venv
    echo Then: pip install -r A2A-LangGraph\requirements.txt
    pause
    exit /b 1
)

REM Activate virtual environment
echo [1/4] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

REM Change to A2A-LangGraph directory
cd A2A-LangGraph

REM Check if .env file exists
if not exist ".env" (
    echo WARNING: .env file not found!
    echo Please create .env file with: OPENAI_API_KEY=your_key_here
    pause
)

echo [2/4] Starting Currency Agent (Port 8000)...
start "Currency Agent" powershell -ExecutionPolicy Bypass -Command "& ..\..\venv\Scripts\Activate.ps1; Write-Host 'Currency Agent - Official A2A Protocol' -ForegroundColor Green; python agents\worker_agent.py"

REM Wait for Currency Agent to start
timeout /t 4 /nobreak >nul

echo [3/4] Starting Weather Agent (Port 8001)...
start "Weather Agent" powershell -ExecutionPolicy Bypass -Command "& ..\..\venv\Scripts\Activate.ps1; Write-Host 'Weather Agent - Official A2A Protocol' -ForegroundColor Cyan; python agents\weather\weather_agent.py"

REM Wait for Weather Agent to start
timeout /t 4 /nobreak >nul

echo [4/4] Starting Host Agent...
echo.
echo =============================================
echo   🎉 A2A Multi-Agent System Ready!
echo =============================================
echo.
echo 🏦 Currency Agent: http://localhost:8000
echo    - Currency conversion (USD, EUR, GBP, JPY, KRW, etc.)
echo    - Official A2A Protocol (message/send)
echo    - MCP Tools Integration
echo.
echo 🌤️ Weather Agent: http://localhost:8001  
echo    - Weather information (Seoul, Tokyo, NY, London, etc.)
echo    - Official A2A Protocol (message/send)
echo    - Real-time data
echo.
echo 🎛️ Host Agent: Interactive Console
echo    - LangGraph ReAct Engine
echo    - Multi-Agent Coordination
echo    - GPT-4o Integration
echo.
echo =============================================
echo 💬 Test Examples:
echo   "Convert 100 USD to EUR"
echo   "What's the weather in Seoul?"
echo   "Planning trip to Tokyo - need weather and 500 USD in yen"
echo.
echo Type 'quit', 'exit', or 'bye' to stop all services.
echo =============================================
echo.

python host\main.py

echo.
echo 🛑 Host Agent stopped.
echo All services should be shut down.
echo Press any key to exit...
pause >nul