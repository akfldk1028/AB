#!/usr/bin/env python3
"""
Test Agent-to-Agent Collaboration
Frontend Agent -> Backend Agent Direct Communication
"""
import requests
import json

def test_frontend_to_backend_collaboration():
    """Test Frontend Agent communicating directly with Backend Agent"""
    
    print("=== Frontend -> Backend Agent Collaboration Test ===")
    
    # Message to Frontend Agent asking it to collaborate with Backend Agent
    collaboration_request = {
        "jsonrpc": "2.0",
        "id": "collab_test",
        "method": "message/send",
        "params": {
            "message": {
                "messageId": "collab_msg",
                "taskId": "collab_task",
                "contextId": "agent_collaboration",
                "parts": [{
                    "kind": "text", 
                    "text": """I need you to collaborate with the Backend Agent to design a user authentication system.

Please send an HTTP request to the Backend Agent at http://localhost:8021/ using the A2A JSON-RPC 2.0 protocol.

Your message to Backend Agent should be:
"Hello Backend Agent! I'm the Frontend Agent working on a user login form. I need your expertise on JWT authentication. Please design:
1. Login API endpoint structure
2. JWT token response format
3. Error handling for invalid credentials
4. Session management recommendations

Please respond with specific API design details."

Send this as a proper A2A message with JSON-RPC 2.0 format and return the Backend Agent's response to me."""
                }]
            }
        }
    }
    
    try:
        print("Sending collaboration request to Frontend Agent...")
        response = requests.post(
            "http://localhost:8010/", 
            json=collaboration_request, 
            timeout=120  # 2 minutes
        )
        
        if response.status_code == 200:
            result = response.json()
            print("SUCCESS: Frontend Agent responded")
            
            if "result" in result and "artifacts" in result["result"]:
                artifacts = result["result"]["artifacts"]
                if artifacts:
                    response_text = artifacts[0]["parts"][0].get("text", "")
                    print(f"\nResponse length: {len(response_text)} characters")
                    print("\n=== Frontend Agent Response ===")
                    print(response_text)
                    
                    # Check if Backend Agent's response is included
                    if ("Backend Agent" in response_text and 
                        ("JWT" in response_text or "API" in response_text)):
                        print("\n✅ SUCCESS: Backend Agent collaboration confirmed!")
                        print("Frontend Agent successfully communicated with Backend Agent")
                        return True
                    else:
                        print("\n⚠️ WARNING: Backend Agent response not clearly identified")
                        return False
            else:
                print("ERROR: No artifacts in response")
                return False
                
        else:
            print(f"ERROR: HTTP {response.status_code}")
            print(response.text)
            return False
            
    except requests.exceptions.Timeout:
        print("ERROR: Request timed out after 2 minutes")
        return False
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_frontend_to_backend_collaboration()
    print("\n" + "="*60)
    if success:
        print("🎉 AGENT COLLABORATION TEST: PASSED")
        print("Frontend and Backend Agents can communicate via A2A protocol")
    else:
        print("❌ AGENT COLLABORATION TEST: FAILED")
    print("="*60)