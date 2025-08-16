import asyncio
from typing import Any, AsyncIterable, Dict, Literal
import json
import requests

from langchain_core.messages import AIMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel

memory = MemorySaver()

def notify_websocket(node, status, message=""):
    """WebSocket으로 노드 상태 알림"""
    try:
        # WebSocket 서버의 HTTP 엔드포인트로 POST 요청
        data = {
            "type": "node_update",
            "node": node,
            "status": status,
            "message": message
        }
        requests.post("http://localhost:8096/notify", json=data, timeout=0.1)
    except:
        pass  # 에러 무시 (WebSocket 서버가 없을 때)

def _create_weather_tools() -> list:
    """
    Create synchronous weather tools.
    """
    from langchain_core.tools import tool
    
    @tool
    def get_weather(city: str = "Seoul", country: str = "KR") -> dict:
        """Get weather information for a city.
        
        Args:
            city: City name (e.g. "Seoul", "New York", "London").
            country: Country code (e.g. "KR", "US", "UK"). Optional.
            
        Returns:
            Dictionary with weather information.
        """
        print(f"DEBUG: Weather tool called for {city}, {country}")
        
        # Demo weather data for various cities
        weather_data = {
            "SEOUL": {
                "temperature": "22°C",
                "condition": "Partly Cloudy",
                "humidity": "65%",
                "wind": "10 km/h",
                "description": "Pleasant weather with some clouds"
            },
            "NEW YORK": {
                "temperature": "18°C", 
                "condition": "Sunny",
                "humidity": "45%",
                "wind": "8 km/h",
                "description": "Clear and sunny day"
            },
            "LONDON": {
                "temperature": "15°C",
                "condition": "Rainy",
                "humidity": "80%", 
                "wind": "12 km/h",
                "description": "Light rain expected throughout the day"
            },
            "TOKYO": {
                "temperature": "25°C",
                "condition": "Cloudy",
                "humidity": "70%",
                "wind": "6 km/h", 
                "description": "Overcast with mild temperatures"
            },
            "PARIS": {
                "temperature": "19°C",
                "condition": "Sunny",
                "humidity": "50%",
                "wind": "9 km/h",
                "description": "Beautiful sunny weather"
            },
            "SYDNEY": {
                "temperature": "28°C",
                "condition": "Partly Cloudy",
                "humidity": "60%",
                "wind": "15 km/h",
                "description": "Warm with scattered clouds"
            }
        }
        
        # Normalize city name
        city_key = city.upper()
        
        # Get weather data or provide default
        if city_key in weather_data:
            weather = weather_data[city_key]
        else:
            # Default weather for unknown cities
            weather = {
                "temperature": "20°C",
                "condition": "Mostly Cloudy", 
                "humidity": "60%",
                "wind": "10 km/h",
                "description": f"Weather information for {city} - moderate conditions"
            }
        
        print(f"DEBUG: Weather tool returning data for {city}")
        
        return {
            "success": True,
            "city": city,
            "country": country,
            "current_weather": weather,
            "timestamp": "2024-08-16T15:00:00Z",
            "provider": "Demo Weather Service"
        }
    
    return [get_weather]


class ResponseFormat(BaseModel):
    """Respond to the user in this format."""

    status: Literal["input_required", "completed", "error"] = "input_required"
    message: str


