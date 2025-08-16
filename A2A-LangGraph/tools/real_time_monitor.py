"""
Real-time LangGraph Monitor
실제 AI 대화와 연동되는 진짜 실시간 모니터링
"""

import os
import sys
import json
import time
import threading
import webbrowser
import socketserver
from http.server import SimpleHTTPRequestHandler
from datetime import datetime
import asyncio
import websockets

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

# Load environment variables
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from agent import CurrencyAgent

class RealTimeGraphMonitor:
    def __init__(self):
        self.websocket_clients = set()
        self.agent = None
        self.current_execution = None
        
    async def register_client(self, websocket):
        """웹소켓 클라이언트 등록"""
        self.websocket_clients.add(websocket)
        await websocket.send(json.dumps({
            "type": "status",
            "message": "Connected to real-time monitor"
        }))
        
    async def unregister_client(self, websocket):
        """웹소켓 클라이언트 해제"""
        self.websocket_clients.discard(websocket)
        
    async def broadcast_to_clients(self, data):
        """모든 클라이언트에게 메시지 브로드캐스트"""
        if self.websocket_clients:
            message = json.dumps(data)
            # 모든 클라이언트에게 동시에 전송
            await asyncio.gather(
                *[client.send(message) for client in self.websocket_clients],
                return_exceptions=True
            )
    
    async def execute_real_query(self, query):
        """실제 쿼리 실행 및 실시간 모니터링"""
        try:
            if not self.agent:
                self.agent = CurrencyAgent()
            
            # 실행 시작 알림
            await self.broadcast_to_clients({
                "type": "node_update",
                "node": "start", 
                "status": "current",
                "message": f"Starting query: {query}"
            })
            
            # Agent 단계
            await self.broadcast_to_clients({
                "type": "node_update", 
                "node": "agent",
                "status": "current",
                "message": "Agent analyzing query..."
            })
            
            config = {"configurable": {"thread_id": f"realtime_{int(time.time())}"}}
            
            # 스트리밍으로 실제 그래프 실행
            step_count = 0
            for chunk in self.agent.graph.stream(
                {"messages": [("user", query)]}, 
                config, 
                stream_mode="values"
            ):
                step_count += 1
                current_messages = chunk.get("messages", [])
                
                if current_messages:
                    last_message = current_messages[-1]
                    
                    # 도구 호출 감지
                    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                        await self.broadcast_to_clients({
                            "type": "node_update",
                            "node": "agent",
                            "status": "completed",
                            "message": "Agent decided to call tools"
                        })
                        
                        await self.broadcast_to_clients({
                            "type": "node_update",
                            "node": "tools", 
                            "status": "current",
                            "message": "Calling get_exchange_rate tool..."
                        })
                        
                    # 도구 결과 처리
                    elif hasattr(last_message, 'name') and last_message.name:
                        await self.broadcast_to_clients({
                            "type": "node_update",
                            "node": "tools",
                            "status": "completed", 
                            "message": f"Tool result: {str(last_message.content)[:50]}..."
                        })
                        
                        await self.broadcast_to_clients({
                            "type": "node_update",
                            "node": "agent",
                            "status": "current",
                            "message": "Agent processing tool results..."
                        })
                    
                    # 구조화된 응답 생성
                    elif hasattr(last_message, 'content') and "status" in str(last_message.content):
                        await self.broadcast_to_clients({
                            "type": "node_update",
                            "node": "response",
                            "status": "current", 
                            "message": "Generating structured response..."
                        })
                
                # 실시간 느낌을 위한 짧은 지연
                await asyncio.sleep(0.2)
            
            # 최종 응답 얻기
            final_response = self.agent.get_agent_response(config)
            
            await self.broadcast_to_clients({
                "type": "node_update",
                "node": "response",
                "status": "completed",
                "message": "Response generated successfully"
            })
            
            await self.broadcast_to_clients({
                "type": "node_update", 
                "node": "end",
                "status": "completed",
                "message": f"Execution completed. Steps: {step_count}"
            })
            
            # 최종 결과 전송
            await self.broadcast_to_clients({
                "type": "final_result",
                "result": final_response,
                "query": query,
                "steps": step_count
            })
            
        except Exception as e:
            await self.broadcast_to_clients({
                "type": "error",
                "message": f"Execution error: {str(e)}"
            })

