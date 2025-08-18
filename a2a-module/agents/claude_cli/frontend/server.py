"""
Frontend Agent A2A Server  
Runs on port 8010
"""
import os
import sys
import json
import time
from datetime import datetime
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
from agent import FrontendCLIAgent


def create_frontend_agent_card() -> AgentCard:
    """Create the agent card for Frontend Agent"""
    return AgentCard(
        url="http://localhost:8010",
        name="Frontend Development Agent",
        description="Expert in React, Vue.js, Angular, and modern frontend technologies. Creates projects in separate project folders.",
        version="1.0.0",
        capabilities=AgentCapabilities(
            streaming=True,
            pushNotifications=True,
            stateTransitionHistory=True
        ),
        skills=[
            AgentSkill(
                id="react_development",
                name="React Development",
                description="Create React components, hooks, and applications",
                tags=["react", "javascript", "typescript", "jsx"],
                examples=["Create a login form component", "Implement React hooks for state management"]
            ),
            AgentSkill(
                id="vue_development", 
                name="Vue.js Development",
                description="Build Vue.js components and applications",
                tags=["vue", "vuejs", "javascript", "typescript"],
                examples=["Create Vue component with composition API", "Implement Vuex store"]
            ),
            AgentSkill(
                id="ui_components",
                name="UI Component Development",
                description="Build reusable UI components and design systems",
                tags=["components", "ui", "design-system", "accessibility"],
                examples=["Create reusable button component", "Build accessible modal dialog"]
            )
        ]
    )


def main():
    """Start the Frontend Agent A2A server"""
    print("[Frontend Agent] Initializing Claude CLI-based Frontend Agent...")
    print("[Frontend Agent] Projects will be created in: projects/[PROJECT_NAME]/frontend/")
    
    # Create agent instance
    agent = FrontendCLIAgent()
    
    # Create task manager
    notification_auth = PushNotificationSenderAuth()
    task_manager = CLIAgentTaskManager(agent, notification_auth)
    
    # Create agent card
    agent_card = create_frontend_agent_card()
    
    # Create and start server
    server = A2AServer(
        host="0.0.0.0",
        port=8010,
        endpoint="/",
        agent_card=agent_card,
        task_manager=task_manager
    )
    
    print("[Frontend Agent] Starting A2A server on port 8010...")
    print("[Frontend Agent] Agent card available at: http://localhost:8110/.well-known/agent.json")
    print("[Frontend Agent] Ready to receive frontend development tasks via A2A protocol")
    print("[Frontend Agent] Using Claude CLI for response generation")
    
    server.start()


if __name__ == "__main__":
    main()