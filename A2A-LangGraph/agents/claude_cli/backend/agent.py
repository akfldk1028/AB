"""
Backend Agent - A2A Protocol Implementation with Claude CLI
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
from shared.mcp.client import MCPClient
from shared.mcp.enhancer import create_smart_enhancer

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


class BackendCLIAgent:
    """Backend Agent that uses Claude CLI subprocess for responses"""
    
    SYSTEM_INSTRUCTION: Final[str] = (
        "You are a Backend Development expert specializing in APIs, databases, "
        "server architecture, and system design. You help with REST/GraphQL APIs, "
        "microservices, database design, authentication, and scalability."
    )
    
    SUPPORTED_CONTENT_TYPES: Final[List[str]] = ["text", "text/plain"]
    
    def __init__(self) -> None:
        self.claude_context_path: Path = Path(__file__).parent / "CLAUDE.md"
        # Use port 8001 for A2A-LangGraph (8000 is used by a2a-module)
        from shared.mcp.client import MCPClient
        mcp_client = MCPClient(proxy_port=8001)
        from shared.mcp.enhancer import SmartMCPEnhancer
        self.smart_enhancer = SmartMCPEnhancer("backend development")
        self.smart_enhancer.mcp_client = mcp_client
        
    def enhance_query_with_mcp(self, query: Query) -> str:
        """Intelligently enhance query using AI-driven MCP analysis"""
        # Temporarily disable MCP for testing
        print(f"[Backend Agent] MCP temporarily disabled, using original query")
        return query
        
    async def invoke_claude_cli(self, query: Query, session_id: SessionId) -> AgentResponse:
        """
        Invoke Claude CLI as a subprocess and get response
        """
        try:
            # Enhance query with MCP tools
            enhanced_query = self.enhance_query_with_mcp(query)
            print(f"[Backend Agent] Enhanced query length: {len(enhanced_query)} chars")
            # Build Claude CLI command - using claude.cmd for Windows compatibility and stdin
            cmd: CommandList = [
                "claude.cmd",
                "--print",  # Non-interactive mode
                "--permission-mode", "bypassPermissions",  # Bypass permissions for A2A
                "--add-dir", str(self.claude_context_path.parent),  # Add agent directory for CLAUDE.md
                "--append-system-prompt", self.SYSTEM_INSTRUCTION
            ]
            
            # Run Claude CLI subprocess with stdin
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=False
            )
            
            # Send enhanced query via stdin and wait for completion with timeout
            query_bytes = enhanced_query.encode('utf-8')
            stdout, stderr = await asyncio.wait_for(
                process.communicate(input=query_bytes),
                timeout=600.0  # 10 minutes for complex AI responses and A2A communication
            )
            
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
                "content": "Claude CLI request timed out after 10 minutes"
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
        print(f"[Backend Agent] Received query: {query[:100]}...")
        result = await self.invoke_claude_cli(query, session_id)
        print(f"[Backend Agent] Response status: task_complete={result.get('is_task_complete')}")
        return result
    
    async def stream(self, query: Query, session_id: SessionId) -> AsyncIterable[AgentResponse]:
        """
        Stream responses (calls invoke_async and yields result)
        """
        # For Claude CLI, we get the full response at once
        yield {
            "is_task_complete": False,
            "require_user_input": False,
            "content": "Processing backend request with Claude CLI..."
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
        agent = BackendCLIAgent()
        response = await agent.invoke_async(
            "Design a REST API for user authentication",
            "test_session_123"
        )
        print("Response:", response)
    
    asyncio.run(test())