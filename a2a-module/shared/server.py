import json
import logging
from typing import Any, AsyncIterable, Union

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sse_starlette.sse import EventSourceResponse

from .abc_task_manager import TaskManager
from .custom_types import (
    A2ARequest,
    AgentCard,
    CancelTaskRequest,
    GetTaskPushNotificationRequest,
    GetTaskRequest,
    InternalError,
    InvalidRequestError,
    JSONParseError,
    JSONRPCResponse,
    SendTaskRequest,
    SendTaskStreamingRequest,
    SetTaskPushNotificationRequest,
    TaskResubscriptionRequest,
    A2AMessageSendRequest,
    A2AMessageSendResponse,
    A2AMessage,
    A2APart,
)

logger = logging.getLogger(__name__)


class A2AServer:
    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 5000,
        endpoint: str = "/",
        agent_card: AgentCard = None,
        task_manager: TaskManager = None,
    ):
        self.host = host
        self.port = port
        self.endpoint = endpoint
        self.task_manager = task_manager
        self.agent_card = agent_card

        # Erstelle eine FastAPI-App für automatische Dokumentation (/docs, /redoc, etc.)
        self.app = FastAPI(
            title="A2A Server", description="A2A Protocol JSON-RPC API", version="1.0.0"
        )
        # JSON-RPC-Endpunkt (POST) - automatische Response Modell Generierung deaktiviert
        self.app.add_api_route(
            self.endpoint, self._process_request, methods=["POST"], response_model=None
        )
        # AgentCard-Endpunkt unter .well-known
        self.app.add_api_route(
            "/.well-known/agent.json",
            self._get_agent_card,
            methods=["GET"],
            response_model=None,
        )
        # A2A Inspector compatibility - also serve at agent-card.json
        self.app.add_api_route(
            "/.well-known/agent-card.json",
            self._get_agent_card,
            methods=["GET"],
            response_model=None,
        )

    def start(self):
        if self.agent_card is None:
            raise ValueError("agent_card is not defined")
        if self.task_manager is None:
            raise ValueError("task_manager is not defined")
        import uvicorn

        uvicorn.run(self.app, host=self.host, port=self.port)

    async def _get_agent_card(self, request: Request) -> JSONResponse:
        # Liefert die AgentCard als JSON zurück.
        return JSONResponse(self.agent_card.model_dump(exclude_none=True))

    async def _process_request(
        self, request: Request
    ) -> Union[JSONResponse, EventSourceResponse]:
        try:
            body = await request.json()
            logger.info(f"Request method: {body.get('method')}")
            logger.info(f"Request body keys: {list(body.keys())}")
            logger.info(f"Params keys: {list(body.get('params', {}).keys())}")
            
            # Handle Google A2A message/send requests directly with manual parsing
            method = body.get('method')
            logger.info(f"Checking method: '{method}' (type: {type(method)})")
            if method == 'message/send':
                logger.info("Processing Google A2A message/send request")
                try:
                    # Manually construct A2AMessageSendRequest
                    from shared.custom_types import A2AMessageSendRequest, MessageSendParams, A2AMessage, A2ATextPart
                    
                    # Extract message parts
                    message_data = body.get('params', {}).get('message', {})
                    parts = []
                    for part_data in message_data.get('parts', []):
                        if part_data.get('kind') == 'text':
                            parts.append(A2ATextPart(
                                kind='text',
                                text=part_data.get('text', ''),
                                mimeType=part_data.get('mimeType', 'text/plain')
                            ))
                    
                    # Create A2A message
                    a2a_message = A2AMessage(
                        role=message_data.get('role', 'user'),
                        parts=parts,
                        messageId=message_data.get('messageId', 'auto'),
                        kind='message'
                    )
                    
                    # Create parameters
                    params = MessageSendParams(message=a2a_message)
                    
                    # Create request
                    json_rpc_request = A2AMessageSendRequest(
                        id=body.get('id', 'auto'),
                        params=params
                    )
                    
                    logger.info(f"Successfully manually parsed A2A message/send request")
                except Exception as e:
                    logger.error(f"Failed to manually parse A2A message/send: {e}")
                    import traceback
                    traceback.print_exc()
                    # Return error immediately
                    from shared.custom_types import InvalidRequestError, JSONRPCResponse
                    return JSONResponse(
                        JSONRPCResponse(
                            id=body.get('id'),
                            error=InvalidRequestError(data=str(e))
                        ).model_dump(exclude_none=True),
                        status_code=400
                    )
            else:
                # Only use TypeAdapter for non-A2A requests
                try:
                    json_rpc_request = A2ARequest.validate_python(body)
                except Exception as e:
                    logger.error(f"Failed to parse non-A2A request: {e}")
                    return JSONResponse(
                        JSONRPCResponse(
                            id=body.get('id'),
                            error=InvalidRequestError(data=str(e))
                        ).model_dump(exclude_none=True),
                        status_code=400
                    )
                
            logger.info(f"Parsed as: {type(json_rpc_request).__name__}")

            if isinstance(json_rpc_request, A2AMessageSendRequest):
                result = await self.task_manager.on_a2a_message_send(
                    json_rpc_request
                )
            elif isinstance(json_rpc_request, A2AMessageStreamRequest):
                # Handle A2A message streaming (future implementation)
                result = await self.task_manager.on_a2a_message_send(
                    json_rpc_request
                )
            elif isinstance(json_rpc_request, GetTaskRequest):
                result = await self.task_manager.on_get_task(json_rpc_request)
            elif isinstance(json_rpc_request, SendTaskRequest):
                result = await self.task_manager.on_send_task(json_rpc_request)
            elif isinstance(json_rpc_request, SendTaskStreamingRequest):
                result = await self.task_manager.on_send_task_subscribe(
                    json_rpc_request
                )
            elif isinstance(json_rpc_request, CancelTaskRequest):
                result = await self.task_manager.on_cancel_task(json_rpc_request)
            elif isinstance(json_rpc_request, SetTaskPushNotificationRequest):
                result = await self.task_manager.on_set_task_push_notification(
                    json_rpc_request
                )
            elif isinstance(json_rpc_request, GetTaskPushNotificationRequest):
                result = await self.task_manager.on_get_task_push_notification(
                    json_rpc_request
                )
            elif isinstance(json_rpc_request, TaskResubscriptionRequest):
                result = await self.task_manager.on_resubscribe_to_task(
                    json_rpc_request
                )
            else:
                logger.warning(f"Unexpected request type: {type(json_rpc_request)}")
                raise ValueError(f"Unexpected request type: {type(json_rpc_request)}")

            return self._create_response(result)

        except Exception as e:
            return self._handle_exception(e)

    def _handle_exception(self, e: Exception) -> JSONResponse:
        if isinstance(e, json.decoder.JSONDecodeError):
            json_rpc_error = JSONParseError()
        elif isinstance(e, ValidationError):
            json_rpc_error = InvalidRequestError(data=json.loads(e.json()))
        else:
            logger.error(f"Unhandled exception: {e}")
            json_rpc_error = InternalError()

        response = JSONRPCResponse(id=None, error=json_rpc_error)
        return JSONResponse(response.model_dump(exclude_none=True), status_code=400)

    def _create_response(self, result: Any) -> Union[JSONResponse, EventSourceResponse]:
        if isinstance(result, AsyncIterable):

            async def event_generator(
                result: AsyncIterable,
            ) -> AsyncIterable[dict[str, str]]:
                async for item in result:
                    yield {"data": item.model_dump_json(exclude_none=True)}

            return EventSourceResponse(event_generator(result))
        elif isinstance(result, JSONRPCResponse):
            return JSONResponse(result.model_dump(exclude_none=True))
        else:
            logger.error(f"Unexpected result type: {type(result)}")
            raise ValueError(f"Unexpected result type: {type(result)}")
