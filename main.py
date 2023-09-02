# import redis.asyncio as redis

import uvicorn
from datetime import datetime

from fastapi.templating import Jinja2Templates

from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter import FastAPILimiter
from fastapi.responses import HTMLResponse

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from src.conf.messages import DB_CONFIG_ERROR, DB_CONNECT_ERROR, WELCOME_MESSAGE


from src.database.connect_db import get_db
from src.routes.auth import router as auth_router
from src.routes.users import router as users_router
from src.routes.ratings import router as ratings_router
from src.routes.photos import router as photos_router
from src.conf.config import settings
from src.conf.info_dict import project_info

from src.conf.config import init_async_redis

current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

app = FastAPI(
    debug=True,
    title="Snapshot Exchange",
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.on_event("startup")
async def startup():
    redis_cache = await init_async_redis()

    await FastAPILimiter.init(redis_cache)


@app.get(
    "/",
    tags=["Root"],
    # dependencies=[Depends(RateLimiter(times=2, seconds=5))]
)
@app.get("/")
async def root(request: Request):
    return project_info


@app.get("/info", response_class=HTMLResponse, include_in_schema=False)
async def root(request: Request):
    project_info.update({"request": request})
    return templates.TemplateResponse(
        "index.html", project_info
    )


@app.get("/api/healthchecker", tags=["Root"])
async def healthchecker(session: AsyncSession = Depends(get_db)):
    try:
        result = await session.execute(text("SELECT 1"))
        rows = result.fetchall()
        if not rows:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=DB_CONFIG_ERROR,
            )

        return {
            "status": "healthy",
            "message": "You successfully connected to the database!",
            "server_time": current_time,
        }

    except Exception as e:
        print(e)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=DB_CONNECT_ERROR,
        )


app.include_router(auth_router, prefix="/api")
app.include_router(users_router, prefix="/api")
app.include_router(ratings_router, prefix="/api")
app.include_router(photos_router, prefix='/api')


if __name__ == "__main__":
    HOST = "0.0.0.0"
    PORT = 8000
    uvicorn.run(app="main:app", host=HOST, port=PORT, reload=True)
