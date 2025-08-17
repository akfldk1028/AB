import requests
import json
import time

def call_a2a_agent(agent_type: str, task: str) -> str:
    """Call an A2A worker agent via HTTP JSON-RPC 2.0"""
    
    agent_ports = {
        "frontend": 8010,
        "backend": 8021,
        "unity": 8012
    }
    
    port = agent_ports.get(agent_type)
    if not port:
        return f"Unknown agent type: {agent_type}"
    
    url = f"http://localhost:{port}/"
    
    # A2A protocol message format
    message = {
        "jsonrpc": "2.0",
        "id": f"host_to_{agent_type}_{int(time.time())}",
        "method": "message/send",
        "params": {
            "message": {
                "messageId": f"msg_{int(time.time())}",
                "taskId": f"task_{int(time.time())}",
                "contextId": "host_session",
                "parts": [{"kind": "text", "text": task}]
            }
        }
    }
    
    try:
        agent_name = f"{agent_type.capitalize()} Agent"
        print(f"\n[{agent_name}] A2A request initiated")
        print(f"[{agent_name}] URL: {url}")
        print(f"[{agent_name}] Task: {task[:100]}...")
        print(f"[{agent_name}] " + "-" * 60)
        
        response = requests.post(
            url, 
            json=message, 
            headers={"Content-Type": "application/json"},
            timeout=360  # 6 minutes for complex AI responses
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Extract response content from A2A protocol format
            if "result" in result:
                artifacts = result.get("result", {}).get("artifacts", [])
                if artifacts and len(artifacts) > 0:
                    parts = artifacts[0].get("parts", [])
                    if parts and len(parts) > 0:
                        content = parts[0].get("text", "")
                        print(f"[{agent_name}] Success: {len(content)} characters received")
                        return content
                
                # Fallback: check status message
                status = result.get("result", {}).get("status", {})
                message = status.get("message", {})
                if message and "parts" in message:
                    parts = message["parts"]
                    if parts and len(parts) > 0:
                        content = parts[0].get("text", "")
                        print(f"[{agent_name}] Status response: {len(content)} characters")
                        return content
            
            print(f"[{agent_name}] Warning: Unexpected response format")
            return str(result)
        else:
            error_msg = f"HTTP {response.status_code}: {response.text}"
            print(f"[{agent_name}] Error: {error_msg}")
            return f"Error from {agent_type} agent: {error_msg}"
            
    except requests.exceptions.Timeout:
        print(f"[{agent_name}] Timeout after 6 minutes")
        return f"{agent_type} agent timed out"
    except Exception as e:
        print(f"[{agent_name}] Exception: {str(e)}")
        return f"Error calling {agent_type} agent: {str(e)}"

# Execute the request to Frontend Agent
result = call_a2a_agent("frontend", "Create a simple React button component")
print("\n" + "="*80)
print("FRONTEND AGENT RESPONSE:")
print("="*80)
print(result)