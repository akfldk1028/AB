"""
Simple LangGraph Live Monitor
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
    <title>LangGraph Live Monitor</title>
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
        .info { background: #d1ecf1; border-left: 4px solid #17a2b8; }
        .btn { background: #007bff; color: white; border: none; padding: 12px 25px; border-radius: 5px; cursor: pointer; margin: 5px; font-size: 16px; }
        .btn:hover { background: #0056b3; }
        .btn:disabled { background: #6c757d; cursor: not-allowed; }
        .status { margin-left: 20px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>LangGraph Real-time Monitor</h1>
            <p>Watch Currency Agent graph execution in real-time</p>
        </div>
        
        <div class="control-panel">
            <button class="btn" onclick="runCurrencyQuery()" id="runBtn">Run Currency Query</button>
            <button class="btn" onclick="runChatQuery()" id="chatBtn">Run Chat Query</button>
            <button class="btn" onclick="clearLogs()">Clear Logs</button>
            <span class="status" id="status">Ready</span>
        </div>
        
        <div class="graph-container">
            <h3>Graph Execution Flow</h3>
            <div class="mermaid" id="graph">
graph TD;
    start([START]):::start
    agent[AGENT<br/>Query Analysis]:::node
    tools[TOOLS<br/>Currency Lookup]:::node  
    response[RESPONSE<br/>Generate Answer]:::node
    end([END]):::end
    
    start --> agent
    agent -.->|if currency needed| tools
    tools --> agent
    agent -.->|ready to respond| response
    response --> end
    
    classDef start fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef end fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef node fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef current fill:#ffeb3b,stroke:#f57f17,stroke-width:4px
    classDef completed fill:#4caf50,color:white,stroke:#2e7d32,stroke-width:2px
            </div>
        </div>
        
        <div class="log-container">
            <h3>Execution Log</h3>
            <div id="logs">
                <div class="log-entry info">
                    [SYSTEM] LangGraph monitoring ready. Click buttons to start execution.
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
    start([START])
    agent[AGENT<br/>Query Analysis]
    tools[TOOLS<br/>Currency Lookup]  
    response[RESPONSE<br/>Generate Answer]
    end([END])
    
    start --> agent
    agent -.->|if currency needed| tools
    tools --> agent
    agent -.->|ready to respond| response
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
            updateStatus('Running...');
            disableButtons(true);
            
            const steps = queryType === 'currency' ? [
                {node: 'start', desc: 'Query started', delay: 500},
                {node: 'agent', desc: 'Agent analyzing currency query', delay: 1200},
                {node: 'tools', desc: 'MCP server fetching exchange rate', delay: 1800},
                {node: 'agent', desc: 'Agent processing tool results', delay: 900},
                {node: 'response', desc: 'Generating structured response', delay: 700},
                {node: 'end', desc: 'Currency query completed', delay: 300}
            ] : [
                {node: 'start', desc: 'Query started', delay: 500},
                {node: 'agent', desc: 'Agent analyzing general query', delay: 1000},
                {node: 'response', desc: 'Responding non-currency topic', delay: 800},
                {node: 'end', desc: 'Response completed', delay: 300}
            ];
            
            let completedNodes = [];
            
            for (let i = 0; i < steps.length; i++) {
                const step = steps[i];
                updateGraph(step.node, completedNodes);
                addLog(`Running: ${step.desc}`, 'running');
                
                await new Promise(resolve => setTimeout(resolve, step.delay));
                
                addLog(`Completed: ${step.desc}`, 'completed');
                completedNodes.push(step.node);
                
                if (i === steps.length - 1) {
                    updateGraph(null, completedNodes);
                }
            }
            
            updateStatus('Completed');
            addLog('All execution completed!', 'completed');
            disableButtons(false);
        }
        
        async function runCurrencyQuery() {
            addLog('Currency query scenario started (USD to EUR)', 'info');
            await simulateExecution('currency');
        }
        
        async function runChatQuery() {
            addLog('General chat scenario started (weather inquiry)', 'info');
            await simulateExecution('chat');
        }
        
        function clearLogs() {
            document.getElementById('logs').innerHTML = 
                '<div class="log-entry info">[SYSTEM] Logs cleared.</div>';
        }
        
        // Initial graph render
        updateGraph(null, []);
        
        // Page load complete message
        window.addEventListener('load', function() {
            addLog('Web monitoring interface loaded', 'completed');
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
            print("LangGraph Live Monitor Server Started")
            print(f"URL: http://localhost:{port}")
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