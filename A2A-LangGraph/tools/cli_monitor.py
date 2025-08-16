"""
CLI + WebSocket Real-time Monitor
CLI에서 대화하면 웹 UI에서 실시간 그래프 확인
"""

import os
import sys
import json
import threading
import webbrowser
import socketserver
from http.server import SimpleHTTPRequestHandler
import asyncio
import websockets
import time
from datetime import datetime

# 전역 WebSocket 클라이언트들
websocket_clients = set()

async def register_client(websocket):
    """웹소켓 클라이언트 등록"""
    websocket_clients.add(websocket)
    await websocket.send(json.dumps({
        "type": "status",
        "message": "Connected to CLI monitor"
    }))

async def unregister_client(websocket):
    """웹소켓 클라이언트 해제"""
    websocket_clients.discard(websocket)

async def broadcast_to_clients(data):
    """모든 클라이언트에게 메시지 브로드캐스트"""
    if websocket_clients:
        message = json.dumps(data)
        await asyncio.gather(
            *[client.send(message) for client in websocket_clients],
            return_exceptions=True
        )

def broadcast_node_update(node, status, message=""):
    """동기 함수에서 WebSocket 브로드캐스트"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(broadcast_to_clients({
            "type": "node_update",
            "node": node,
            "status": status,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }))
        loop.close()
    except:
        pass  # 에러 무시

async def websocket_handler(websocket, path):
    """웹소켓 핸들러"""
    await register_client(websocket)
    try:
        async for message in websocket:
            # CLI 모니터는 단방향이므로 메시지 처리 불필요
            pass
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        await unregister_client(websocket)

def create_monitor_html():
    return """
<!DOCTYPE html>
<html>
<head>
    <title>🖥️ CLI Real-time Monitor</title>
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
        .status-panel { 
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
        .log-container { 
            background: #f8f9fa; 
            padding: 20px; 
            border-radius: 10px; 
            max-height: 300px; 
            overflow-y: auto;
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
        
        .log-entry {
            padding: 8px;
            margin: 3px 0;
            border-radius: 3px;
            font-family: monospace;
            font-size: 14px;
            border-left: 4px solid #ddd;
        }
        .running { background: #fff3cd; border-left-color: #ffc107; }
        .completed { background: #d4edda; border-left-color: #28a745; }
        .info { background: #d1ecf1; border-left-color: #17a2b8; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🖥️ CLI Real-time LangGraph Monitor</h1>
            <p>CLI에서 대화하면 실시간으로 그래프 실행을 확인하세요!</p>
        </div>
        
        <div class="status-panel">
            <div class="connection-status disconnected" id="connectionStatus">
                🔴 Connecting to CLI monitor...
            </div>
            <div style="text-align: center; font-size: 18px; margin-top: 10px;">
                <strong>💬 CLI에서 "Convert 100 USD to EUR" 입력해보세요</strong>
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
        
        <div class="log-container">
            <h3>📋 Real-time CLI Activity Log</h3>
            <div id="logs">
                <div class="log-entry info">
                    [SYSTEM] CLI monitoring ready. CLI에서 질문을 입력하세요.
                </div>
            </div>
        </div>
    </div>

    <script>
        let ws = null;
        
        function connectWebSocket() {
            try {
                ws = new WebSocket('ws://localhost:8765');
                
                ws.onopen = function() {
                    document.getElementById('connectionStatus').textContent = '🟢 Connected to CLI monitor';
                    document.getElementById('connectionStatus').className = 'connection-status connected';
                };
                
                ws.onmessage = function(event) {
                    const data = JSON.parse(event.data);
                    handleWebSocketMessage(data);
                };
                
                ws.onclose = function() {
                    document.getElementById('connectionStatus').textContent = '🔴 Disconnected from CLI monitor';
                    document.getElementById('connectionStatus').className = 'connection-status disconnected';
                    
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
                addLog(`[${new Date().toLocaleTimeString()}] ${data.message}`, data.status === 'current' ? 'running' : 'completed');
            }
        }
        
        function updateNode(nodeId, status) {
            const node = document.getElementById(`node-${nodeId}`);
            if (!node) return;
            
            // Remove all status classes
            node.classList.remove('current', 'completed');
            
            // Add new status
            if (status === 'current') {
                node.classList.add('current');
            } else if (status === 'completed') {
                node.classList.add('completed');
            }
        }
        
        function addLog(message, type = 'info') {
            const logs = document.getElementById('logs');
            const logEntry = document.createElement('div');
            logEntry.className = `log-entry ${type}`;
            logEntry.textContent = message;
            logs.appendChild(logEntry);
            logs.scrollTop = logs.scrollHeight;
        }
        
        // Auto-connect on page load
        window.addEventListener('load', function() {
            connectWebSocket();
        });
    </script>
</body>
</html>
    """

def start_web_server():
    """HTTP 웹 서버 시작"""
    port = 8095
    
    class CustomHandler(SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/' or self.path == '/index.html':
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(create_monitor_html().encode('utf-8'))
            else:
                super().do_GET()
        
        def do_POST(self):
            if self.path == '/notify':
                try:
                    content_length = int(self.headers['Content-Length'])
                    post_data = self.rfile.read(content_length)
                    data = json.loads(post_data.decode('utf-8'))
                    
                    # WebSocket으로 브로드캐스트
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(broadcast_to_clients(data))
                    loop.close()
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(b'{"status": "ok"}')
                except Exception as e:
                    self.send_response(500)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
            else:
                super().do_POST()
    
    with socketserver.TCPServer(("", port), CustomHandler) as httpd:
        print(f"CLI Monitor Web UI started on http://localhost:{port}")
        httpd.serve_forever()

def start_notification_server():
    """알림 전용 HTTP 서버"""
    port = 8096
    
    class NotificationHandler(SimpleHTTPRequestHandler):
        def do_POST(self):
            if self.path == '/notify':
                try:
                    content_length = int(self.headers['Content-Length'])
                    post_data = self.rfile.read(content_length)
                    data = json.loads(post_data.decode('utf-8'))
                    
                    # WebSocket으로 브로드캐스트
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(broadcast_to_clients(data))
                    loop.close()
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(b'{"status": "ok"}')
                except Exception as e:
                    self.send_response(500)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
    
    with socketserver.TCPServer(("", port), NotificationHandler) as httpd:
        print(f"CLI Monitor Notification server started on http://localhost:{port}")
        httpd.serve_forever()

def start_websocket_server():
    """웹소켓 서버 시작"""
    start_server = websockets.serve(websocket_handler, "localhost", 8765)
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    print("CLI Monitor WebSocket server started on ws://localhost:8765")
    loop.run_until_complete(start_server)
    loop.run_forever()

if __name__ == "__main__":
    print("CLI + WebSocket Monitor Starting...")
    print("=" * 50)
    
    # 웹소켓 서버를 별도 쓰레드에서 시작
    websocket_thread = threading.Thread(target=start_websocket_server, daemon=True)
    websocket_thread.start()
    
    # 알림 서버를 별도 쓰레드에서 시작
    notification_thread = threading.Thread(target=start_notification_server, daemon=True)
    notification_thread.start()
    
    # 브라우저 자동 열기
    threading.Timer(2.0, lambda: webbrowser.open('http://localhost:8095')).start()
    
    try:
        # 웹 서버 시작 (메인 쓰레드)
        start_web_server()
    except KeyboardInterrupt:
        print("\nServers stopped")