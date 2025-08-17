"""
Pytest configuration and fixtures for Claude CLI Multi-Agent A2A System tests
"""
import asyncio
import pytest
import pytest_asyncio
from pathlib import Path
import sys
from unittest.mock import AsyncMock, Mock
from typing import AsyncGenerator, Generator

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from shared.custom_types import (
    TaskSendParams, Message, TextPart, Task, TaskStatus, TaskState,
    A2AMessageSendRequest, A2AMessage, A2AMessagePart
)
from shared.push_notification_auth import PushNotificationSenderAuth


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_push_notification_auth() -> Mock:
    """Mock push notification auth for testing"""
    mock_auth = Mock(spec=PushNotificationSenderAuth)
    mock_auth.verify_push_notification_url = AsyncMock(return_value=True)
    mock_auth.send_push_notification = AsyncMock()
    return mock_auth


@pytest.fixture
def sample_task_params() -> TaskSendParams:
    """Sample task parameters for testing"""
    return TaskSendParams(
        id="test_task_123",
        sessionId="test_session_456",
        message=Message(
            role="user",
            parts=[TextPart(text="Test query for agent")]
        )
    )


@pytest.fixture
def sample_a2a_message_request() -> A2AMessageSendRequest:
    """Sample A2A message request for testing"""
    return A2AMessageSendRequest(
        id="test_a2a_request_123",
        method="message/send",
        params={
            "message": A2AMessage(
                messageId="msg_test_001",
                taskId="task_test_001",
                contextId="session_test_001",
                parts=[A2AMessagePart(kind="text", text="Test A2A message")]
            )
        }
    )


@pytest.fixture
def mock_claude_cli_response() -> dict:
    """Mock Claude CLI response"""
    return {
        "is_task_complete": True,
        "require_user_input": False,
        "content": "Mock response from Claude CLI"
    }


@pytest.fixture
def mock_process() -> Mock:
    """Mock subprocess for Claude CLI calls"""
    mock_process = Mock()
    mock_process.returncode = 0
    mock_process.communicate = AsyncMock(return_value=(
        b"Mock Claude CLI response",
        b""
    ))
    return mock_process


@pytest_asyncio.fixture
async def frontend_agent():
    """Frontend agent instance for testing"""
    from agents.claude_cli.frontend.agent import FrontendCLIAgent
    return FrontendCLIAgent()


@pytest_asyncio.fixture
async def backend_agent():
    """Backend agent instance for testing"""
    from agents.claude_cli.backend.agent import BackendCLIAgent
    return BackendCLIAgent()


@pytest_asyncio.fixture
async def unity_agent():
    """Unity agent instance for testing"""
    from agents.claude_cli.unity.agent import UnityCLIAgent
    return UnityCLIAgent()


@pytest_asyncio.fixture
async def frontend_task_manager(frontend_agent, mock_push_notification_auth):
    """Frontend task manager for testing"""
    from agents.claude_cli.base_cli_task_manager import CLIAgentTaskManager
    return CLIAgentTaskManager(frontend_agent, mock_push_notification_auth)


@pytest_asyncio.fixture
async def backend_task_manager(backend_agent, mock_push_notification_auth):
    """Backend task manager for testing"""
    from agents.claude_cli.base_cli_task_manager import CLIAgentTaskManager
    return CLIAgentTaskManager(backend_agent, mock_push_notification_auth)


@pytest_asyncio.fixture
async def unity_task_manager(unity_agent, mock_push_notification_auth):
    """Unity task manager for testing"""
    from agents.claude_cli.base_cli_task_manager import CLIAgentTaskManager
    return CLIAgentTaskManager(unity_agent, mock_push_notification_auth)


@pytest.fixture
def temp_claude_context(tmp_path) -> Path:
    """Create temporary CLAUDE.md context file"""
    claude_md = tmp_path / "CLAUDE.md"
    claude_md.write_text("""
# Test Agent Configuration
This is a test configuration for Claude CLI agent.
""")
    return claude_md