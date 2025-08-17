import requests
import json

def call_backend_via_a2a():
    """Call Backend Agent via A2A protocol"""
    
    url = "http://localhost:8021/api/message"
    
    payload = {
        "task": "Create a simple user profile API endpoint with GET and POST methods. Include fields: id, name, email, createdAt. Use in-memory storage for now.",
        "agent": "backend",
        "request_type": "api_creation"
    }
    
    try:
        print(f"[Backend Agent A2A] Sending request to {url}")
        print(f"[Backend Agent A2A] Payload: {json.dumps(payload, indent=2)}")
        print("[Backend Agent A2A] " + "-" * 60)
        
        response = requests.post(url, json=payload, timeout=30)
        
        print(f"[Backend Agent A2A] Status Code: {response.status_code}")
        print(f"[Backend Agent A2A] Response:")
        print(json.dumps(response.json(), indent=2))
        
        return response.json()
    except requests.exceptions.RequestException as e:
        return f"Error calling Backend Agent via A2A: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"

if __name__ == "__main__":
    result = call_backend_via_a2a()
    print("\nFinal Result:")
    print(result)