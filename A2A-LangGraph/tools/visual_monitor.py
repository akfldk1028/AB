"""
Visual LangGraph Monitor with CSS-based graph
"""

import threading
import webbrowser
import socketserver
from http.server import SimpleHTTPRequestHandler

def create_html():
    return """
<!DOCTYPE html>
<html>
<head>
    <title>LangGraph Visual Monitor</title>
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
        .control-panel { 
            background: #f8f9fa; 
            padding: 20px; 
            border-radius: 10px; 
            margin-bottom: 30px;
            text-align: center;
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
            transition: all 0.3s ease;
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
        
        .arrow-right {
            width: 0;
            height: 0;
            border-top: 15px solid transparent;
            border-bottom: 15px solid transparent;
            border-left: 20px solid #666;
            margin: 0 10px;
        }
        
        .conditional-arrow {
            border-left-color: #ff9800 !important;
            border-top-color: #ff9800 !important;
        }
        
        /* Button and Log Styles */
        .btn { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; 
            border: none; 
            padding: 15px 25px; 
            border-radius: 25px; 
            cursor: pointer; 
            margin: 10px; 
            font-size: 16px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }
        .btn:hover { 
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.3);
        }
        .btn:disabled { 
            background: #6c757d; 
            cursor: not-allowed;
            transform: none;
        }
        
        .status { 
            margin-left: 20px; 
            font-weight: bold; 
            font-size: 18px;
            color: #667eea;
        }
        
        .log-entry { 
            padding: 10px; 
            margin: 5px 0; 
            border-radius: 5px; 
            font-family: monospace; 
            font-size: 14px;
            border-left: 4px solid #ddd;
        }
        .running { background: #fff3cd; border-left-color: #ffc107; }
        .completed { background: #d4edda; border-left-color: #28a745; }
        .info { background: #d1ecf1; border-left-color: #17a2b8; }
        
        .legend {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-top: 20px;
            flex-wrap: wrap;
        }
        
        .legend-item {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px 12px;
            background: white;
            border-radius: 20px;
            border: 2px solid #ddd;
            font-size: 12px;
        }
        
        .legend-dot {
            width: 16px;
            height: 16px;
            border-radius: 50%;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>LangGraph Real-time Visual Monitor</h1>
            <p>Watch the Currency Agent graph execution with beautiful animations</p>
        </div>
        
        <div class="control-panel">
            <button class="btn" onclick="runCurrencyQuery()" id="runBtn">💱 Run Currency Query</button>
            <button class="btn" onclick="runChatQuery()" id="chatBtn">💬 Run Chat Query</button>
            <button class="btn" onclick="clearLogs()">🗑️ Clear Logs</button>
            <span class="status" id="status">Ready to Execute</span>
        </div>
        
        <div class="graph-container">
            <h3 style="text-align: center; margin-bottom: 30px;">📊 Graph Execution Flow</h3>
            
            <div class="graph">
                <!-- Row 1: Start -->
                <div class="graph-row">
                    <div class="node start" id="node-start">
                        🏁<br>START
                    </div>
                </div>
                
                <div class="arrow"></div>
                
                <!-- Row 2: Agent -->
                <div class="graph-row">
                    <div class="node agent" id="node-agent">
                        🤖<br>AGENT<br><small>Query Analysis</small>
                    </div>
                </div>
                
                <!-- Row 3: Tools (conditional) -->
                <div class="graph-row">
                    <div class="arrow conditional-arrow" style="transform: rotate(45deg);"></div>
                    <div class="node tools" id="node-tools">
                        🔧<br>TOOLS<br><small>Currency API</small>
                    </div>
                    <div class="arrow conditional-arrow" style="transform: rotate(-45deg);"></div>
                </div>
                
                <!-- Row 4: Response -->
                <div class="graph-row">
                    <div class="node response" id="node-response">
                        📝<br>RESPONSE<br><small>Generate Answer</small>
                    </div>
                </div>
                
                <div class="arrow"></div>
                
                <!-- Row 5: End -->
                <div class="graph-row">
                    <div class="node end" id="node-end">
                        🏁<br>END
                    </div>
                </div>
            </div>
            
            <div class="legend">
                <div class="legend-item">
                    <div class="legend-dot" style="background: #e3f2fd; border: 2px solid #1976d2;"></div>
                    Waiting
                </div>
                <div class="legend-item">
                    <div class="legend-dot" style="background: #ffeb3b; border: 2px solid #f57f17;"></div>
                    Running
                </div>
                <div class="legend-item">
                    <div class="legend-dot" style="background: #4caf50; border: 2px solid #2e7d32;"></div>
                    Completed
                </div>
                <div class="legend-item">
                    <div class="legend-dot" style="background: #ff9800; border: 2px solid #f57c00;"></div>
                    Conditional
                </div>
            </div>
        </div>
        
        <div class="log-container">
            <h3>📋 Execution Log</h3>
            <div id="logs">
                <div class="log-entry info">
                    [SYSTEM] LangGraph visual monitoring ready. Click buttons to start execution.
                </div>
            </div>
        </div>
    </div>

    <script>
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
        
        function resetGraph() {
            const nodes = ['start', 'agent', 'tools', 'response', 'end'];
            nodes.forEach(node => {
                const element = document.getElementById(`node-${node}`);
                element.className = `node ${node}`;
            });
        }
        
        function highlightNode(node) {
            const element = document.getElementById(`node-${node}`);
            element.classList.add('current');
        }
        
        function completeNode(node) {
            const element = document.getElementById(`node-${node}`);
            element.classList.remove('current');
            element.classList.add('completed');
        }
        
        async function simulateExecution(queryType) {
            resetGraph();
            updateStatus('🔄 Executing...');
            disableButtons(true);
            
            const steps = queryType === 'currency' ? [
                {node: 'start', desc: '🏁 Query started', delay: 800},
                {node: 'agent', desc: '🤖 Agent analyzing currency query', delay: 1500},
                {node: 'tools', desc: '🔧 MCP server fetching exchange rate data', delay: 2000},
                {node: 'agent', desc: '🤖 Agent processing tool results', delay: 1200},
                {node: 'response', desc: '📝 Generating structured response', delay: 1000},
                {node: 'end', desc: '🏁 Currency query execution completed', delay: 500}
            ] : [
                {node: 'start', desc: '🏁 Query started', delay: 800},
                {node: 'agent', desc: '🤖 Agent analyzing general query', delay: 1500},
                {node: 'response', desc: '📝 Responding: non-currency topic', delay: 1200},
                {node: 'end', desc: '🏁 Response execution completed', delay: 500}
            ];
            
            for (let i = 0; i < steps.length; i++) {
                const step = steps[i];
                
                // Highlight current node
                highlightNode(step.node);
                addLog(`▶️ ${step.desc}`, 'running');
                
                // Wait for step completion
                await new Promise(resolve => setTimeout(resolve, step.delay));
                
                // Complete current node
                completeNode(step.node);
                addLog(`✅ ${step.desc.replace('ing', 'ed').replace('analyzing', 'analyzed')}`, 'completed');
            }
            
            updateStatus('✅ Completed');
            addLog('🎉 Full execution completed successfully!', 'completed');
            disableButtons(false);
        }
        
        async function runCurrencyQuery() {
            addLog('💱 Starting currency query scenario (USD → EUR)', 'info');
            await simulateExecution('currency');
        }
        
        async function runChatQuery() {
            addLog('💬 Starting general chat scenario (weather inquiry)', 'info');
            await simulateExecution('chat');
        }
        
        function clearLogs() {
            document.getElementById('logs').innerHTML = 
                '<div class="log-entry info">[SYSTEM] Execution logs cleared.</div>';
            resetGraph();
            updateStatus('Ready to Execute');
        }
        
        // Page load complete
        window.addEventListener('load', function() {
            addLog('🌐 Visual monitoring interface loaded successfully', 'completed');
        });
    </script>
</body>
</html>
    """

def start_server():
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
    
    try:
        with socketserver.TCPServer(("", port), CustomHandler) as httpd:
            print("LangGraph Visual Monitor Server Started")
            print(f"URL: http://localhost:{port}")
            print("Beautiful CSS-based graph visualization ready!")
            print("Press Ctrl+C to stop")
            
            # Open browser
            threading.Timer(1.0, lambda: webbrowser.open(f'http://localhost:{port}')).start()
            
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\\nServer stopped")
    except Exception as e:
        print(f"Server error: {e}")

if __name__ == "__main__":
    start_server()