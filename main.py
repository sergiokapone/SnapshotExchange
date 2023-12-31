import uvicorn
from datetime import datetime

from fastapi.templating import Jinja2Templates

from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter import FastAPILimiter


from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from src.conf.messages import DB_CONFIG_ERROR, DB_CONNECT_ERROR


from src.database.connect_db import get_db

from src.routes.auth import router as auth_router
from src.routes.users import router as users_router
from src.routes.ratings import router as ratings_router
from src.routes.photos import router as photos_router
from src.routes.comments import router as comments_router
from src.routes.search import router as search_router

from src.views.dashboard import router as dashboard_views_router
from src.views.auth import router as auth_views_router
from src.views.users import router as user_views_router
from src.views.photos import router as photo_views_router
from src.views.chat import router as chat_router


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
    allow_credentials=True,
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
    include_in_schema=False,
    # dependencies=[Depends(RateLimiter(times=2, seconds=5))]
)
async def root():
    return {
        "name": "Snapshot Exchange REST API!",
        "version": "Version 1.0",
        "description": "This API provides access to Snapshot Exchange services.",
        "authors": [
            {
                "name": "Sergiy Ponomarenko (aka sergiokapone)",
                "github": "https://github.com/sergiokapone",
                "additional_info": "Team Lead of Project",
            },
            {
                "name": "Sergiy Stepanov",
                "github": "https://github.com/S-Stepanov-1",
                "additional_info": "Scrum Master",
            },
            {
                "name": "Ilya Vasylevskyi",
                "github": "https://github.com/BonesetterB",
                "additional_info": "Contributor",
            },
            {
                "name": "Oleksandr Tarasov",
                "github": "https://github.com/Taras55001",
                "additional_info": "Contributor",
            },
        ],
        "license": "This API is distributed under the MIT License.",
        "site": "https://snapshotexchange.onrender.com/docs",
        "repository": "https://github.com/sergiokapone/SnapshotExchange",
    }


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
        raise e

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=DB_CONNECT_ERROR,
        )


@app.get("/list", tags=["Root"])
def get_all_urls_from_request(request: Request) -> list[dict]:
    routes = [
        {
            "path": str(request.base_url)[:-1] + route.path,
            "name": route.name,
            "method": route.methods,
            "description": route.description,
        }
        for route in request.app.routes
        if hasattr(route, "description") and route.description is not None
    ]
    return routes


app.include_router(auth_router, prefix="/api")
app.include_router(users_router, prefix="/api")
app.include_router(photos_router, prefix="/api")
app.include_router(comments_router, prefix="/api")
app.include_router(search_router, prefix="/api")
app.include_router(ratings_router, prefix="/api")

app.include_router(dashboard_views_router, prefix="/views")
app.include_router(auth_views_router, prefix="/views")
app.include_router(user_views_router, prefix="/views")
app.include_router(photo_views_router, prefix="/views")
app.include_router(chat_router, prefix="/views")


if __name__ == "__main__":
    HOST = "0.0.0.0"
    PORT = 8000
    uvicorn.run(app="main:app", host=HOST, port=PORT, reload=True)
