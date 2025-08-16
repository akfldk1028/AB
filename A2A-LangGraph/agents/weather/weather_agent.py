import logging
import os

import click
from dotenv import load_dotenv

# Import shared files from shared directory
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from custom_types import AgentCapabilities, AgentCard, AgentSkill, MissingAPIKeyError
from push_notification_auth import PushNotificationSenderAuth
from server import A2AServer
from task_manager import AgentTaskManager
from weather_agent_core import WeatherAgent

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@click.command()
@click.option("--host", "host", default="localhost")
@click.option("--port", "port", default=8001)
def main(host, port):
    """Starts the Weather Agent server."""
    try:
        if not os.getenv("OPENAI_API_KEY"):
            raise MissingAPIKeyError("OPENAI_API_KEY environment variable not set.")

        capabilities = AgentCapabilities(streaming=True, pushNotifications=False)
        skill = AgentSkill(
            id="get_weather",
            name="Weather Information Tool",
            description="Provides weather information for cities around the world",
            tags=["weather", "forecast", "temperature"],
            examples=["What's the weather in Seoul?", "How's the weather in New York?"],
        )
        agent_card = AgentCard(
            name="Weather Agent",
            description="Provides weather information for cities worldwide",
            url=f"http://{host}:{port}/",
            version="1.0.0",
            defaultInputModes=WeatherAgent.SUPPORTED_CONTENT_TYPES,
            defaultOutputModes=WeatherAgent.SUPPORTED_CONTENT_TYPES,
            capabilities=capabilities,
            skills=[skill],
        )

        notification_sender_auth = PushNotificationSenderAuth()
        notification_sender_auth.generate_jwk()
        server = A2AServer(
            agent_card=agent_card,
            task_manager=AgentTaskManager(
                agent=WeatherAgent(), notification_sender_auth=notification_sender_auth
            ),
            host=host,
            port=port,
        )

        server.app.add_route(
            "/.well-known/jwks.json",
            notification_sender_auth.handle_jwks_endpoint,
            methods=["GET"],
        )

        logger.info(f"Starting Weather Agent server on {host}:{port}")
        server.start()
    except MissingAPIKeyError as e:
        logger.error(f"Error: {e}")
        exit(1)
    except Exception as e:
        logger.error(f"An error occurred during server startup: {e}")
        exit(1)


if __name__ == "__main__":
    main()