"""
Integration tests for the Claude CLI Multi-Agent A2A System
"""
import pytest
import asyncio
import json
import aiohttp
from unittest.mock import patch, AsyncMock
from typing import Dict, Any

from shared.custom_types import A2AMessageSendRequest, A2AMessage, A2AMessagePart


class TestA2AIntegration:
    """Integration tests for A2A protocol"""
    
    @pytest.mark.asyncio
    async def test_frontend_agent_a2a_message_flow(self):
        """Test complete A2A message flow with Frontend agent"""
        # Mock A2A message request
        request_data = {
            "jsonrpc": "2.0",
            "id": "test_frontend_123",
            "method": "message/send",
            "params": {
                "message": {
                    "messageId": "msg_frontend_001",
                    "taskId": "task_frontend_component",
                    "contextId": "session_frontend_001",
                    "parts": [
                        {
                            "kind": "text",
                            "text": "Create a simple React login form"
                        }
                    ]
                }
            }
        }
        
        # This would test the actual HTTP endpoint if running
        # For now, we test the message parsing
        message = A2AMessage(**request_data["params"]["message"])
        assert message.messageId == "msg_frontend_001"
        assert message.taskId == "task_frontend_component"
        assert len(message.parts) == 1
        assert message.parts[0].text == "Create a simple React login form"
    
    @pytest.mark.asyncio
    async def test_backend_agent_a2a_message_flow(self):
        """Test complete A2A message flow with Backend agent"""
        request_data = {
            "jsonrpc": "2.0",
            "id": "test_backend_123",
            "method": "message/send",
            "params": {
                "message": {
                    "messageId": "msg_backend_001",
                    "taskId": "task_backend_api",
                    "contextId": "session_backend_001",
                    "parts": [
                        {
                            "kind": "text",
                            "text": "Create a REST API for user authentication"
                        }
                    ]
                }
            }
        }
        
        message = A2AMessage(**request_data["params"]["message"])
        assert message.messageId == "msg_backend_001"
        assert message.taskId == "task_backend_api"
        assert len(message.parts) == 1
        assert message.parts[0].text == "Create a REST API for user authentication"
    
    @pytest.mark.asyncio
    async def test_unity_agent_a2a_message_flow(self):
        """Test complete A2A message flow with Unity agent"""
        request_data = {
            "jsonrpc": "2.0",
            "id": "test_unity_123",
            "method": "message/send",
            "params": {
                "message": {
                    "messageId": "msg_unity_001",
                    "taskId": "task_unity_controller",
                    "contextId": "session_unity_001",
                    "parts": [
                        {
                            "kind": "text",
                            "text": "Create a Unity character movement script"
                        }
                    ]
                }
            }
        }
        
        message = A2AMessage(**request_data["params"]["message"])
        assert message.messageId == "msg_unity_001"
        assert message.taskId == "task_unity_controller"
        assert len(message.parts) == 1
        assert message.parts[0].text == "Create a Unity character movement script"


class TestMultiAgentCoordination:
    """Tests for multi-agent coordination scenarios"""
    
    @pytest.mark.asyncio
    async def test_fullstack_app_coordination(self):
        """Test coordination between Frontend and Backend agents for full-stack app"""
        # This would test the Host agent coordinating between multiple agents
        frontend_task = "Create a React dashboard with user management"
        backend_task = "Create REST APIs for user CRUD operations"
        
        # Mock coordination logic
        tasks = {
            "frontend": {"agent": "frontend", "task": frontend_task},
            "backend": {"agent": "backend", "task": backend_task}
        }
        
        # Verify task distribution
        assert tasks["frontend"]["agent"] == "frontend"
        assert tasks["backend"]["agent"] == "backend"
        assert "React" in tasks["frontend"]["task"]
        assert "REST API" in tasks["backend"]["task"]
    
    @pytest.mark.asyncio
    async def test_game_with_backend_coordination(self):
        """Test coordination between Unity and Backend agents for game with backend"""
        unity_task = "Create Unity multiplayer game client"
        backend_task = "Create game server with leaderboard API"
        
        tasks = {
            "unity": {"agent": "unity", "task": unity_task},
            "backend": {"agent": "backend", "task": backend_task}
        }
        
        assert tasks["unity"]["agent"] == "unity"
        assert tasks["backend"]["agent"] == "backend"
        assert "Unity" in tasks["unity"]["task"]
        assert "leaderboard" in tasks["backend"]["task"]


class TestErrorHandling:
    """Tests for error handling in integration scenarios"""
    
    @pytest.mark.asyncio
    async def test_claude_cli_subprocess_failure(self):
        """Test handling of Claude CLI subprocess failures"""
        # Mock subprocess failure
        with patch('asyncio.create_subprocess_exec') as mock_subprocess:
            mock_process = AsyncMock()
            mock_process.returncode = 1
            mock_process.communicate = AsyncMock(return_value=(b"", b"Command failed"))
            mock_subprocess.return_value = mock_process
            
            from agents.claude_cli.frontend.agent import FrontendCLIAgent
            agent = FrontendCLIAgent()
            
            result = await agent.invoke_claude_cli("test query", "test_session")
            
            assert result["is_task_complete"] is False
            assert result["require_user_input"] is True
            assert "Error from Claude CLI" in result["content"]
    
    @pytest.mark.asyncio
    async def test_claude_cli_subprocess_timeout(self):
        """Test handling of Claude CLI subprocess timeouts"""
        with patch('asyncio.create_subprocess_exec') as mock_subprocess:
            mock_process = AsyncMock()
            mock_process.communicate = AsyncMock(side_effect=asyncio.TimeoutError())
            mock_subprocess.return_value = mock_process
            
            from agents.claude_cli.backend.agent import BackendCLIAgent
            agent = BackendCLIAgent()
            
            result = await agent.invoke_claude_cli("test query", "test_session")
            
            assert result["is_task_complete"] is False
            assert result["require_user_input"] is True
            assert "timed out" in result["content"]
    
    @pytest.mark.asyncio
    async def test_claude_cli_file_not_found(self):
        """Test handling when Claude CLI is not found"""
        with patch('asyncio.create_subprocess_exec') as mock_subprocess:
            mock_subprocess.side_effect = FileNotFoundError("claude not found")
            
            from agents.claude_cli.unity.agent import UnityCLIAgent
            agent = UnityCLIAgent()
            
            result = await agent.invoke_claude_cli("test query", "test_session")
            
            assert result["is_task_complete"] is False
            assert result["require_user_input"] is True
            assert "Claude CLI not found" in result["content"]


