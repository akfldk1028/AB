"""
Tests for A2A Protocol compliance and functionality
"""
import pytest
import json
from unittest.mock import AsyncMock, Mock

from shared.custom_types import (
    A2AMessageSendRequest, A2AMessageSendResponse, A2AMessage, A2AMessagePart,
    Task, TaskStatus, TaskState, Message, TextPart, Artifact
)


class TestA2AProtocolCompliance:
    """Test A2A protocol compliance"""
    
    def test_a2a_message_structure(self):
        """Test A2A message structure compliance"""
        message = A2AMessage(
            messageId="msg_001",
            taskId="task_001", 
            contextId="session_001",
            parts=[A2AMessagePart(kind="text", text="Test message")]
        )
        
        assert message.messageId == "msg_001"
        assert message.taskId == "task_001"
        assert message.contextId == "session_001"
        assert len(message.parts) == 1
        assert message.parts[0].kind == "text"
        assert message.parts[0].text == "Test message"
    
    def test_a2a_message_send_request_structure(self):
        """Test A2A message/send request structure"""
        request = A2AMessageSendRequest(
            id="request_123",
            method="message/send",
            params={
                "message": A2AMessage(
                    messageId="msg_001",
                    taskId="task_001",
                    contextId="session_001",
                    parts=[A2AMessagePart(kind="text", text="Test")]
                )
            }
        )
        
        assert request.id == "request_123"
        assert request.method == "message/send"
        assert request.params["message"].messageId == "msg_001"
    
    def test_a2a_message_send_response_structure(self):
        """Test A2A message/send response structure"""
        task = Task(
            id="task_001",
            status=TaskStatus(state=TaskState.COMPLETED),
            sessionId="session_001"
        )
        
        response = A2AMessageSendResponse(
            id="request_123",
            result=task
        )
        
        assert response.id == "request_123"
        assert response.result is not None
        assert response.result.id == "task_001"
        assert response.error is None
    
    def test_a2a_message_send_response_error(self):
        """Test A2A message/send response with error"""
        from shared.custom_types import InternalError
        
        response = A2AMessageSendResponse(
            id="request_123",
            error=InternalError(message="Test error")
        )
        
        assert response.id == "request_123"
        assert response.result is None
        assert response.error is not None
        assert response.error.message == "Test error"
    
    def test_a2a_message_multiple_parts(self):
        """Test A2A message with multiple parts"""
        message = A2AMessage(
            messageId="msg_002",
            taskId="task_002",
            contextId="session_002",
            parts=[
                A2AMessagePart(kind="text", text="First part"),
                A2AMessagePart(kind="text", text="Second part")
            ]
        )
        
        assert len(message.parts) == 2
        assert message.parts[0].text == "First part"
        assert message.parts[1].text == "Second part"


class TestA2AMessageProcessing:
    """Test A2A message processing logic"""
    
    @pytest.mark.asyncio
    async def test_extract_text_from_a2a_message(self):
        """Test extracting text content from A2A message parts"""
        message = A2AMessage(
            messageId="msg_001",
            taskId="task_001",
            contextId="session_001",
            parts=[
                A2AMessagePart(kind="text", text="First part. "),
                A2AMessagePart(kind="text", text="Second part.")
            ]
        )
        
        # Simulate the extraction logic from task manager
        message_text = ""
        for part in message.parts:
            if part.kind == "text":
                message_text += part.text
        
        assert message_text == "First part. Second part."
    
    @pytest.mark.asyncio 
    async def test_convert_a2a_to_internal_task(self):
        """Test converting A2A message to internal task format"""
        a2a_message = A2AMessage(
            messageId="msg_001",
            taskId="task_001",
            contextId="session_001",
            parts=[A2AMessagePart(kind="text", text="Create a React component")]
        )
        
        # Conversion logic from task manager
        message_text = ""
        for part in a2a_message.parts:
            if part.kind == "text":
                message_text += part.text
        
        from shared.custom_types import TaskSendParams
        task_params = TaskSendParams(
            id=a2a_message.taskId,
            sessionId=a2a_message.contextId,
            message=Message(role="user", parts=[TextPart(text=message_text)])
        )
        
        assert task_params.id == "task_001"
        assert task_params.sessionId == "session_001"
        assert task_params.message.parts[0].text == "Create a React component"
    
    @pytest.mark.asyncio
    async def test_convert_internal_response_to_a2a(self):
        """Test converting internal response to A2A format"""
        # Mock internal agent response
        agent_response = {
            "is_task_complete": True,
            "require_user_input": False,
            "content": "Here's your React component code..."
        }
        
        # Conversion logic from task manager
        if agent_response.get("is_task_complete", False):
            task_status = TaskStatus(state=TaskState.COMPLETED)
            artifact = Artifact(parts=[TextPart(text=agent_response["content"])])
        else:
            task_status = TaskStatus(
                state=TaskState.INPUT_REQUIRED,
                message=Message(role="agent", parts=[TextPart(text=agent_response["content"])])
            )
            artifact = None
        
        task = Task(
            id="task_001",
            status=task_status,
            sessionId="session_001",
            artifacts=[artifact] if artifact else None
        )
        
        response = A2AMessageSendResponse(id="request_123", result=task)
        
        assert response.result.status.state == TaskState.COMPLETED
        assert response.result.artifacts is not None
        assert len(response.result.artifacts) == 1
        assert response.result.artifacts[0].parts[0].text == "Here's your React component code..."


