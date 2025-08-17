# Claude CLI Multi-Agent System - Agent Server Launcher (PowerShell)

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "   Claude CLI Multi-Agent System - Agent Server Launcher" -ForegroundColor Cyan  
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

Set-Location "D:\Data\05_CGXR\A2A\LangGrpah\A2A-LangGraph"

Write-Host "[1/3] Starting Frontend Agent on port 8010..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python -m agents.claude_cli.frontend.server"

Write-Host "[2/3] Starting Backend Agent on port 8021..." -ForegroundColor Green  
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python -m agents.claude_cli.backend.server"

Write-Host "[3/3] Starting Unity Agent on port 8012..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python -m agents.claude_cli.unity.server"

Write-Host ""
Write-Host "================================================================" -ForegroundColor Yellow
Write-Host "   All agents are starting in separate windows!" -ForegroundColor Yellow
Write-Host ""
Write-Host "   Frontend Agent: http://localhost:8010/.well-known/agent.json" -ForegroundColor White
Write-Host "   Backend Agent:  http://localhost:8021/.well-known/agent.json" -ForegroundColor White  
Write-Host "   Unity Agent:    http://localhost:8012/.well-known/agent.json" -ForegroundColor White
Write-Host ""
Write-Host "   Now you can start Claude CLI in the project directory:" -ForegroundColor Cyan
Write-Host "   cd `"D:\Data\05_CGXR\A2A\LangGrpah\A2A-LangGraph`"" -ForegroundColor Gray
Write-Host "   claude" -ForegroundColor Gray
Write-Host "================================================================" -ForegroundColor Yellow
Write-Host ""

# 잠시 대기 후 agent 상태 확인
Start-Sleep -Seconds 3

Write-Host "Checking agent status..." -ForegroundColor Cyan
try {
    $frontend = Invoke-WebRequest -Uri "http://localhost:8010/.well-known/agent.json" -TimeoutSec 2 -ErrorAction SilentlyContinue
    if ($frontend.StatusCode -eq 200) {
        Write-Host "✅ Frontend Agent: Running" -ForegroundColor Green
    }
} catch {
    Write-Host "⏳ Frontend Agent: Starting..." -ForegroundColor Yellow
}

try {
    $backend = Invoke-WebRequest -Uri "http://localhost:8021/.well-known/agent.json" -TimeoutSec 2 -ErrorAction SilentlyContinue  
    if ($backend.StatusCode -eq 200) {
        Write-Host "✅ Backend Agent: Running" -ForegroundColor Green
    }
} catch {
    Write-Host "⏳ Backend Agent: Starting..." -ForegroundColor Yellow
}

try {
    $unity = Invoke-WebRequest -Uri "http://localhost:8012/.well-known/agent.json" -TimeoutSec 2 -ErrorAction SilentlyContinue
    if ($unity.StatusCode -eq 200) {
        Write-Host "✅ Unity Agent: Running" -ForegroundColor Green  
    }
} catch {
    Write-Host "⏳ Unity Agent: Starting..." -ForegroundColor Yellow
}

Write-Host ""
Read-Host "Press Enter to continue"