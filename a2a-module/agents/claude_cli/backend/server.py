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


def create_backend_agent_card() -> AgentCard:
    """Create the agent card for Backend Agent"""
    return AgentCard(
        url="http://localhost:8021",
        name="Backend Development Agent",
        description="Expert in APIs, databases, server architecture, and system design. Creates projects in separate project folders.",
        version="1.0.0",
        capabilities=AgentCapabilities(
            streaming=True,
            pushNotifications=True,
            stateTransitionHistory=True
        ),
        skills=[
            AgentSkill(
                id="api_design",
                name="API Design & Development",
                description="Design and implement REST and GraphQL APIs",
                tags=["api", "rest", "graphql", "endpoints"],
                examples=["Create REST API for user management", "Design GraphQL schema for e-commerce"]
            ),
            AgentSkill(
                id="database_design",
                name="Database Design & Optimization",
                description="Design database schemas and optimize queries",
                tags=["database", "sql", "nosql", "optimization"],
                examples=["Design PostgreSQL schema for blog system", "Optimize MongoDB queries"]
            ),
            AgentSkill(
                id="authentication",
                name="Authentication & Security",
                description="Implement secure authentication and authorization",
                tags=["auth", "security", "jwt", "oauth"],
                examples=["Implement JWT authentication", "Design OAuth2 flow"]
            )
        ]
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
    
    # Create agent card
    agent_card = create_backend_agent_card()
    
    # Create and start server
    server = A2AServer(
        host="0.0.0.0",
        port=8021,
        endpoint="/",
        agent_card=agent_card,
        task_manager=task_manager
    )
    
    print("[Backend Agent] Starting A2A server on port 8021...")
    print("[Backend Agent] Agent card available at: http://localhost:8021/.well-known/agent.json")
    print("[Backend Agent] Ready to receive backend development tasks via A2A protocol")
    print("[Backend Agent] Using Claude CLI for response generation")
    
    server.start()


if __name__ == "__main__":
    main()