@echo off
echo ================================================================
echo   Claude CLI Multi-Agent System - Agent Server Launcher
echo ================================================================
echo.

cd /d "D:\Data\05_CGXR\A2A\LangGrpah\A2A-LangGraph"

echo [1/3] Starting Frontend Agent on port 8010...
start "Frontend Agent (Port 8010)" cmd /k "python -m agents.claude_cli.frontend.server"

echo [2/3] Starting Backend Agent on port 8021...
start "Backend Agent (Port 8021)" cmd /k "python -m agents.claude_cli.backend.server"

echo [3/3] Starting Unity Agent on port 8012...
start "Unity Agent (Port 8012)" cmd /k "python -m agents.claude_cli.unity.server"

echo.
echo ================================================================
echo   All agents are starting in separate windows!
echo.
echo   Frontend Agent: http://localhost:8010/.well-known/agent.json
echo   Backend Agent:  http://localhost:8021/.well-known/agent.json
echo   Unity Agent:    http://localhost:8012/.well-known/agent.json
echo.
echo   Now you can start Claude CLI in the project directory:
echo   cd "D:\Data\05_CGXR\A2A\LangGrpah\A2A-LangGraph"
echo   claude
echo ================================================================
echo.
pause