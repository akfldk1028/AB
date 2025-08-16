from host_agent import HostAgent
import httpx


# Connect to our running agents
http_client = httpx.AsyncClient()
root_agent = HostAgent(
    ['http://localhost:9999', 'http://localhost:10002'], 
    http_client
).create_agent()
