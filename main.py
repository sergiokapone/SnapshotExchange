# import redis.asyncio as redis

import uvicorn

from fastapi import FastAPI, HTTPException, Depends, status

from fastapi_limiter import FastAPILimiter

from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import text

from src.conf.messages import DB_CONFIG_ERROR, DB_CONNECT_ERROR, WELCOME_MESSAGE

from src.database.connect_db import get_db
from src.routes.auth import router as auth_router
from src.routes.users import router as users_router
from src.routes.ratings import router as ratings_router
from src.routes.photos import router as photos_router
from src.conf.config import settings

from src.conf.config import init_async_redis

app = FastAPI(

    debug=True,

    title="Snapshot Exchange",
)


@app.on_event("startup")
async def startup():
    redis_cache = await init_async_redis()

    await FastAPILimiter.init(redis_cache)


@app.get("/", tags=["Root"],

         # dependencies=[Depends(RateLimiter(times=2, seconds=5))]
         )
async def read_root():
    return {"message": "Photo Share REST API"}


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


app.include_router(photos_router, prefix='/api')
app.include_router(auth_router, prefix='/api')
app.include_router(users_router, prefix='/api')
app.include_router(ratings_router, prefix='/api')

if __name__ == '__main__':
    HOST = 'localhost'

    PORT = 8000

    uvicorn.run(app='main:app', host=HOST, port=PORT, reload=True)
