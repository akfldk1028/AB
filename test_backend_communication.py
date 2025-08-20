"""
Test script to communicate with Backend Agent
Using the function from CLAUDE.md
"""
import requests
import json
import time

def communicate_with_backend(message: str) -> str:
    """Send a message to the Backend Agent via A2A protocol"""
    
    agent_ports = {
        "frontend": 8010,
        "backend": 8021,
        "unity": 8012
    }
    
    port = agent_ports.get("backend")
    url = f"http://localhost:{port}/"
    
    # Google A2A protocol message format (strictly compliant)
    a2a_message = {
        "jsonrpc": "2.0",
        "id": f"host_to_backend_{int(time.time())}",
        "method": "message/send",
        "params": {
            "message": {
                "role": "user",
                "parts": [
                    {
                        "kind": "text",
                        "text": message,
                        "mimeType": "text/plain"
                    }
                ],
                "messageId": f"msg_{int(time.time())}",
                "kind": "message"
            }
        }
    }
    
    try:
        agent_name = "Backend Agent"
        print(f"\n[{agent_name}] A2A request initiated")
        print(f"[{agent_name}] URL: {url}")
        print(f"[{agent_name}] Message: {message[:100]}...")
        print(f"[{agent_name}] " + "-" * 60)
        
        response = requests.post(
            url, 
            json=a2a_message, 
            headers={"Content-Type": "application/json; charset=utf-8"},
            timeout=30  # 30 seconds for simple test
        )
        
        # Ensure response is properly encoded
        response.encoding = 'utf-8'
        
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
                message_resp = status.get("message", {})
                if message_resp and "parts" in message_resp:
                    parts = message_resp["parts"]
                    if parts and len(parts) > 0:
                        content = parts[0].get("text", "")
                        print(f"[{agent_name}] Status response: {len(content)} characters")
                        return content
            
            print(f"[{agent_name}] Warning: Unexpected response format")
            return str(result)
        else:
            error_msg = f"HTTP {response.status_code}: {response.text}"
            print(f"[{agent_name}] Error: {error_msg}")
            
            # If it's an internal server error, provide diagnostic info
            if response.status_code == 400 or response.status_code == 500:
                print(f"[{agent_name}] The Backend Agent server is running but experiencing issues.")
                print(f"[{agent_name}] This could be due to:")
                print(f"[{agent_name}]   - Claude CLI not being accessible from the agent")
                print(f"[{agent_name}]   - Message format incompatibility")
                print(f"[{agent_name}]   - Internal processing error in the agent")
            
            return f"Error from backend agent: {error_msg}"
            
    except requests.exceptions.ConnectionError:
        print(f"[{agent_name}] Connection failed - agent may not be running")
        return f"Connection failed - Backend Agent may not be running on port {port}"
    except requests.exceptions.Timeout:
        print(f"[{agent_name}] Request timed out after 30 seconds")
        return "Backend agent timed out"
    except Exception as e:
        print(f"[{agent_name}] Exception: {str(e)}")
        return f"Error calling backend agent: {str(e)}"


if __name__ == "__main__":
    # Test the communication
    print("=" * 80)
    print("Testing Backend Agent Communication")
    print("=" * 80)
    
    test_message = "Hello Backend Agent! This is a test message."
    result = communicate_with_backend(test_message)
    
    print("\n" + "=" * 80)
    print("Test Results:")
    print("-" * 80)
    print(f"Response: {result}")
    print("=" * 80)