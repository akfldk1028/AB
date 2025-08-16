"""
Simple Web UI for testing currency conversion
"""

import requests
import threading
import webbrowser
import socketserver
from http.server import SimpleHTTPRequestHandler
import json
import urllib.parse

def create_ui_html():
    return """
<!DOCTYPE html>
<html>
<head>
    <title>Currency Converter Test</title>
    <style>
        body { font-family: Arial; margin: 40px; background: #f5f5f5; }
        .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
        .header { text-align: center; margin-bottom: 30px; }
        .input-group { margin: 20px 0; }
        .input-group label { display: block; margin-bottom: 5px; font-weight: bold; }
        .input-group input { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; font-size: 16px; }
        .btn { background: #007bff; color: white; border: none; padding: 15px 30px; border-radius: 5px; cursor: pointer; font-size: 16px; }
        .btn:hover { background: #0056b3; }
        .result { margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 5px; min-height: 50px; }
        .loading { color: #666; font-style: italic; }
        .error { color: #dc3545; }
        .success { color: #28a745; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏦 Currency Converter Test</h1>
            <p>Test the A2A Currency Agent system</p>
        </div>
        
        <div class="input-group">
            <label>Query:</label>
            <input type="text" id="queryInput" placeholder="Convert 100 USD to EUR" value="Convert 100 USD to EUR">
        </div>
        
        <button class="btn" onclick="testCurrency()">🚀 Test Currency Conversion</button>
        
        <div class="result" id="result">
            Ready to test currency conversion...
        </div>
    </div>

    <script>
        async function testCurrency() {
            const query = document.getElementById('queryInput').value;
            const resultDiv = document.getElementById('result');
            
            if (!query.trim()) {
                resultDiv.innerHTML = '<span class="error">Please enter a query</span>';
                return;
            }
            
            resultDiv.innerHTML = '<span class="loading">🔄 Processing request...</span>';
            
            try {
                const response = await fetch('/test', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        method: 'process_user_request',
                        params: {
                            query: query,
                            sessionId: 'web-ui-' + Date.now()
                        }
                    })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    resultDiv.innerHTML = `
                        <div class="success">
                            <strong>✅ Response:</strong><br>
                            ${JSON.stringify(data, null, 2)}
                        </div>
                    `;
                } else {
                    resultDiv.innerHTML = `
                        <div class="error">
                            <strong>❌ Error:</strong><br>
                            ${JSON.stringify(data, null, 2)}
                        </div>
                    `;
                }
            } catch (error) {
                resultDiv.innerHTML = `
                    <div class="error">
                        <strong>❌ Network Error:</strong><br>
                        ${error.message}
                    </div>
                `;
            }
        }
        
        // Enter key support
        document.getElementById('queryInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                testCurrency();
            }
        });
    </script>
</body>
</html>
    """

class CustomHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(create_ui_html().encode('utf-8'))
        else:
            super().do_GET()
    
    def do_POST(self):
        if self.path == '/test':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                request_data = json.loads(post_data.decode('utf-8'))
                
                # Forward request to Worker Agent
                worker_response = requests.post(
                    'http://localhost:8000/',
                    json=request_data,
                    headers={'Content-Type': 'application/json'},
                    timeout=30
                )
                
                self.send_response(worker_response.status_code)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(worker_response.content)
                
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                error_response = {'error': str(e)}
                self.wfile.write(json.dumps(error_response).encode('utf-8'))
        else:
            super().do_POST()

def start_server():
    port = 8090
    
    try:
        with socketserver.TCPServer(("", port), CustomHandler) as httpd:
            print(f"Currency Test UI started on http://localhost:{port}")
            print("Opening browser...")
            print("Press Ctrl+C to stop")
            
            # Open browser
            threading.Timer(1.0, lambda: webbrowser.open(f'http://localhost:{port}')).start()
            
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped")
    except Exception as e:
        print(f"Server error: {e}")

if __name__ == "__main__":
    start_server()