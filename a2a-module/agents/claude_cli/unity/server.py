"""
Unity Agent A2A Server
Runs on port 8012
"""
import os
import sys
from pathlib import Path

# Add parent directories to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from shared.server import A2AServer
from shared.custom_types import AgentCard, AgentCapabilities, AgentSkill
from shared.push_notification_auth import PushNotificationSenderAuth

# Import the CLI task manager
sys.path.append(str(Path(__file__).parent.parent))
from base_cli_task_manager import CLIAgentTaskManager

# Import agent from current directory
sys.path.append(str(Path(__file__).parent))
from agent import UnityCLIAgent


def create_unity_agent_card() -> AgentCard:
    """Create the agent card for Unity Agent"""
    return AgentCard(
        url="http://localhost:8012",
        name="Unity Game Development Agent",
        description="Expert in Unity Engine, C# game programming, graphics, and optimization. Handles game mechanics, shaders, multiplayer, VR/AR, and performance.",
        version="1.0.0",
        capabilities=AgentCapabilities(
            streaming=True,
            pushNotifications=True,
            stateTransitionHistory=True
        ),
        skills=[
            AgentSkill(
                id="game_mechanics",
                name="Game Mechanics Development",
                description="Implement core game systems and mechanics",
                tags=["unity", "csharp", "gameplay", "mechanics"],
                examples=["Create character controller", "Implement inventory system", "Build combat system"]
            ),
            AgentSkill(
                id="graphics_shaders",
                name="Graphics & Shader Development",
                description="Create shaders and visual effects in Unity",
                tags=["shaders", "hlsl", "graphics", "vfx"],
                examples=["Create water shader", "Implement post-processing effects", "Build particle systems"]
            ),
            AgentSkill(
                id="multiplayer_networking",
                name="Multiplayer & Networking",
                description="Implement multiplayer game systems",
                tags=["multiplayer", "networking", "mirror", "netcode"],
                examples=["Setup multiplayer lobby", "Implement client-server sync", "Build matchmaking"]
            ),
            AgentSkill(
                id="performance_optimization",
                name="Performance Optimization",
                description="Optimize Unity games for better performance",
                tags=["optimization", "performance", "mobile", "profiling"],
                examples=["Optimize for mobile devices", "Reduce draw calls", "Memory management"]
            )
        ]
    )


def main():
    """Start the Unity Agent A2A server"""
    print("[Unity Agent] Initializing Claude CLI-based Unity Agent...")
    
    # Create agent instance
    agent = UnityCLIAgent()
    
    # Create task manager
    notification_auth = PushNotificationSenderAuth()
    task_manager = CLIAgentTaskManager(agent, notification_auth)
    
    # Create agent card
    agent_card = create_unity_agent_card()
    
    # Create and start server
    server = A2AServer(
        host="0.0.0.0",
        port=8012,
        endpoint="/",
        agent_card=agent_card,
        task_manager=task_manager
    )
    
    print("[Unity Agent] Starting A2A server on port 8012...")
    print("[Unity Agent] Agent card available at: http://localhost:8012/.well-known/agent.json")
    print("[Unity Agent] Ready to receive Unity development tasks via A2A protocol")
    print("[Unity Agent] Using Claude CLI for response generation")
    
    server.start()


if __name__ == "__main__":
    main()