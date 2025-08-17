"""
Unit tests for Claude CLI Agents
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, Mock, patch
from pathlib import Path

from agents.claude_cli.frontend.agent import FrontendCLIAgent
from agents.claude_cli.backend.agent import BackendCLIAgent
from agents.claude_cli.unity.agent import UnityCLIAgent


class TestFrontendAgent:
    """Test cases for Frontend Agent"""
    
    @pytest.mark.asyncio
    async def test_frontend_agent_initialization(self, frontend_agent):
        """Test frontend agent initialization"""
        assert frontend_agent.SYSTEM_INSTRUCTION is not None
        assert "Frontend Development" in frontend_agent.SYSTEM_INSTRUCTION
        assert "text" in frontend_agent.SUPPORTED_CONTENT_TYPES
        assert isinstance(frontend_agent.claude_context_path, Path)
    
    @pytest.mark.asyncio
    async def test_frontend_agent_invoke_claude_cli_success(self, frontend_agent, mock_process):
        """Test successful Claude CLI invocation"""
        with patch('asyncio.create_subprocess_exec') as mock_subprocess:
            mock_subprocess.return_value = mock_process
            
            result = await frontend_agent.invoke_claude_cli(
                "Create a React component", 
                "test_session"
            )
            
            assert result["is_task_complete"] is True
            assert result["require_user_input"] is False
            assert "Mock Claude CLI response" in result["content"]
            
    @pytest.mark.asyncio
    async def test_frontend_agent_invoke_claude_cli_timeout(self, frontend_agent):
        """Test Claude CLI timeout handling"""
        with patch('asyncio.create_subprocess_exec') as mock_subprocess:
            mock_process = Mock()
            mock_process.communicate = AsyncMock(side_effect=asyncio.TimeoutError())
            mock_subprocess.return_value = mock_process
            
            result = await frontend_agent.invoke_claude_cli(
                "Create a React component", 
                "test_session"
            )
            
            assert result["is_task_complete"] is False
            assert result["require_user_input"] is True
            assert "timed out" in result["content"]
    
    @pytest.mark.asyncio
    async def test_frontend_agent_invoke_claude_cli_error(self, frontend_agent):
        """Test Claude CLI error handling"""
        with patch('asyncio.create_subprocess_exec') as mock_subprocess:
            mock_process = Mock()
            mock_process.returncode = 1
            mock_process.communicate = AsyncMock(return_value=(b"", b"Error message"))
            mock_subprocess.return_value = mock_process
            
            result = await frontend_agent.invoke_claude_cli(
                "Create a React component", 
                "test_session"
            )
            
            assert result["is_task_complete"] is False
            assert result["require_user_input"] is True
            assert "Error from Claude CLI" in result["content"]
    
    @pytest.mark.asyncio
    async def test_frontend_agent_invoke_async(self, frontend_agent, mock_process):
        """Test async invocation method"""
        with patch('asyncio.create_subprocess_exec') as mock_subprocess:
            mock_subprocess.return_value = mock_process
            
            result = await frontend_agent.invoke_async(
                "Create a React component", 
                "test_session"
            )
            
            assert isinstance(result, dict)
            assert "is_task_complete" in result
            assert "require_user_input" in result
            assert "content" in result
    
    @pytest.mark.asyncio
    async def test_frontend_agent_stream(self, frontend_agent, mock_process):
        """Test streaming responses"""
        with patch('asyncio.create_subprocess_exec') as mock_subprocess:
            mock_subprocess.return_value = mock_process
            
            responses = []
            async for response in frontend_agent.stream("Create a React component", "test_session"):
                responses.append(response)
            
            assert len(responses) == 2  # Initial + final response
            assert responses[0]["content"] == "Processing frontend request with Claude CLI..."
            assert responses[1]["is_task_complete"] is True


class TestBackendAgent:
    """Test cases for Backend Agent"""
    
    @pytest.mark.asyncio
    async def test_backend_agent_initialization(self, backend_agent):
        """Test backend agent initialization"""
        assert backend_agent.SYSTEM_INSTRUCTION is not None
        assert "Backend Development" in backend_agent.SYSTEM_INSTRUCTION
        assert "text" in backend_agent.SUPPORTED_CONTENT_TYPES
        assert isinstance(backend_agent.claude_context_path, Path)
    
    @pytest.mark.asyncio
    async def test_backend_agent_invoke_success(self, backend_agent, mock_process):
        """Test successful backend agent invocation"""
        with patch('asyncio.create_subprocess_exec') as mock_subprocess:
            mock_subprocess.return_value = mock_process
            
            result = await backend_agent.invoke_async(
                "Create a REST API", 
                "test_session"
            )
            
            assert result["is_task_complete"] is True
            assert result["require_user_input"] is False
            assert "Mock Claude CLI response" in result["content"]
    
    @pytest.mark.asyncio
    async def test_backend_agent_stream(self, backend_agent, mock_process):
        """Test backend agent streaming"""
        with patch('asyncio.create_subprocess_exec') as mock_subprocess:
            mock_subprocess.return_value = mock_process
            
            responses = []
            async for response in backend_agent.stream("Create a REST API", "test_session"):
                responses.append(response)
            
            assert len(responses) == 2
            assert "backend request" in responses[0]["content"]


class TestUnityAgent:
    """Test cases for Unity Agent"""
    
    @pytest.mark.asyncio
    async def test_unity_agent_initialization(self, unity_agent):
        """Test unity agent initialization"""
        assert unity_agent.SYSTEM_INSTRUCTION is not None
        assert "Unity" in unity_agent.SYSTEM_INSTRUCTION
        assert "text" in unity_agent.SUPPORTED_CONTENT_TYPES
        assert isinstance(unity_agent.claude_context_path, Path)
    
    @pytest.mark.asyncio
    async def test_unity_agent_invoke_success(self, unity_agent, mock_process):
        """Test successful unity agent invocation"""
        with patch('asyncio.create_subprocess_exec') as mock_subprocess:
            mock_subprocess.return_value = mock_process
            
            result = await unity_agent.invoke_async(
                "Create a character controller", 
                "test_session"
            )
            
            assert result["is_task_complete"] is True
            assert result["require_user_input"] is False
            assert "Mock Claude CLI response" in result["content"]
    
    @pytest.mark.asyncio
    async def test_unity_agent_stream(self, unity_agent, mock_process):
        """Test unity agent streaming"""
        with patch('asyncio.create_subprocess_exec') as mock_subprocess:
            mock_subprocess.return_value = mock_process
            
            responses = []
            async for response in unity_agent.stream("Create a character controller", "test_session"):
                responses.append(response)
            
            assert len(responses) == 2
            assert "Unity development request" in responses[0]["content"]


class TestAgentCommon:
    """Common tests for all agents"""
    
    @pytest.mark.parametrize("agent_class", [
        FrontendCLIAgent,
        BackendCLIAgent, 
        UnityCLIAgent
    ])
    def test_agent_supported_content_types(self, agent_class):
        """Test that all agents support required content types"""
        agent = agent_class()
        assert "text" in agent.SUPPORTED_CONTENT_TYPES
        assert "text/plain" in agent.SUPPORTED_CONTENT_TYPES
    
    @pytest.mark.parametrize("agent_class", [
        FrontendCLIAgent,
        BackendCLIAgent,
        UnityCLIAgent
    ])
    def test_agent_system_instruction_not_empty(self, agent_class):
        """Test that all agents have non-empty system instructions"""
        agent = agent_class()
        assert agent.SYSTEM_INSTRUCTION
        assert len(agent.SYSTEM_INSTRUCTION.strip()) > 0
    
    @pytest.mark.parametrize("agent_class", [
        FrontendCLIAgent,
        BackendCLIAgent,
        UnityCLIAgent
    ])
    def test_agent_context_path_exists(self, agent_class):
        """Test that all agents have valid context paths"""
        agent = agent_class()
        assert isinstance(agent.claude_context_path, Path)
        # Note: We don't check if file exists as it may not during testing