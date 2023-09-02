# import redis.asyncio as redis

import uvicorn

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware

from fastapi_limiter import FastAPILimiter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from src.conf.messages import DB_CONFIG_ERROR, DB_CONNECT_ERROR, WELCOME_MESSAGE


from src.database.connect_db import get_db
from src.routes.auth import router as auth_router
from src.routes.users import router as users_router
from src.routes.ratings import router as ratings_router
from src.conf.config import settings

from src.conf.config import init_async_redis


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


@app.on_event("startup")
async def startup():
    redis_cache = await init_async_redis()

    await FastAPILimiter.init(redis_cache)


@app.get(
    "/",
    tags=["Root"],
    # dependencies=[Depends(RateLimiter(times=2, seconds=5))]
)
async def root():
    return {
        "message": "Welcome to the Snapshot Exchange REST API!",
        "version": "Version 1.0",
        "description": "This API provides access to Snapshot Exchange services.",
        "documentation": "For API documentation, visit our [Documentation Page](https://example.com/documentation).",
        "authors": [
            "Sergiy Ponomarenko (aka sergiokapone)",
            "Sergiy Stepanov",
            "Ilya Vasylevskyi",
            "Oleksandr Tarasov",
        ],
        "license": "This API is distributed under the MIT License.",
        "repository": "Find the source code on [GitHub](https://github.com/sergiokapone/SnapshotExchange).",
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

        return {"message": "You successfully connected to the database!"}

    except Exception as e:
        print(e)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=DB_CONNECT_ERROR,
        )


app.include_router(auth_router, prefix="/api")
app.include_router(users_router, prefix="/api")
app.include_router(ratings_router, prefix="/api")


if __name__ == "__main__":
    HOST = "0.0.0.0"
    PORT = 8000
    uvicorn.run(app="main:app", host=HOST, port=PORT, reload=True)
