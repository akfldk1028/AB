"""
Frontend Agent - A2A Protocol Implementation with Claude CLI
"""
import os
import sys
import asyncio
import subprocess
from typing import Any, AsyncIterable, Dict, Literal, List, Optional, Union, Final, TYPE_CHECKING
from pathlib import Path

try:
    from typing import TypeAlias
except ImportError:
    from typing_extensions import TypeAlias

# Add parent directories to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from langchain_core.messages import AIMessage, ToolMessage
from pydantic import BaseModel
from langgraph.checkpoint.memory import MemorySaver

# Import shared modules
from shared.custom_types import (
    Task, TaskStatus, TaskState, Message, TextPart, Artifact
)

memory = MemorySaver()

# Type aliases for better maintainability
AgentResponse: TypeAlias = Dict[str, Any]
Query: TypeAlias = str
SessionId: TypeAlias = str
CommandList: TypeAlias = List[str]
ProcessOutput: TypeAlias = tuple[Optional[bytes], Optional[bytes]]


class ResponseFormat(BaseModel):
    """Response format for agent responses"""
    status: Literal["input_required", "completed", "error"] = "input_required"
    message: str


class FrontendCLIAgent:
    """Frontend Agent that uses Claude CLI subprocess for responses"""
    
    SYSTEM_INSTRUCTION: Final[str] = (
        "You are a Frontend Development expert specializing in React, Vue.js, Angular, "
        "and modern web technologies. You help with UI/UX implementation, component development, "
        "state management, and responsive design."
    )
    
    SUPPORTED_CONTENT_TYPES: Final[List[str]] = ["text", "text/plain"]
    
    def __init__(self) -> None:
        self.claude_context_path: Path = Path(__file__).parent / "CLAUDE.md"
        
    async def invoke_claude_cli(self, query: Query, session_id: SessionId) -> AgentResponse:
        """
        Invoke Claude CLI as a subprocess and get response
        """
        try:
            # Build Claude CLI command (using mock for testing)
            mock_claude_path = Path(__file__).parent.parent.parent.parent / "mock_claude.py"
            cmd: CommandList = [
                "python", str(mock_claude_path),
                "--context", str(self.claude_context_path),
                "--system", self.SYSTEM_INSTRUCTION,
                query
            ]
            
            # Run Claude CLI subprocess
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=False
            )
            
            # Wait for completion with timeout
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=60.0
            )
            output: ProcessOutput = (stdout, stderr)
            
            # Decode output
            response_text: str = stdout.decode('utf-8', errors='replace') if stdout else ""
            error_text: str = stderr.decode('utf-8', errors='replace') if stderr else ""
            
            if process.returncode != 0:
                return {
                    "is_task_complete": False,
                    "require_user_input": True,
                    "content": f"Error from Claude CLI: {error_text or 'Unknown error'}"
                }
            
            # Parse response - Claude CLI returns plain text
            return {
                "is_task_complete": True,
                "require_user_input": False,
                "content": response_text.strip()
            }
            
        except asyncio.TimeoutError:
            return {
                "is_task_complete": False,
                "require_user_input": True,
                "content": "Claude CLI request timed out after 60 seconds"
            }
        except FileNotFoundError:
            return {
                "is_task_complete": False,
                "require_user_input": True,
                "content": "Claude CLI not found. Please ensure 'claude' is installed and in PATH"
            }
        except Exception as e:
            return {
                "is_task_complete": False,
                "require_user_input": True,
                "content": f"Error invoking Claude CLI: {str(e)}"
            }
    
    async def invoke_async(self, query: Query, session_id: SessionId) -> AgentResponse:
        """
        Async method to invoke agent
        """
        print(f"[Frontend Agent] Received query: {query[:100]}...")
        result = await self.invoke_claude_cli(query, session_id)
        print(f"[Frontend Agent] Response status: task_complete={result.get('is_task_complete')}")
        return result
    
    async def stream(self, query: Query, session_id: SessionId) -> AsyncIterable[AgentResponse]:
        """
        Stream responses (calls invoke_async and yields result)
        """
        # For Claude CLI, we get the full response at once
        yield {
            "is_task_complete": False,
            "require_user_input": False,
            "content": "Processing frontend request with Claude CLI..."
        }
        
        result = await self.invoke_async(query, session_id)
        yield result
    
    def get_agent_response(self, result: AgentResponse) -> AgentResponse:
        """
        Format the agent response
        """
        return result


# For testing standalone
if __name__ == "__main__":
    async def test() -> None:
        agent = FrontendCLIAgent()
        response = await agent.invoke_async(
            "Create a simple React button component",
            "test_session_123"
        )
        print("Response:", response)
    
    asyncio.run(test())