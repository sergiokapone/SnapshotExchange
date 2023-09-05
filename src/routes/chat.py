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

router = APIRouter(prefix="/chat", tags=["Chat"])
templates = Jinja2Templates(directory="templates")

@router.get("/")
async def get(request: Request):
    return templates.TemplateResponse(
        "chat.html", {"request": request}
    )

# async def get_cookie_or_token(
#     websocket: WebSocket,
#     session: Annotated[str | None, Cookie()] = None,
#     token: Annotated[str | None, Query()] = None,
# ):

#     if session is None and token is None:
#         raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
#     return session or token


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    print('asdfadfdf')
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")