class TestPerformance:
    """Performance tests for the multi-agent system"""
    
    @pytest.mark.asyncio
    async def test_concurrent_agent_requests(self):
        """Test handling of concurrent requests to multiple agents"""
        from agents.claude_cli.frontend.agent import FrontendCLIAgent
        from agents.claude_cli.backend.agent import BackendCLIAgent
        from agents.claude_cli.unity.agent import UnityCLIAgent
        
        # Mock successful responses for all agents
        with patch('asyncio.create_subprocess_exec') as mock_subprocess:
            mock_process = AsyncMock()
            mock_process.returncode = 0
            mock_process.communicate = AsyncMock(return_value=(b"Mock response", b""))
            mock_subprocess.return_value = mock_process
            
            frontend_agent = FrontendCLIAgent()
            backend_agent = BackendCLIAgent()
            unity_agent = UnityCLIAgent()
            
            # Run concurrent requests
            tasks = [
                frontend_agent.invoke_async("Create React component", "session1"),
                backend_agent.invoke_async("Create REST API", "session2"),
                unity_agent.invoke_async("Create character controller", "session3")
            ]
            
            results = await asyncio.gather(*tasks)
            
            # All should succeed
            assert len(results) == 3
            for result in results:
                assert result["is_task_complete"] is True
                assert "Mock response" in result["content"]
    
    @pytest.mark.asyncio
    async def test_streaming_performance(self):
        """Test streaming response performance"""
        with patch('asyncio.create_subprocess_exec') as mock_subprocess:
            mock_process = AsyncMock()
            mock_process.returncode = 0
            mock_process.communicate = AsyncMock(return_value=(b"Mock streaming response", b""))
            mock_subprocess.return_value = mock_process
            
            from agents.claude_cli.frontend.agent import FrontendCLIAgent
            agent = FrontendCLIAgent()
            
            start_time = asyncio.get_event_loop().time()
            
            responses = []
            async for response in agent.stream("Create complex component", "test_session"):
                responses.append(response)
            
            end_time = asyncio.get_event_loop().time()
            duration = end_time - start_time
            
            # Should complete within reasonable time
            assert duration < 5.0  # 5 seconds max
            assert len(responses) == 2  # Initial + final response


class TestDataIntegrity:
    """Tests for data integrity across the system"""
    
    @pytest.mark.asyncio
    async def test_task_state_consistency(self, frontend_task_manager, mock_claude_cli_response):
        """Test that task states remain consistent throughout processing"""
        from shared.custom_types import SendTaskRequest, TaskSendParams, Message, TextPart
        
        request = SendTaskRequest(
            id="test_request",
            method="send_task",
            params=TaskSendParams(
                id="test_task",
                sessionId="test_session",
                message=Message(role="user", parts=[TextPart(text="Test task")])
            )
        )
        
        # Mock all necessary methods
        frontend_task_manager.agent.invoke_async = AsyncMock(return_value=mock_claude_cli_response)
        frontend_task_manager.upsert_task = AsyncMock()
        frontend_task_manager.send_task_notification = AsyncMock()
        
        # Track task state changes
        task_states = []
        
        async def mock_update_store(task_id, status, artifacts):
            task_states.append(status.state)
            return Mock(id=task_id, status=status, sessionId="test_session")
        
        frontend_task_manager.update_store = mock_update_store
        frontend_task_manager.append_task_history = Mock(side_effect=lambda task, _: task)
        
        await frontend_task_manager.on_send_task(request)
        
        # Should have proper state progression
        assert len(task_states) >= 1
        # Final state should be appropriate for the response
        if mock_claude_cli_response["require_user_input"]:
            assert task_states[-1] in ["input-required", "working"]
        else:
            assert task_states[-1] == "completed"
    
    @pytest.mark.asyncio
    async def test_session_id_consistency(self):
        """Test that session IDs are maintained consistently"""
        session_id = "test_session_123"
        
        # Test with different message formats
        from shared.custom_types import TaskSendParams, Message, TextPart, A2AMessage, A2AMessagePart
        
        # Internal task format
        task_params = TaskSendParams(
            id="test_task",
            sessionId=session_id,
            message=Message(role="user", parts=[TextPart(text="test")])
        )
        
        # A2A format
        a2a_message = A2AMessage(
            messageId="msg_001",
            taskId="test_task",
            contextId=session_id,
            parts=[A2AMessagePart(kind="text", text="test")]
        )
        
        # Both should reference the same session
        assert task_params.sessionId == session_id
        assert a2a_message.contextId == session_id