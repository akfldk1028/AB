"""
Backend Agent A2A Server
Runs on port 8021
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
from agent import BackendCLIAgent


def load_backend_agent_card() -> AgentCard:
    """Load the agent card from JSON file"""
    import json
    
    agent_card_path = Path(__file__).parent.parent.parent.parent / "agent_cards" / "backend_agent.json"
    
    try:
        with open(agent_card_path, 'r', encoding='utf-8') as f:
            card_data = json.load(f)
        
        # Convert JSON to AgentCard object
        capabilities = AgentCapabilities(**card_data["capabilities"])
        
        skills = []
        for skill_data in card_data.get("skills", []):
            skill = AgentSkill(**skill_data)
            skills.append(skill)
        
        return AgentCard(
            url=card_data["url"],
            name=card_data["name"],
            description=card_data["description"],
            version=card_data["version"],
            capabilities=capabilities,
            skills=skills,
            defaultInputModes=card_data.get("defaultInputModes", ["text"]),
            defaultOutputModes=card_data.get("defaultOutputModes", ["text"])
        )
    
    except Exception as e:
        print(f"[Backend Agent] Warning: Could not load agent card from JSON: {e}")
        # Fallback to hardcoded card
        return AgentCard(
            url="http://localhost:8020",
            name="Backend Development Agent",
            description="Expert in APIs, databases, server architecture, and system design.",
            version="1.0.0",
            capabilities=AgentCapabilities(
                streaming=True,
                pushNotifications=True,
                stateTransitionHistory=True
            ),
            skills=[]
        )


def main():
    """Start the Backend Agent A2A server"""
    print("[Backend Agent] Initializing Claude CLI-based Backend Agent...")
    print("[Backend Agent] Projects will be created in: projects/[PROJECT_NAME]/backend/")
    
    # Create agent instance
    agent = BackendCLIAgent()
    
    # Create task manager
    notification_auth = PushNotificationSenderAuth()
    task_manager = CLIAgentTaskManager(agent, notification_auth)
    
    # Load agent card from JSON
    agent_card = load_backend_agent_card()
    
    # Create and start server
    server = A2AServer(
        host="0.0.0.0",
        port=8020,
        endpoint="/",
        agent_card=agent_card,
        task_manager=task_manager
    )
    
    print("[Backend Agent] Starting A2A server on port 8020...")
    print("[Backend Agent] Agent card available at: http://localhost:8020/.well-known/agent.json")
    print("[Backend Agent] Ready to receive backend development tasks via A2A protocol")
    print("[Backend Agent] Using Claude CLI for response generation")
    
    server.start()


if __name__ == "__main__":
    main()