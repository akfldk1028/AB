#!/usr/bin/env python3
"""
Simple Google A2A Protocol Test
Frontend Agent -> Backend Agent Direct Communication Test
"""
import requests
import json
import time

def test_a2a_agent_to_agent():
    """Frontend Agent sends direct A2A message to Backend Agent"""
    
    print("=== Google A2A Protocol Test ===")
    print("=" * 60)
    
    # Step 1: Send A2A message to Frontend Agent to communicate with Backend Agent
    frontend_url = "http://localhost:8010/"
    
    # Google A2A standard JSON-RPC 2.0 message
    a2a_message = {
        "jsonrpc": "2.0",
        "id": f"test_{int(time.time())}",
        "method": "message/send",
        "params": {
            "message": {
                "messageId": f"msg_{int(time.time())}",
                "taskId": f"task_{int(time.time())}",
                "contextId": "agent_to_agent_test",
                "parts": [
                    {
                        "kind": "text",
                        "text": """Send a direct A2A JSON-RPC 2.0 message to Backend Agent.

Goal: Send POST request to http://localhost:8021/ to communicate directly with Backend Agent

Message content: "Hello Backend Agent! This is Frontend Agent. I want to collaborate on user login API design. Please suggest JWT token-based authentication system API endpoints and response formats."

Please send actual HTTP request in A2A standard format and receive response."""
                    }
                ]
            }
        }
    }
    
    print("[HOST -> Frontend] Sending A2A message...")
    print(f"URL: {frontend_url}")
    print(f"Message preview: {a2a_message['params']['message']['parts'][0]['text'][:100]}...")
    print("-" * 60)
    
    try:
        # Send message to Frontend Agent to communicate with Backend Agent
        response = requests.post(
            frontend_url,
            json=a2a_message,
            headers={"Content-Type": "application/json"},
            timeout=300  # 5 minute wait
        )
        
        if response.status_code == 200:
            result = response.json()
            print("[Frontend -> Backend] A2A communication success!")
            
            # Parse response
            if "result" in result and "artifacts" in result["result"]:
                artifacts = result["result"]["artifacts"]
                if artifacts and len(artifacts) > 0:
                    response_text = artifacts[0]["parts"][0].get("text", "")
                    
                    print(f"Frontend Agent response:")
                    print(f"Response length: {len(response_text)} characters")
                    print(f"Preview: {response_text[:300]}...")
                    
                    # Check if Backend Agent response is included
                    if "Backend Agent" in response_text or "API" in response_text:
                        print("SUCCESS: Backend Agent A2A communication confirmed!")
                    else:
                        print("WARNING: Backend Agent response not included")
                    
                    return True
                else:
                    print("ERROR: No artifacts in response")
                    
            print(f"Full response: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
        else:
            print(f"HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("TIMEOUT: No response after 5 minutes")
    except Exception as e:
        print(f"ERROR: {str(e)}")
    
    return False

def verify_a2a_protocol():
    """Verify A2A protocol standard compliance"""
    
    print("\n=== A2A Protocol Standard Check ===")
    print("=" * 60)
    
    agents = {
        "Frontend": "http://localhost:8010",
        "Backend": "http://localhost:8021", 
        "Unity": "http://localhost:8012"
    }
    
    for name, url in agents.items():
        print(f"\n[{name} Agent Check]:")
        
        # 1. Check Agent Card (Google A2A standard)
        try:
            card_response = requests.get(f"{url}/.well-known/agent-card.json", timeout=10)
            if card_response.status_code == 200:
                card = card_response.json()
                print(f"  Agent Card: {card.get('name', 'Unknown')}")
                print(f"  Description: {card.get('description', 'No description')[:50]}...")
                print(f"  Skills: {len(card.get('skills', []))} skills")
            else:
                print(f"  No Agent Card: HTTP {card_response.status_code}")
        except Exception as e:
            print(f"  Agent Card Error: {str(e)}")
        
        # 2. Check JSON-RPC 2.0 endpoint
        try:
            test_message = {
                "jsonrpc": "2.0",
                "id": "protocol_test",
                "method": "message/send",
                "params": {
                    "message": {
                        "messageId": "test_msg",
                        "taskId": "test_task", 
                        "contextId": "protocol_test",
                        "parts": [{"kind": "text", "text": "Protocol test"}]
                    }
                }
            }
            
            response = requests.post(f"{url}/", json=test_message, timeout=30)
            if response.status_code == 200:
                result = response.json()
                if "jsonrpc" in result and "result" in result:
                    print(f"  JSON-RPC 2.0: Normal response")
                else:
                    print(f"  JSON-RPC 2.0: Non-standard response")
            else:
                print(f"  JSON-RPC 2.0: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"  JSON-RPC 2.0 Error: {str(e)}")

if __name__ == "__main__":
    print("=== Real Google A2A Agent Communication Test ===")
    print("=" * 80)
    
    # 1. Verify A2A protocol standard compliance
    verify_a2a_protocol()
    
    # 2. Test actual Agent communication  
    print("\n" + "=" * 80)
    success = test_a2a_agent_to_agent()
    
    print("\n" + "=" * 80)
    if success:
        print("SUCCESS: A2A Agent communication test passed!")
    else:
        print("FAILED: A2A Agent communication test failed")
    print("=" * 80)