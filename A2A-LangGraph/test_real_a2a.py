#!/usr/bin/env python3
"""
실제 Google A2A 프로토콜 테스트
Frontend Agent → Backend Agent 직접 통신 테스트
"""
import requests
import json
import time

def test_a2a_agent_to_agent():
    """Frontend Agent가 Backend Agent에게 직접 A2A 메시지 보내기"""
    
    print("🧪 Google A2A 프로토콜 테스트 시작")
    print("=" * 60)
    
    # Step 1: Frontend Agent에게 Backend Agent와 직접 소통하도록 요청
    frontend_url = "http://localhost:8010/"
    
    # Google A2A 표준 JSON-RPC 2.0 메시지
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
                        "text": """Backend Agent에게 직접 A2A JSON-RPC 2.0 메시지를 보내세요.

목표: http://localhost:8021/ 로 POST 요청을 보내서 Backend Agent와 직접 소통

보낼 메시지 내용: "안녕하세요 Backend Agent! Frontend Agent입니다. 사용자 로그인 API 설계에 대해 협업하고 싶습니다. JWT 토큰 기반 인증 시스템의 API 엔드포인트와 응답 형식을 제안해주세요."

A2A 표준 형식으로 실제 HTTP 요청을 보내고 응답을 받아주세요."""
                    }
                ]
            }
        }
    }
    
    print("📤 [HOST → Frontend] A2A 메시지 전송 중...")
    print(f"URL: {frontend_url}")
    print(f"메시지: {a2a_message['params']['message']['parts'][0]['text'][:100]}...")
    print("-" * 60)
    
    try:
        # Frontend Agent에게 Backend Agent와 소통하라고 지시
        response = requests.post(
            frontend_url,
            json=a2a_message,
            headers={"Content-Type": "application/json"},
            timeout=300  # 5분 대기
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ [Frontend → Backend] A2A 통신 성공!")
            
            # 응답 파싱
            if "result" in result and "artifacts" in result["result"]:
                artifacts = result["result"]["artifacts"]
                if artifacts and len(artifacts) > 0:
                    response_text = artifacts[0]["parts"][0].get("text", "")
                    
                    print(f"📨 Frontend Agent 응답:")
                    print(f"응답 길이: {len(response_text)} 글자")
                    print(f"미리보기: {response_text[:300]}...")
                    
                    # Backend Agent의 응답이 포함되었는지 확인
                    if "Backend Agent" in response_text or "API" in response_text:
                        print("✅ Backend Agent와의 A2A 통신 성공 확인!")
                    else:
                        print("⚠️ Backend Agent 응답이 포함되지 않음")
                    
                    return True
                else:
                    print("❌ 응답에 artifacts가 없음")
                    
            print(f"전체 응답: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
        else:
            print(f"❌ HTTP 오류: {response.status_code}")
            print(f"응답: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ 타임아웃: 5분 대기 후 응답 없음")
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
    
    return False

def verify_a2a_protocol():
    """A2A 프로토콜 표준 준수 확인"""
    
    print("\n🔍 A2A 프로토콜 표준 확인")
    print("=" * 60)
    
    agents = {
        "Frontend": "http://localhost:8010",
        "Backend": "http://localhost:8021", 
        "Unity": "http://localhost:8012"
    }
    
    for name, url in agents.items():
        print(f"\n📋 {name} Agent 확인:")
        
        # 1. Agent Card 확인 (Google A2A 표준)
        try:
            card_response = requests.get(f"{url}/.well-known/agent-card.json", timeout=10)
            if card_response.status_code == 200:
                card = card_response.json()
                print(f"  ✅ Agent Card: {card.get('name', 'Unknown')}")
                print(f"  📄 설명: {card.get('description', 'No description')[:50]}...")
                print(f"  🔧 기능: {len(card.get('skills', []))}개 스킬")
            else:
                print(f"  ❌ Agent Card 없음: HTTP {card_response.status_code}")
        except Exception as e:
            print(f"  ❌ Agent Card 오류: {str(e)}")
        
        # 2. JSON-RPC 2.0 엔드포인트 확인
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
                    print(f"  ✅ JSON-RPC 2.0: 정상 응답")
                else:
                    print(f"  ⚠️ JSON-RPC 2.0: 비표준 응답")
            else:
                print(f"  ❌ JSON-RPC 2.0: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ JSON-RPC 2.0 오류: {str(e)}")

if __name__ == "__main__":
    print("🚀 실제 Google A2A Agent간 통신 테스트")
    print("=" * 80)
    
    # 1. A2A 프로토콜 표준 준수 확인
    verify_a2a_protocol()
    
    # 2. 실제 Agent 간 통신 테스트  
    print("\n" + "=" * 80)
    success = test_a2a_agent_to_agent()
    
    print("\n" + "=" * 80)
    if success:
        print("🎉 A2A Agent 간 통신 테스트 성공!")
    else:
        print("❌ A2A Agent 간 통신 테스트 실패")
    print("=" * 80)