"""
실시간 LangGraph 실행 모니터링
그래프 노드들이 실행될 때마다 동적으로 시각화
"""

import os
import sys
import json
import time
import threading
import webbrowser
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
import socketserver

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

# Load environment variables
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from agent import CurrencyAgent

class GraphMonitor:
    def __init__(self):
        self.execution_log = []
        self.current_node = None
        self.start_time = None
        
    def log_node_execution(self, node_name, status="running", data=None):
        """노드 실행을 로그에 기록"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        log_entry = {
            "timestamp": timestamp,
            "node": node_name,
            "status": status,
            "data": data or {},
            "elapsed": time.time() - self.start_time if self.start_time else 0
        }
        self.execution_log.append(log_entry)
        self.current_node = node_name
        print(f"[{timestamp}] 🔄 {node_name} - {status}")
        
    def start_monitoring(self, query="USD to EUR conversion"):
        """그래프 실행을 시작하고 모니터링"""
        print("🚀 LangGraph 실시간 모니터링 시작")
        print("=" * 50)
        
        self.start_time = time.time()
        self.log_node_execution("__start__", "completed", {"query": query})
        
        try:
            # CurrencyAgent 생성 및 실행
            agent = CurrencyAgent()
            
            # 스트리밍으로 실행하여 각 단계 모니터링
            config = {"configurable": {"thread_id": "monitor_session"}}
            
            self.log_node_execution("agent", "running", {"action": "analyzing_query"})
            
            # 그래프 실행 (각 스텝 모니터링)
            for i, chunk in enumerate(agent.graph.stream(
                {"messages": [("user", query)]}, 
                config, 
                stream_mode="values"
            )):
                current_messages = chunk.get("messages", [])
                if current_messages:
                    last_message = current_messages[-1]
                    
                    # 메시지 타입에 따라 현재 노드 추정
                    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                        self.log_node_execution("agent", "completed", {"decision": "call_tools"})
                        self.log_node_execution("tools", "running", {"tool": "get_exchange_rate"})
                    elif hasattr(last_message, 'name') and last_message.name:
                        self.log_node_execution("tools", "completed", {"result": str(last_message.content)[:100]})
                        self.log_node_execution("agent", "running", {"action": "processing_tool_result"})
                    elif hasattr(last_message, 'content') and "status" in str(last_message.content):
                        self.log_node_execution("generate_structured_response", "running")
                        
                time.sleep(0.1)  # 시각화를 위한 지연
            
            self.log_node_execution("generate_structured_response", "completed")
            self.log_node_execution("__end__", "completed")
            
        except Exception as e:
            self.log_node_execution("error", "failed", {"error": str(e)})
            
        total_time = time.time() - self.start_time
        print(f"\n✅ 총 실행 시간: {total_time:.2f}초")
        print(f"📊 실행된 노드 수: {len(set(log['node'] for log in self.execution_log))}")

def create_live_html():
    """동적 HTML 페이지 생성"""
    return """