class WeatherAgent:
    SYSTEM_INSTRUCTION = (
        "You are a weather information assistant. You have access to a get_weather tool. "
        "For any weather-related query, you MUST call get_weather first before responding. "
        "Example: User says 'What's the weather in Seoul?' -> IMMEDIATELY call get_weather(city='Seoul'). "
        "Always use the tool first, then format a proper response with the weather information."
    )

    def __init__(self):
        # Use synchronous tool wrappers
        self.tools = _create_weather_tools()
        
        print(f"DEBUG: Loaded {len(self.tools)} weather tools")
        for tool in self.tools:
            print(f"DEBUG: Tool name: {tool.name if hasattr(tool, 'name') else 'no name'}")
            print(f"DEBUG: Tool description: {tool.description if hasattr(tool, 'description') else 'no description'}")

        self.model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        
        self.graph = create_react_agent(
            self.model,
            tools=self.tools,
            checkpointer=memory,
            prompt=self.SYSTEM_INSTRUCTION,
        )

    async def invoke_async(self, query, sessionId) -> dict:
        """Async version of invoke method"""
        print(f"DEBUG: WEATHER ASYNC INVOKE method called with query: {query}")
        
        result_items = []
        async for item in self.stream(query, sessionId):
            result_items.append(item)
            if item.get("is_task_complete", False):
                return item
        # Return the last item if no completion found
        return result_items[-1] if result_items else {
            "is_task_complete": False,
            "require_user_input": True,
            "content": "Unable to process weather request"
        }
    
    def invoke(self, query, sessionId) -> str:
        """Sync wrapper for backward compatibility"""
        print(f"DEBUG: WEATHER SYNC INVOKE wrapper called with query: {query}")
        import asyncio
        try:
            loop = asyncio.get_running_loop()
            raise RuntimeError("invoke() called from async context - use invoke_async() instead")
        except RuntimeError:
            return asyncio.run(self.invoke_async(query, sessionId))

    async def stream(self, query, sessionId) -> AsyncIterable[Dict[str, Any]]:
        inputs = {"messages": [("user", query)]}
        config = {"configurable": {"thread_id": sessionId}, "recursion_limit": 100}

        # Start notification
        notify_websocket("start", "current", f"Starting weather query: {query}")
        notify_websocket("agent", "current", "Weather agent analyzing query...")

        print(f"DEBUG: Starting weather stream for query: {query}")
        step_count = 0

        for item in self.graph.stream(inputs, config, stream_mode="values"):
            step_count += 1
            print(f"DEBUG: Weather stream step {step_count}")
            print(f"DEBUG: Item keys: {list(item.keys())}")
            
            if "messages" in item:
                messages = item["messages"]
                print(f"DEBUG: Got {len(messages)} messages")
                if messages:
                    last_message = messages[-1]
                    print(f"DEBUG: Last message type: {type(last_message)}")
                    
                    if (
                        isinstance(last_message, AIMessage)
                        and hasattr(last_message, 'tool_calls')
                        and last_message.tool_calls
                        and len(last_message.tool_calls) > 0
                    ):
                        print(f"DEBUG: Found weather tool calls: {last_message.tool_calls}")
                        notify_websocket("agent", "completed", "Weather agent decided to call tools")
                        notify_websocket("tools", "current", "Calling get_weather tool...")
                        yield {
                            "is_task_complete": False,
                            "require_user_input": False,
                            "content": "Looking up weather information...",
                        }
                    elif isinstance(last_message, ToolMessage):
                        print(f"DEBUG: Found weather tool message: {last_message}")
                        notify_websocket("tools", "completed", "Weather tool result received")
                        notify_websocket("agent", "current", "Weather agent processing results...")
                        yield {
                            "is_task_complete": False,
                            "require_user_input": False,
                            "content": "Processing weather data...",
                        }

        print(f"DEBUG: Weather stream completed after {step_count} steps")
        notify_websocket("response", "current", "Generating weather response...")
        result = self.get_agent_response(config)
        notify_websocket("response", "completed", "Weather response generated")
        notify_websocket("end", "completed", "Weather execution completed")
        yield result

    def get_agent_response(self, config):
        current_state = self.graph.get_state(config)
        print(f"DEBUG: Weather agent current state: {current_state.values.keys()}")
        
        # Check for structured_response first (if it exists)
        structured_response = current_state.values.get("structured_response")
        if structured_response and isinstance(structured_response, ResponseFormat):
            if structured_response.status == "input_required":
                return {
                    "is_task_complete": False,
                    "require_user_input": True,
                    "content": structured_response.message,
                }
            elif structured_response.status == "error":
                return {
                    "is_task_complete": False,
                    "require_user_input": True,
                    "content": structured_response.message,
                }
            elif structured_response.status == "completed":
                return {
                    "is_task_complete": True,
                    "require_user_input": False,
                    "content": structured_response.message,
                }
        
        # If no structured_response, check the messages for final AI response
        messages = current_state.values.get("messages", [])
        if messages:
            # Get the last AI message
            last_ai_message = None
            for msg in reversed(messages):
                if hasattr(msg, 'content') and hasattr(msg, '__class__') and 'AIMessage' in str(msg.__class__):
                    last_ai_message = msg
                    break
            
            if last_ai_message and last_ai_message.content:
                print(f"DEBUG: Found final weather AI message: {last_ai_message.content[:200]}...")
                return {
                    "is_task_complete": True,
                    "require_user_input": False,
                    "content": last_ai_message.content,
                }

        print("DEBUG: No weather response found, returning default error")
        return {
            "is_task_complete": False,
            "require_user_input": True,
            "content": "Unable to get weather information at the moment. Please try again.",
        }

    SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]