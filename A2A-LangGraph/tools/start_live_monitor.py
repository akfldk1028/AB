"""
LangGraph 실시간 웹 모니터 시작
"""

import os
import sys
import threading
import webbrowser
import socketserver
from http.server import SimpleHTTPRequestHandler

def create_live_html():
    """동적 HTML 페이지 생성"""
    return """
<!DOCTYPE html>
<html>
<head>
    <title>🔄 LangGraph 실시간 모니터링</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <style>
        body { font-family: Arial; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; text-align: center; }
        .control-panel { background: white; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
        .graph-container { background: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
        .log-container { background: white; padding: 20px; border-radius: 5px; max-height: 300px; overflow-y: auto; }
        .log-entry { padding: 8px; margin: 3px 0; border-radius: 3px; font-family: monospace; font-size: 14px; }
        .running { background: #fff3cd; border-left: 4px solid #ffc107; }
        .completed { background: #d4edda; border-left: 4px solid #28a745; }
        .failed { background: #f8d7da; border-left: 4px solid #dc3545; }
        .info { background: #d1ecf1; border-left: 4px solid #17a2b8; }
        .btn { background: #007bff; color: white; border: none; padding: 12px 25px; border-radius: 5px; cursor: pointer; margin: 5px; font-size: 16px; }
        .btn:hover { background: #0056b3; }
        .btn:disabled { background: #6c757d; cursor: not-allowed; }
        .status { margin-left: 20px; font-weight: bold; }
        .node-current { animation: pulse 2s infinite; }
        @keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.05); } 100% { transform: scale(1); } }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 LangGraph 실시간 실행 모니터링</h1>
            <p>Currency Agent의 그래프 실행을 실시간으로 확인하세요</p>
        </div>
        
        <div class="control-panel">
            <button class="btn" onclick="runCurrencyQuery()" id="runBtn">💱 환율 조회 실행</button>
            <button class="btn" onclick="runChatQuery()" id="chatBtn">💬 일반 채팅 실행</button>
            <button class="btn" onclick="clearLogs()">🗑️ 로그 지우기</button>
            <span class="status" id="status">준비 완료</span>
        </div>
        
        <div class="graph-container">
            <h3>📊 그래프 실행 흐름</h3>
            <div class="mermaid" id="graph">
graph TD;
    start([🏁 START]):::start
    agent[🤖 AGENT<br/>쿼리 분석]:::node
    tools[🔧 TOOLS<br/>환율 조회]:::node  
    response[📝 RESPONSE<br/>응답 생성]:::node
    end([🏁 END]):::end
    
    start --> agent
    agent -.->|환율 필요시| tools
    tools --> agent
    agent -.->|응답 준비| response
    response --> end
    
    classDef start fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef end fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef node fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef current fill:#ffeb3b,stroke:#f57f17,stroke-width:4px
    classDef completed fill:#4caf50,color:white,stroke:#2e7d32,stroke-width:2px
            </div>
        </div>
        
        <div class="log-container">
            <h3>📋 실시간 실행 로그</h3>
            <div id="logs">
                <div class="log-entry info">
                    [시스템] LangGraph 모니터링 준비 완료. 버튼을 클릭하여 실행하세요.
                </div>
            </div>
        </div>
    </div>

    <script>
        mermaid.initialize({
            startOnLoad: true,
            theme: 'default',
            flowchart: {
                useMaxWidth: true,
                htmlLabels: true
            }
        });
        
        function addLog(message, type = 'info') {
            const logs = document.getElementById('logs');
            const time = new Date().toLocaleTimeString();
            const logEntry = document.createElement('div');
            logEntry.className = `log-entry ${type}`;
            logEntry.innerHTML = `[${time}] ${message}`;
            logs.appendChild(logEntry);
            logs.scrollTop = logs.scrollHeight;
        }
        
        function updateStatus(message) {
            document.getElementById('status').textContent = message;
        }
        
        function disableButtons(disabled = true) {
            document.getElementById('runBtn').disabled = disabled;
            document.getElementById('chatBtn').disabled = disabled;
        }
        
        function updateGraph(currentNode, completedNodes = []) {
            const graphDiv = document.getElementById('graph');
            let graphCode = `
graph TD;
    start([🏁 START])
    agent[🤖 AGENT<br/>쿼리 분석]
    tools[🔧 TOOLS<br/>환율 조회]  
    response[📝 RESPONSE<br/>응답 생성]
    end([🏁 END])
    
    start --> agent
    agent -.->|환율 필요시| tools
    tools --> agent
    agent -.->|응답 준비| response
    response --> end
    
    classDef start fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef end fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef node fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef current fill:#ffeb3b,stroke:#f57f17,stroke-width:4px
    classDef completed fill:#4caf50,color:white,stroke:#2e7d32,stroke-width:2px
            `;
            
            if (currentNode) {
                graphCode += `\\n    class ${currentNode} current`;
            }
            
            for (let node of completedNodes) {
                graphCode += `\\n    class ${node} completed`;
            }
            
            graphDiv.innerHTML = graphCode;
            mermaid.init(undefined, graphDiv);
        }
        
        async function simulateExecution(queryType) {
            updateStatus('실행 중...');
            disableButtons(true);
            
            const steps = queryType === 'currency' ? [
                {node: 'start', desc: '🏁 쿼리 시작', delay: 500},
                {node: 'agent', desc: '🤖 에이전트가 환율 쿼리 분석 중', delay: 1200},
                {node: 'tools', desc: '🔧 MCP 서버에서 환율 데이터 조회 중', delay: 1800},
                {node: 'agent', desc: '🤖 에이전트가 조회 결과 처리 중', delay: 900},
                {node: 'response', desc: '📝 구조화된 응답 생성 중', delay: 700},
                {node: 'end', desc: '🏁 환율 조회 완료', delay: 300}
            ] : [
                {node: 'start', desc: '🏁 쿼리 시작', delay: 500},
                {node: 'agent', desc: '🤖 에이전트가 일반 쿼리 분석 중', delay: 1000},
                {node: 'response', desc: '📝 환율 외 주제라고 응답 생성 중', delay: 800},
                {node: 'end', desc: '🏁 응답 완료', delay: 300}
            ];
            
            let completedNodes = [];
            
            for (let i = 0; i < steps.length; i++) {
                const step = steps[i];
                updateGraph(step.node, completedNodes);
                addLog(`🔄 ${step.desc}`, 'running');
                
                await new Promise(resolve => setTimeout(resolve, step.delay));
                
                addLog(`✅ ${step.desc.replace('중', '완료')}`, 'completed');
                completedNodes.push(step.node);
                
                if (i === steps.length - 1) {
                    updateGraph(null, completedNodes);
                }
            }
            
            updateStatus('완료');
            addLog('🎉 전체 실행 완료!', 'completed');
            disableButtons(false);
        }
        
        async function runCurrencyQuery() {
            addLog('💱 환율 조회 시나리오 시작 (USD → EUR)', 'info');
            await simulateExecution('currency');
        }
        
        async function runChatQuery() {
            addLog('💬 일반 채팅 시나리오 시작 (날씨 문의)', 'info');
            await simulateExecution('chat');
        }
        
        function clearLogs() {
            document.getElementById('logs').innerHTML = 
                '<div class="log-entry info">[시스템] 로그가 지워졌습니다.</div>';
        }
        
        // 초기 그래프 렌더링
        updateGraph(null, []);
        
        // 페이지 로드 완료 메시지
        window.addEventListener('load', function() {
            addLog('🌐 웹 모니터링 인터페이스 로드 완료', 'completed');
        });
    </script>
</body>
</html>
    """

def start_web_server():
    """웹 서버 시작"""
    port = 8080
    
    class CustomHandler(SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/' or self.path == '/index.html':
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(create_live_html().encode('utf-8'))
            else:
                super().do_GET()
    
    try:
        with socketserver.TCPServer(("", port), CustomHandler) as httpd:
            print(f"🌐 LangGraph 실시간 모니터링 웹서버 시작")
            print(f"📱 URL: http://localhost:{port}")
            print("💡 브라우저에서 실시간 그래프 실행을 확인하세요!")
            print("🔄 Ctrl+C로 종료")
            
            # 브라우저 자동 열기
            threading.Timer(1.0, lambda: webbrowser.open(f'http://localhost:{port}')).start()
            
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n✅ 웹 서버 종료")
    except Exception as e:
        print(f"❌ 서버 에러: {e}")

if __name__ == "__main__":
    start_web_server()