<!DOCTYPE html>
<html>
<head>
    <title>LangGraph 실시간 모니터링</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <style>
        body { font-family: Arial; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .status-bar { background: white; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
        .graph-container { background: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
        .log-container { background: white; padding: 20px; border-radius: 5px; max-height: 300px; overflow-y: auto; }
        .log-entry { padding: 5px; margin: 2px 0; border-radius: 3px; font-family: monospace; }
        .running { background: #fff3cd; }
        .completed { background: #d4edda; }
        .failed { background: #f8d7da; }
        .current-node { animation: pulse 1s infinite; }
        @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
        .refresh-btn { background: #007bff; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔄 LangGraph 실시간 실행 모니터링</h1>
        
        <div class="status-bar">
            <button class="refresh-btn" onclick="runDemo()">새 쿼리 실행</button>
            <span id="status">대기 중...</span>
        </div>
        
        <div class="graph-container">
            <div class="mermaid" id="graph">
graph TD;
    start([🏁 start]):::start
    agent[🤖 agent]:::node
    tools[🔧 tools]:::node  
    response[📝 response]:::node
    end([🏁 end]):::end
    
    start --> agent
    agent -.-> tools
    tools --> agent
    agent -.-> response
    response --> end
    
    classDef start fill:#e1f5fe
    classDef end fill:#e8f5e8
    classDef node fill:#f3e5f5
    classDef current fill:#ffeb3b,stroke:#f57f17,stroke-width:3px
    classDef completed fill:#4caf50,color:white
            </div>
        </div>
        
        <div class="log-container">
            <h3>📋 실행 로그</h3>
            <div id="logs">
                <div class="log-entry">시스템 준비 완료. 'Query 실행' 버튼을 클릭하세요.</div>
            </div>
        </div>
    </div>

    <script>
        mermaid.initialize({startOnLoad: true});
        
        let currentStep = 0;
        const steps = ['start', 'agent', 'tools', 'agent', 'response', 'end'];
        const stepDescriptions = {
            'start': '쿼리 시작',
            'agent': '에이전트 분석',
            'tools': '도구 실행',
            'response': '응답 생성',
            'end': '완료'
        };
        
        function addLog(message, type = 'info') {
            const logs = document.getElementById('logs');
            const time = new Date().toLocaleTimeString();
            const logEntry = document.createElement('div');
            logEntry.className = `log-entry ${type}`;
            logEntry.innerHTML = `[${time}] ${message}`;
            logs.appendChild(logEntry);
            logs.scrollTop = logs.scrollHeight;
        }
        
        function updateGraph(currentNode) {
            const graphDiv = document.getElementById('graph');
            let graphCode = `
graph TD;
    start([🏁 start])
    agent[🤖 agent]
    tools[🔧 tools]  
    response[📝 response]
    end([🏁 end])
    
    start --> agent
    agent -.-> tools
    tools --> agent
    agent -.-> response
    response --> end
    
    classDef start fill:#e1f5fe
    classDef end fill:#e8f5e8
    classDef node fill:#f3e5f5
    classDef current fill:#ffeb3b,stroke:#f57f17,stroke-width:3px
    classDef completed fill:#4caf50,color:white
            `;
            
            if (currentNode) {
                graphCode += `\n    class ${currentNode} current`;
            }
            
            graphDiv.innerHTML = graphCode;
            mermaid.init(undefined, graphDiv);
        }
        
        async function runDemo() {
            document.getElementById('status').textContent = '실행 중...';
            addLog('🚀 새 쿼리 실행 시작', 'running');
            
            const steps = [
                {node: 'start', desc: '쿼리 시작', delay: 500},
                {node: 'agent', desc: '에이전트가 쿼리 분석 중', delay: 1000},
                {node: 'tools', desc: '환율 조회 도구 실행 중', delay: 1500},
                {node: 'agent', desc: '에이전트가 결과 처리 중', delay: 800},
                {node: 'response', desc: '응답 생성 중', delay: 700},
                {node: 'end', desc: '실행 완료', delay: 300}
            ];
            
            for (let step of steps) {
                updateGraph(step.node);
                addLog(`🔄 ${step.desc}`, 'running');
                await new Promise(resolve => setTimeout(resolve, step.delay));
                addLog(`✅ ${step.desc} 완료`, 'completed');
            }
            
            document.getElementById('status').textContent = '완료';
            addLog('🎉 모든 단계 완료!', 'completed');
            updateGraph(null);
        }
        
        // 초기 그래프 렌더링
        updateGraph(null);
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
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(create_live_html().encode())
            else:
                super().do_GET()
    
    try:
        with socketserver.TCPServer(("", port), CustomHandler) as httpd:
            print(f"🌐 웹 서버 시작: http://localhost:{port}")
            print("브라우저에서 실시간 그래프를 확인하세요!")
            
            # 브라우저 자동 열기
            threading.Timer(1.0, lambda: webbrowser.open(f'http://localhost:{port}')).start()
            
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n웹 서버 종료")

if __name__ == "__main__":
    print("LangGraph 실시간 모니터링 도구")
    print("=" * 50)
    
    choice = input("실행 방법을 선택하세요:\n1. 콘솔 모니터링\n2. 웹 UI 모니터링\n선택 (1/2): ")
    
    if choice == "1":
        monitor = GraphMonitor()
        monitor.start_monitoring("Convert 100 USD to EUR")
    else:
        start_web_server()