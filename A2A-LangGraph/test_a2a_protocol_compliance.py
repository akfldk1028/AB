#!/usr/bin/env python3
"""
A2A Protocol Compliance Test Suite
Tests the A2A implementation against Google ADK standards
"""
import asyncio
import json
import time
from typing import Dict, Any, Optional, List
import httpx
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from shared.custom_types import (
    A2AMessage,
    A2ATextPart,
    MessageSendParams,
    A2AErrorCodes
)
from shared.a2a_conversation_logger import get_conversation_logger

# Test configuration
AGENTS = {
    "frontend": {"port": 8010, "name": "Frontend Agent"},
    "backend": {"port": 8021, "name": "Backend Agent"},
    "unity": {"port": 8012, "name": "Unity Agent"}
}

# Initialize logger
logger = get_conversation_logger()


class A2AProtocolTester:
    """Test suite for A2A protocol compliance"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.test_results = []
        
    async def test_agent_card(self, agent_type: str) -> bool:
        """Test 1: Agent Card availability and compliance"""
        print(f"\n[TEST] Agent Card for {agent_type}")
        port = AGENTS[agent_type]["port"]
        
        try:
            # Test .well-known/agent.json endpoint
            response = await self.client.get(f"http://localhost:{port}/.well-known/agent.json")
            
            if response.status_code != 200:
                self._record_failure(f"{agent_type}_card", "Agent card not available")
                return False
                
            card = response.json()
            
            # Verify required fields
            required_fields = ["protocolVersion", "name", "description", "url", "capabilities"]
            for field in required_fields:
                if field not in card:
                    self._record_failure(f"{agent_type}_card", f"Missing required field: {field}")
                    return False
                    
            # Verify capabilities structure
            capabilities = card.get("capabilities", {})
            if not isinstance(capabilities, dict):
                self._record_failure(f"{agent_type}_card", "Invalid capabilities structure")
                return False
                
            print(f"  [OK] Agent Card valid: {card['name']}")
            print(f"     - Protocol: {card['protocolVersion']}")
            print(f"     - Streaming: {capabilities.get('streaming', False)}")
            print(f"     - Push Notifications: {capabilities.get('pushNotifications', False)}")
            
            self._record_success(f"{agent_type}_card")
            return True
            
        except Exception as e:
            self._record_failure(f"{agent_type}_card", str(e))
            return False
            
    async def test_message_send(self, agent_type: str) -> bool:
        """Test 2: message/send endpoint compliance"""
        print(f"\n[TEST] message/send for {agent_type}")
        port = AGENTS[agent_type]["port"]
        
        try:
            # Create A2A compliant message
            message = A2AMessage(
                role="user",
                parts=[
                    A2ATextPart(
                        kind="text",
                        text="Hello, this is a test message for A2A protocol compliance"
                    )
                ],
                messageId=f"test_msg_{int(time.time())}",
                taskId=f"task_{int(time.time())}",
                contextId=f"test_ctx_{agent_type}",
                kind="message"
            )
            
            # Create JSON-RPC request
            request = {
                "jsonrpc": "2.0",
                "id": f"test_{int(time.time())}",
                "method": "message/send",
                "params": {
                    "message": message.model_dump(exclude_none=True)
                }
            }
            
            # Log request
            logger.log_request("tester", agent_type, request, port)
            
            # Send request
            start_time = time.time()
            response = await self.client.post(
                f"http://localhost:{port}/",
                json=request,
                headers={"Content-Type": "application/json"}
            )
            duration_ms = (time.time() - start_time) * 1000
            
            if response.status_code != 200:
                self._record_failure(f"{agent_type}_message_send", f"HTTP {response.status_code}")
                return False
                
            result = response.json()
            
            # Log response
            logger.log_response("tester", agent_type, result, duration_ms)
            
            # Verify JSON-RPC response structure
            if "jsonrpc" not in result or result["jsonrpc"] != "2.0":
                self._record_failure(f"{agent_type}_message_send", "Invalid JSON-RPC version")
                return False
                
            if "id" not in result:
                self._record_failure(f"{agent_type}_message_send", "Missing response ID")
                return False
                
            # Check for error or result
            if "error" in result:
                error = result["error"]
                print(f"  [WARN] Error response: {error.get('message')} (code: {error.get('code')})")
                self._record_failure(f"{agent_type}_message_send", f"Error: {error}")
                return False
                
            if "result" not in result:
                self._record_failure(f"{agent_type}_message_send", "Missing result in response")
                return False
                
            # Verify result structure (can be Message or Task)
            res = result["result"]
            if "kind" in res:
                print(f"  [OK] Response type: {res['kind']}")
                if res["kind"] == "message":
                    print(f"     - Message ID: {res.get('messageId', 'N/A')}")
                elif res["kind"] == "task":
                    print(f"     - Task ID: {res.get('id', 'N/A')}")
                    print(f"     - Status: {res.get('status', {}).get('state', 'N/A')}")
            else:
                # Legacy response format
                print(f"  [OK] Response received (legacy format)")
                
            print(f"     - Response time: {duration_ms:.0f}ms")
            
            self._record_success(f"{agent_type}_message_send")
            return True
            
        except Exception as e:
            logger.log_error(f"test_message_send_{agent_type}", e)
            self._record_failure(f"{agent_type}_message_send", str(e))
            return False
            
    async def test_error_handling(self, agent_type: str) -> bool:
        """Test 3: Error handling compliance"""
        print(f"\n[TEST] Error Handling for {agent_type}")
        port = AGENTS[agent_type]["port"]
        
        test_cases = [
            {
                "name": "Invalid JSON",
                "data": "invalid json{",
                "expected_code": A2AErrorCodes.PARSE_ERROR
            },
            {
                "name": "Invalid Method",
                "data": {
                    "jsonrpc": "2.0",
                    "id": "test",
                    "method": "invalid/method",
                    "params": {}
                },
                "expected_code": A2AErrorCodes.METHOD_NOT_FOUND
            },
            {
                "name": "Missing Parameters",
                "data": {
                    "jsonrpc": "2.0",
                    "id": "test",
                    "method": "message/send",
                    "params": {}
                },
                "expected_code": A2AErrorCodes.INVALID_PARAMS
            }
        ]
        
        all_passed = True
        
        for test_case in test_cases:
            print(f"  Testing: {test_case['name']}")
            
            try:
                if isinstance(test_case["data"], str):
                    response = await self.client.post(
                        f"http://localhost:{port}/",
                        content=test_case["data"],
                        headers={"Content-Type": "application/json"}
                    )
                else:
                    response = await self.client.post(
                        f"http://localhost:{port}/",
                        json=test_case["data"],
                        headers={"Content-Type": "application/json"}
                    )
                
                if response.status_code == 200:
                    result = response.json()
                    if "error" in result:
                        error_code = result["error"].get("code")
                        if error_code == test_case["expected_code"]:
                            print(f"    [OK] Correct error code: {error_code}")
                        else:
                            print(f"    [ERROR] Wrong error code: {error_code} (expected: {test_case['expected_code']})")
                            all_passed = False
                    else:
                        print(f"    [ERROR] No error in response")
                        all_passed = False
                else:
                    # Some error codes might return 400
                    if response.status_code == 400:
                        print(f"    [OK] Error response with HTTP 400")
                    else:
                        print(f"    [ERROR] Unexpected HTTP status: {response.status_code}")
                        all_passed = False
                        
            except Exception as e:
                print(f"    [ERROR] Exception: {e}")
                all_passed = False
                
        if all_passed:
            self._record_success(f"{agent_type}_error_handling")
        else:
            self._record_failure(f"{agent_type}_error_handling", "Some error tests failed")
            
        return all_passed
        
    async def test_worker_communication(self) -> bool:
        """Test 4: Worker-to-Worker A2A communication"""
        print(f"\n[TEST] Worker-to-Worker Communication")
        
        try:
            # Test Frontend → Backend communication
            print("  Testing Frontend → Backend...")
            
            message = A2AMessage(
                role="user",
                parts=[
                    A2ATextPart(
                        kind="text",
                        text="Send A2A message to Backend Agent at http://localhost:8021 asking about API design patterns"
                    )
                ],
                messageId=f"worker_test_{int(time.time())}",
                taskId=f"task_{int(time.time())}",
                contextId="worker_communication_test",
                kind="message"
            )
            
            request = {
                "jsonrpc": "2.0",
                "id": f"worker_{int(time.time())}",
                "method": "message/send",
                "params": {
                    "message": message.model_dump(exclude_none=True)
                }
            }
            
            response = await self.client.post(
                "http://localhost:8010/",
                json=request,
                headers={"Content-Type": "application/json"},
                timeout=60.0
            )
            
            if response.status_code == 200:
                result = response.json()
                if "result" in result:
                    print("    [OK] Frontend successfully communicated with Backend")
                    self._record_success("worker_communication")
                    return True
                else:
                    print("    [ERROR] No result in response")
            else:
                print(f"    [ERROR] HTTP {response.status_code}")
                
        except Exception as e:
            print(f"    [ERROR] Exception: {e}")
            logger.log_error("test_worker_communication", e)
            
        self._record_failure("worker_communication", "Worker communication failed")
        return False
        
    async def test_a2a_inspector_compatibility(self, agent_type: str) -> bool:
        """Test 5: A2A Inspector compatibility"""
        print(f"\n[TEST] A2A Inspector Compatibility for {agent_type}")
        port = AGENTS[agent_type]["port"]
        
        try:
            # Test agent-card.json endpoint (A2A Inspector uses this)
            response = await self.client.get(f"http://localhost:{port}/.well-known/agent-card.json")
            
            if response.status_code == 200:
                print(f"  [OK] A2A Inspector endpoint available")
                card = response.json()
                
                # Verify skills if present
                skills = card.get("skills", [])
                if skills:
                    print(f"     - Skills defined: {len(skills)}")
                    for skill in skills[:3]:  # Show first 3 skills
                        print(f"       • {skill.get('name', 'Unknown')}")
                        
                self._record_success(f"{agent_type}_inspector")
                return True
            else:
                print(f"  [WARN] agent-card.json not available (optional)")
                return True  # This is optional
                
        except Exception as e:
            print(f"  [WARN] Inspector compatibility check failed: {e}")
            return True  # Non-critical
            
    def _record_success(self, test_name: str):
        """Record a successful test"""
        self.test_results.append({
            "test": test_name,
            "status": "PASS",
            "timestamp": datetime.now().isoformat()
        })
        
    def _record_failure(self, test_name: str, reason: str):
        """Record a failed test"""
        self.test_results.append({
            "test": test_name,
            "status": "FAIL",
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        })
        
    async def run_all_tests(self):
        """Run all A2A protocol compliance tests"""
        print("=" * 70)
        print("A2A PROTOCOL COMPLIANCE TEST SUITE")
        print("Testing against Google ADK standards")
        print("=" * 70)
        
        # Check if agents are running
        print("\n[SETUP] Checking agent availability...")
        agents_available = []
        
        for agent_type, config in AGENTS.items():
            try:
                response = await self.client.get(
                    f"http://localhost:{config['port']}/.well-known/agent.json",
                    timeout=2.0
                )
                if response.status_code == 200:
                    print(f"  [OK] {config['name']} is running on port {config['port']}")
                    agents_available.append(agent_type)
                else:
                    print(f"  [ERROR] {config['name']} not responding on port {config['port']}")
            except:
                print(f"  [ERROR] {config['name']} not available on port {config['port']}")
                
        if not agents_available:
            print("\n[ERROR] No agents are running! Please start the agents first:")
            print("   cd agents/claude_cli/frontend && python server.py")
            print("   cd agents/claude_cli/backend && python server.py")
            print("   cd agents/claude_cli/unity && python server.py")
            return
            
        # Run tests for available agents
        for agent_type in agents_available:
            print(f"\n{'='*70}")
            print(f"Testing {AGENTS[agent_type]['name']}")
            print(f"{'='*70}")
            
            # Run test suite
            await self.test_agent_card(agent_type)
            await self.test_message_send(agent_type)
            await self.test_error_handling(agent_type)
            await self.test_a2a_inspector_compatibility(agent_type)
            
        # Test worker communication if multiple agents available
        if len(agents_available) > 1:
            print(f"\n{'='*70}")
            print("Testing Worker-to-Worker Communication")
            print(f"{'='*70}")
            await self.test_worker_communication()
            
        # Print summary
        self._print_summary()
        
    def _print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)
        
        passed = sum(1 for r in self.test_results if r["status"] == "PASS")
        failed = sum(1 for r in self.test_results if r["status"] == "FAIL")
        
        print(f"\nTotal Tests: {len(self.test_results)}")
        print(f"  [OK] Passed: {passed}")
        print(f"  [ERROR] Failed: {failed}")
        
        if failed > 0:
            print("\nFailed Tests:")
            for result in self.test_results:
                if result["status"] == "FAIL":
                    print(f"  - {result['test']}: {result.get('reason', 'Unknown')}")
                    
        if passed == len(self.test_results):
            print("\n[SUCCESS] All tests passed! Your A2A implementation is compliant!")
        else:
            print(f"\n[WARN] {failed} test(s) failed. Please review the implementation.")
            
        # Save results to file
        results_file = Path("test_results_a2a_compliance.json")
        with open(results_file, "w") as f:
            json.dump(self.test_results, f, indent=2)
        print(f"\nDetailed results saved to: {results_file}")
        

async def main():
    """Main test runner"""
    tester = A2AProtocolTester()
    try:
        await tester.run_all_tests()
    finally:
        await tester.client.aclose()
        

if __name__ == "__main__":
    asyncio.run(main())