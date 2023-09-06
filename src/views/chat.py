from typing import Annotated

from fastapi.templating import Jinja2Templates
from fastapi import (
    APIRouter,
    Request,
    Cookie,
    Depends,
    FastAPI,
    Query,
    WebSocket,
    WebSocketException,
    status,
)

router = APIRouter(tags=["Chat"])
templates = Jinja2Templates(directory="templates")

@router.get("/chat")
async def get(request: Request):
    
    """
    Get Chat HTML Page
    

    This endpoint serves an HTML page for a chat application.

    :param request: The HTTP request object.
    :type request: Request
    :return: The HTML page for the chat.
    :rtype: HTMLResponse
    """
    
    return templates.TemplateResponse(
        "chat.html", {"request": request}
    )

active_connections = []

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    
    """
    WebSocket Endpoint
    

    This WebSocket endpoint establishes a connection for real-time chat.
    Clients can send and receive text messages.

    :param websocket: WebSocket connection.
    :type websocket: WebSocket
    """
    
    await websocket.accept()
    active_connections.append(websocket)  
    try:
        while True:
            data = await websocket.receive_text()  
            for connection in active_connections:
                await connection.send_text(f"Message text was: {data}")
    except WebSocketDisconnect:

        active_connections.remove(websocket)