class TestA2AProtocolValidation:
    """Test A2A protocol validation and error handling"""
    
    def test_a2a_message_missing_required_fields(self):
        """Test validation of A2A message with missing required fields"""
        with pytest.raises(Exception):  # Pydantic validation error
            A2AMessage(
                # Missing messageId
                taskId="task_001",
                contextId="session_001",
                parts=[A2AMessagePart(kind="text", text="Test")]
            )
    
    def test_a2a_message_part_invalid_kind(self):
        """Test validation of A2A message part with invalid kind"""
        # Note: This depends on how strict the validation is
        # If kind is open-ended, this might pass
        part = A2AMessagePart(kind="invalid_kind", text="Test")
        assert part.kind == "invalid_kind"  # Should be allowed for extensibility
    
    def test_a2a_request_invalid_method(self):
        """Test A2A request with invalid method"""
        # This should still be parseable but might be rejected by handlers
        request = A2AMessageSendRequest(
            id="request_123",
            method="invalid/method",  # Invalid method
            params={
                "message": A2AMessage(
                    messageId="msg_001",
                    taskId="task_001",
                    contextId="session_001",
                    parts=[A2AMessagePart(kind="text", text="Test")]
                )
            }
        )
        
        assert request.method == "invalid/method"
        # Handler would reject this, but structure is valid


class TestA2AJSONSerialization:
    """Test JSON serialization/deserialization for A2A protocol"""
    
    def test_a2a_message_json_serialization(self):
        """Test A2A message JSON serialization"""
        message = A2AMessage(
            messageId="msg_001",
            taskId="task_001",
            contextId="session_001",
            parts=[A2AMessagePart(kind="text", text="Test message")]
        )
        
        # Serialize to dict (Pydantic)
        message_dict = message.model_dump()
        
        assert message_dict["messageId"] == "msg_001"
        assert message_dict["taskId"] == "task_001"
        assert message_dict["contextId"] == "session_001"
        assert len(message_dict["parts"]) == 1
        assert message_dict["parts"][0]["kind"] == "text"
        assert message_dict["parts"][0]["text"] == "Test message"
    
    def test_a2a_request_json_serialization(self):
        """Test A2A request JSON serialization"""
        request = A2AMessageSendRequest(
            id="request_123",
            method="message/send",
            params={
                "message": A2AMessage(
                    messageId="msg_001",
                    taskId="task_001",
                    contextId="session_001",
                    parts=[A2AMessagePart(kind="text", text="Test")]
                )
            }
        )
        
        request_dict = request.model_dump()
        
        assert request_dict["id"] == "request_123"
        assert request_dict["method"] == "message/send"
        assert "message" in request_dict["params"]
        assert request_dict["params"]["message"]["messageId"] == "msg_001"
    
    def test_a2a_response_json_serialization(self):
        """Test A2A response JSON serialization"""
        task = Task(
            id="task_001",
            status=TaskStatus(state=TaskState.COMPLETED),
            sessionId="session_001"
        )
        
        response = A2AMessageSendResponse(id="request_123", result=task)
        response_dict = response.model_dump(exclude_none=True)
        
        assert response_dict["id"] == "request_123"
        assert "result" in response_dict
        assert response_dict["result"]["id"] == "task_001"
        assert response_dict["result"]["status"]["state"] == "completed"
        assert "error" not in response_dict  # Should be excluded since it's None
    
    def test_a2a_json_round_trip(self):
        """Test A2A JSON round-trip serialization"""
        original_message = A2AMessage(
            messageId="msg_001",
            taskId="task_001",
            contextId="session_001",
            parts=[A2AMessagePart(kind="text", text="Test message")]
        )
        
        # Serialize to JSON string
        json_str = original_message.model_dump_json()
        
        # Parse back from JSON
        parsed_dict = json.loads(json_str)
        reconstructed_message = A2AMessage(**parsed_dict)
        
        # Should be identical
        assert reconstructed_message.messageId == original_message.messageId
        assert reconstructed_message.taskId == original_message.taskId
        assert reconstructed_message.contextId == original_message.contextId
        assert len(reconstructed_message.parts) == len(original_message.parts)
        assert reconstructed_message.parts[0].text == original_message.parts[0].text