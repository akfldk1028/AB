"""
Unit tests for CLI Agent Task Manager
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, Mock, patch
from pathlib import Path

from agents.claude_cli.base_cli_task_manager import CLIAgentTaskManager
from shared.custom_types import (
    TaskSendParams, SendTaskRequest, A2AMessageSendRequest, 
    TaskState, TaskStatus, Message, TextPart, Task
)


class TestCLIAgentTaskManager:
    """Test cases for CLI Agent Task Manager"""
    
    @pytest.mark.asyncio
    async def test_task_manager_initialization(self, frontend_task_manager):
        """Test task manager initialization"""
        assert frontend_task_manager.agent is not None
        assert frontend_task_manager.notification_sender_auth is not None
    
    @pytest.mark.asyncio
    async def test_get_user_query(self, frontend_task_manager, sample_task_params):
        """Test user query extraction"""
        query = frontend_task_manager._get_user_query(sample_task_params)
        assert query == "Test query for agent"
    
    @pytest.mark.asyncio
    async def test_get_user_query_invalid_part(self, frontend_task_manager):
        """Test user query extraction with invalid part type"""
        invalid_params = TaskSendParams(
            id="test_task",
            sessionId="test_session",
            message=Message(role="user", parts=[{"type": "invalid", "data": "test"}])
        )
        
        with pytest.raises(ValueError, match="Only text parts are supported"):
            frontend_task_manager._get_user_query(invalid_params)
    
    @pytest.mark.asyncio
    async def test_validate_request_valid(self, frontend_task_manager):
        """Test request validation with valid request"""
        request = SendTaskRequest(
            id="test_request",
            method="send_task",
            params=TaskSendParams(
                id="test_task",
                sessionId="test_session",
                message=Message(role="user", parts=[TextPart(text="test")])
            )
        )
        
        result = frontend_task_manager._validate_request(request)
        assert result is None  # No validation error
    
    @pytest.mark.asyncio
    async def test_validate_request_incompatible_types(self, frontend_task_manager):
        """Test request validation with incompatible content types"""
        request = SendTaskRequest(
            id="test_request",
            method="send_task",
            params=TaskSendParams(
                id="test_task",
                sessionId="test_session",
                message=Message(role="user", parts=[TextPart(text="test")]),
                acceptedOutputModes=["image", "video"]  # Incompatible with agent
            )
        )
        
        result = frontend_task_manager._validate_request(request)
        assert result is not None
        assert result.error is not None
    
    @pytest.mark.asyncio
    async def test_on_send_task_success(self, frontend_task_manager, mock_claude_cli_response):
        """Test successful task sending"""
        request = SendTaskRequest(
            id="test_request",
            method="send_task",
            params=TaskSendParams(
                id="test_task",
                sessionId="test_session",
                message=Message(role="user", parts=[TextPart(text="Create a component")])
            )
        )
        
        # Mock the agent's invoke_async method
        frontend_task_manager.agent.invoke_async = AsyncMock(return_value=mock_claude_cli_response)
        
        # Mock task store operations
        frontend_task_manager.upsert_task = AsyncMock()
        frontend_task_manager.update_store = AsyncMock(return_value=Task(
            id="test_task",
            status=TaskStatus(state=TaskState.COMPLETED),
            sessionId="test_session"
        ))
        frontend_task_manager.send_task_notification = AsyncMock()
        frontend_task_manager.append_task_history = Mock(return_value=Task(
            id="test_task",
            status=TaskStatus(state=TaskState.COMPLETED),
            sessionId="test_session"
        ))
        
        response = await frontend_task_manager.on_send_task(request)
        
        assert response.id == "test_request"
        assert response.result is not None
        assert response.error is None
    
    @pytest.mark.asyncio
    async def test_on_send_task_agent_error(self, frontend_task_manager):
        """Test task sending with agent error"""
        request = SendTaskRequest(
            id="test_request",
            method="send_task",
            params=TaskSendParams(
                id="test_task",
                sessionId="test_session",
                message=Message(role="user", parts=[TextPart(text="Create a component")])
            )
        )
        
        # Mock agent error
        frontend_task_manager.agent.invoke_async = AsyncMock(side_effect=Exception("Agent error"))
        
        # Mock task store operations
        frontend_task_manager.upsert_task = AsyncMock()
        frontend_task_manager.update_store = AsyncMock()
        frontend_task_manager.send_task_notification = AsyncMock()
        
        with pytest.raises(ValueError, match="Error invoking agent"):
            await frontend_task_manager.on_send_task(request)
    
    @pytest.mark.asyncio
    async def test_on_a2a_message_send_success(self, frontend_task_manager, sample_a2a_message_request, mock_claude_cli_response):
        """Test successful A2A message handling"""
        # Mock the agent's invoke_async method
        frontend_task_manager.agent.invoke_async = AsyncMock(return_value=mock_claude_cli_response)
        
        # Mock task store operations
        frontend_task_manager.upsert_task = AsyncMock()
        frontend_task_manager.update_store = AsyncMock(return_value=Task(
            id="task_test_001",
            status=TaskStatus(state=TaskState.COMPLETED),
            sessionId="session_test_001"
        ))
        
        response = await frontend_task_manager.on_a2a_message_send(sample_a2a_message_request)
        
        assert response.id == "test_a2a_request_123"
        assert response.result is not None
        assert response.error is None
    
    @pytest.mark.asyncio
    async def test_on_a2a_message_send_input_required(self, frontend_task_manager, sample_a2a_message_request):
        """Test A2A message handling with input required"""
        # Mock agent response requiring input
        mock_response = {
            "is_task_complete": False,
            "require_user_input": True,
            "content": "Need more information"
        }
        frontend_task_manager.agent.invoke_async = AsyncMock(return_value=mock_response)
        
        # Mock task store operations
        frontend_task_manager.upsert_task = AsyncMock()
        frontend_task_manager.update_store = AsyncMock(return_value=Task(
            id="task_test_001",
            status=TaskStatus(state=TaskState.INPUT_REQUIRED),
            sessionId="session_test_001"
        ))
        
        response = await frontend_task_manager.on_a2a_message_send(sample_a2a_message_request)
        
        assert response.id == "test_a2a_request_123"
        assert response.result is not None
        assert response.result.status.state == TaskState.INPUT_REQUIRED
    
    @pytest.mark.asyncio
    async def test_on_a2a_message_send_error(self, frontend_task_manager, sample_a2a_message_request):
        """Test A2A message handling with error"""
        # Mock agent error
        frontend_task_manager.agent.invoke_async = AsyncMock(side_effect=Exception("Agent error"))
        frontend_task_manager.upsert_task = AsyncMock()
        
        response = await frontend_task_manager.on_a2a_message_send(sample_a2a_message_request)
        
        assert response.id == "test_a2a_request_123"
        assert response.result is None
        assert response.error is not None
        assert "Error processing A2A message" in response.error.message
    
    @pytest.mark.asyncio
    async def test_send_task_notification_no_push_info(self, frontend_task_manager):
        """Test task notification when no push info exists"""
        task = Task(
            id="test_task",
            status=TaskStatus(state=TaskState.COMPLETED),
            sessionId="test_session"
        )
        
        frontend_task_manager.has_push_notification_info = AsyncMock(return_value=False)
        
        # Should not raise an error, just log and return
        await frontend_task_manager.send_task_notification(task)
        
        frontend_task_manager.has_push_notification_info.assert_called_once_with("test_task")
    
    @pytest.mark.asyncio
    async def test_send_task_notification_with_push_info(self, frontend_task_manager):
        """Test task notification with push info"""
        task = Task(
            id="test_task",
            status=TaskStatus(state=TaskState.COMPLETED),
            sessionId="test_session"
        )
        
        mock_push_info = Mock()
        mock_push_info.url = "https://example.com/webhook"
        
        frontend_task_manager.has_push_notification_info = AsyncMock(return_value=True)
        frontend_task_manager.get_push_notification_info = AsyncMock(return_value=mock_push_info)
        
        await frontend_task_manager.send_task_notification(task)
        
        frontend_task_manager.notification_sender_auth.send_push_notification.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_set_push_notification_info_success(self, frontend_task_manager):
        """Test successful push notification info setting"""
        from shared.custom_types import PushNotificationConfig
        
        push_config = PushNotificationConfig(url="https://example.com/webhook")
        
        # Mock parent class method
        with patch.object(CLIAgentTaskManager.__bases__[0], 'set_push_notification_info') as mock_parent:
            mock_parent.return_value = AsyncMock()
            
            result = await frontend_task_manager.set_push_notification_info("test_task", push_config)
            
            assert result is True
            frontend_task_manager.notification_sender_auth.verify_push_notification_url.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_set_push_notification_info_verification_failed(self, frontend_task_manager):
        """Test push notification info setting with verification failure"""
        from shared.custom_types import PushNotificationConfig
        
        push_config = PushNotificationConfig(url="https://invalid-url.com/webhook")
        
        # Mock verification failure
        frontend_task_manager.notification_sender_auth.verify_push_notification_url = AsyncMock(return_value=False)
        
        result = await frontend_task_manager.set_push_notification_info("test_task", push_config)
        
        assert result is False