# 글로벌 모니터 인스턴스
monitor = RealTimeGraphMonitor()

async def websocket_handler(websocket, path):
    """웹소켓 핸들러"""
    await monitor.register_client(websocket)
    try:
        async for message in websocket:
            data = json.loads(message)
            if data["type"] == "execute_query":
                query = data["query"]
                # 백그라운드에서 쿼리 실행
                asyncio.create_task(monitor.execute_real_query(query))
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        await monitor.unregister_client(websocket)

def create_html():
    return """
<!DOCTYPE html>
<html>
<head>
    <title>Real-time LangGraph Monitor</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 20px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
        }
        .container { 
            max-width: 1200px; 
            margin: 0 auto; 
            background: white;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        .header { 
            text-align: center; 
            margin-bottom: 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
        }
        .input-panel { 
            background: #f8f9fa; 
            padding: 20px; 
            border-radius: 10px; 
            margin-bottom: 30px;
        }
        .graph-container { 
            background: #f8f9fa; 
            padding: 30px; 
            border-radius: 10px; 
            margin-bottom: 30px;
            min-height: 400px;
        }
        .result-container {
            background: #f8f9fa; 
            padding: 20px; 
            border-radius: 10px; 
            margin-bottom: 20px;
            min-height: 100px;
        }
        
        /* Input Styles */
        .query-input {
            width: 70%;
            padding: 15px;
            border: 2px solid #ddd;
            border-radius: 25px;
            font-size: 16px;
            margin-right: 10px;
        }
        
        .execute-btn {
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 25px;
            font-size: 16px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .execute-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.3);
        }
        
        .execute-btn:disabled {
            background: #6c757d;
            cursor: not-allowed;
            transform: none;
        }
        
        /* Graph Styles */
        .graph {
            display: flex;
            justify-content: center;
            align-items: center;
            flex-direction: column;
            gap: 20px;
            padding: 20px;
        }
        
        .graph-row {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 30px;
            margin: 10px 0;
        }
        
        .node {
            width: 120px;
            height: 80px;
            border-radius: 15px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 14px;
            text-align: center;
            transition: all 0.5s ease;
            border: 3px solid #ddd;
            background: white;
            position: relative;
        }
        
        .node.start { background: #e3f2fd; border-color: #1976d2; }
        .node.agent { background: #f3e5f5; border-color: #7b1fa2; }
        .node.tools { background: #fff3e0; border-color: #f57c00; }
        .node.response { background: #e8f5e8; border-color: #388e3c; }
        .node.end { background: #fce4ec; border-color: #c2185b; }
        
        .node.current {
            background: #ffeb3b !important;
            border-color: #f57f17 !important;
            transform: scale(1.1);
            box-shadow: 0 0 20px rgba(245, 127, 23, 0.5);
            animation: pulse 1.5s infinite;
        }
        
        .node.completed {
            background: #4caf50 !important;
            color: white !important;
            border-color: #2e7d32 !important;
            transform: scale(0.95);
        }
        
        @keyframes pulse {
            0% { box-shadow: 0 0 20px rgba(245, 127, 23, 0.5); }
            50% { box-shadow: 0 0 30px rgba(245, 127, 23, 0.8); }
            100% { box-shadow: 0 0 20px rgba(245, 127, 23, 0.5); }
        }
        
        .arrow {
            width: 0;
            height: 0;
            border-left: 15px solid transparent;
            border-right: 15px solid transparent;
            border-top: 20px solid #666;
            margin: 5px 0;
        }
        
        .connection-status {
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 20px;
            font-weight: bold;
        }
        
        .connected { background: #d4edda; color: #155724; }
        .disconnected { background: #f8d7da; color: #721c24; }
        
        .result-content {
            background: white;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #007bff;
            font-family: monospace;
            white-space: pre-wrap;
        }
        
        .example-queries {
            margin-top: 15px;
        }
        
        .example-btn {
            background: #6c757d;
            color: white;
            border: none;
            padding: 8px 15px;
            border-radius: 15px;
            margin: 5px;
            cursor: pointer;
            font-size: 14px;
        }
        
        .example-btn:hover {
            background: #5a6268;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔗 Real-time LangGraph Monitor</h1>
            <p>Execute actual AI queries and watch the graph in real-time!</p>
        </div>
        
        <div class="connection-status disconnected" id="connectionStatus">
            🔴 Connecting to real-time monitor...
        </div>
        
        <div class="input-panel">
            <h3>💬 Execute Real AI Query</h3>
            <input type="text" class="query-input" id="queryInput" 
                   placeholder="Enter your query (e.g., 'Convert 100 USD to EUR')" 
                   value="Convert 100 USD to EUR">
            <button class="execute-btn" onclick="executeQuery()" id="executeBtn" disabled>
                🚀 Execute Real Query
            </button>
            
            <div class="example-queries">
                <strong>Quick Examples:</strong>
                <button class="example-btn" onclick="setQuery('Convert 50 USD to EUR')">USD → EUR</button>
                <button class="example-btn" onclick="setQuery('What is the exchange rate for GBP to JPY?')">GBP → JPY</button>
                <button class="example-btn" onclick="setQuery('How is the weather today?')">Non-currency</button>
                <button class="example-btn" onclick="setQuery('Convert 1000 EUR to USD')">EUR → USD</button>
            </div>
        </div>
        
        <div class="graph-container">
            <h3 style="text-align: center; margin-bottom: 30px;">📊 Real-time Graph Execution</h3>
            
            <div class="graph">
                <div class="graph-row">
                    <div class="node start" id="node-start">🏁<br>START</div>
                </div>
                <div class="arrow"></div>
                <div class="graph-row">
                    <div class="node agent" id="node-agent">🤖<br>AGENT<br><small>Analysis</small></div>
                </div>
                <div class="graph-row">
                    <div class="node tools" id="node-tools">🔧<br>TOOLS<br><small>Currency API</small></div>
                </div>
                <div class="graph-row">
                    <div class="node response" id="node-response">📝<br>RESPONSE<br><small>Generate</small></div>
                </div>
                <div class="arrow"></div>
                <div class="graph-row">
                    <div class="node end" id="node-end">🏁<br>END</div>
                </div>
            </div>
        </div>
        
        <div class="result-container">
            <h3>📋 Real-time Execution Result</h3>
            <div class="result-content" id="resultContent">
                Waiting for query execution...
            </div>
        </div>
    </div>

    <script>
        let ws = null;
        
        function connectWebSocket() {
            try {
                ws = new WebSocket('ws://localhost:8765');
                
                ws.onopen = function() {
                    document.getElementById('connectionStatus').textContent = '🟢 Connected to real-time monitor';
                    document.getElementById('connectionStatus').className = 'connection-status connected';
                    document.getElementById('executeBtn').disabled = false;
                };
                
                ws.onmessage = function(event) {
                    const data = JSON.parse(event.data);
                    handleWebSocketMessage(data);
                };
                
                ws.onclose = function() {
                    document.getElementById('connectionStatus').textContent = '🔴 Disconnected from monitor';
                    document.getElementById('connectionStatus').className = 'connection-status disconnected';
                    document.getElementById('executeBtn').disabled = true;
                    
                    // Reconnect after 3 seconds
                    setTimeout(connectWebSocket, 3000);
                };
                
                ws.onerror = function() {
                    document.getElementById('connectionStatus').textContent = '🔴 Connection error';
                    document.getElementById('connectionStatus').className = 'connection-status disconnected';
                };
                
            } catch (error) {
                console.error('WebSocket connection failed:', error);
                setTimeout(connectWebSocket, 3000);
            }
        }
        
        function handleWebSocketMessage(data) {
            if (data.type === 'node_update') {
                updateNode(data.node, data.status);
                updateResult(`[${new Date().toLocaleTimeString()}] ${data.message}`);
            } else if (data.type === 'final_result') {
                updateResult(`\\n=== FINAL RESULT ===\\nQuery: ${data.query}\\nSteps: ${data.steps}\\nResult: ${JSON.stringify(data.result, null, 2)}`);
                document.getElementById('executeBtn').disabled = false;
                document.getElementById('executeBtn').textContent = '🚀 Execute Real Query';
            } else if (data.type === 'error') {
                updateResult(`\\n❌ ERROR: ${data.message}`);
                document.getElementById('executeBtn').disabled = false;
                document.getElementById('executeBtn').textContent = '🚀 Execute Real Query';
            }
        }
        
        function updateNode(nodeId, status) {
            const node = document.getElementById(`node-${nodeId}`);
            
            // Remove all status classes
            node.classList.remove('current', 'completed');
            
            // Add new status
            if (status === 'current') {
                node.classList.add('current');
            } else if (status === 'completed') {
                node.classList.add('completed');
            }
        }
        
        function updateResult(message) {
            const resultDiv = document.getElementById('resultContent');
            resultDiv.textContent += message + '\\n';
            resultDiv.scrollTop = resultDiv.scrollHeight;
        }
        
        function resetGraph() {
            const nodes = ['start', 'agent', 'tools', 'response', 'end'];
            nodes.forEach(nodeId => {
                const node = document.getElementById(`node-${nodeId}`);
                node.classList.remove('current', 'completed');
            });
        }
        
        function executeQuery() {
            const query = document.getElementById('queryInput').value.trim();
            if (!query) {
                alert('Please enter a query');
                return;
            }
            
            resetGraph();
            document.getElementById('resultContent').textContent = '';
            document.getElementById('executeBtn').disabled = true;
            document.getElementById('executeBtn').textContent = '🔄 Executing...';
            
            // Send query to WebSocket
            ws.send(JSON.stringify({
                type: 'execute_query',
                query: query
            }));
        }
        
        function setQuery(query) {
            document.getElementById('queryInput').value = query;
        }
        
        // Auto-connect on page load
        window.addEventListener('load', function() {
            connectWebSocket();
        });
        
        // Enter key support
        document.getElementById('queryInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                executeQuery();
            }
        });
    </script>
</body>
</html>
    """

def start_web_server():
    """HTTP 웹 서버 시작"""
    port = 8080
    
    class CustomHandler(SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/' or self.path == '/index.html':
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(create_html().encode('utf-8'))
            else:
                super().do_GET()
    
    with socketserver.TCPServer(("", port), CustomHandler) as httpd:
        print(f"Web server started on http://localhost:{port}")
        httpd.serve_forever()

def start_websocket_server():
    """웹소켓 서버 시작"""
    import websockets
    
    start_server = websockets.serve(websocket_handler, "localhost", 8765)
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    print("WebSocket server started on ws://localhost:8765")
    loop.run_until_complete(start_server)
    loop.run_forever()

if __name__ == "__main__":
    print("Real-time LangGraph Monitor Starting...")
    print("=" * 50)
    
    # 웹소켓 서버를 별도 쓰레드에서 시작
    websocket_thread = threading.Thread(target=start_websocket_server, daemon=True)
    websocket_thread.start()
    
    # 브라우저 자동 열기
    threading.Timer(2.0, lambda: webbrowser.open('http://localhost:8080')).start()
    
    try:
        # 웹 서버 시작 (메인 쓰레드)
        start_web_server()
    except KeyboardInterrupt:
        print("\\nServers stopped")