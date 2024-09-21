from fastapi import FastAPI,Request,HTTPException
from  .routers import users
from .database import engine
from .models import Base
import aioredis
import time
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from . import models


from .utility.auth import get_current_user


Base.metadata.create_all(bind=engine)

app = FastAPI()
from .database import get_db

@app.on_event("startup")
async def startup_event():
    try:
        app.state.redis = await aioredis.create_redis_pool("redis://localhost")
    except Exception as e:
        print(f"Error connecting to Redis: {e}")
        app.state.redis = None  

@app.on_event("shutdown")
async def shutdown_event():
    await app.state.redis.close()

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

EXEMPT_ROUTES = ['/login/', '/register/', '/register','/docs','/openapi.json']


async def get_user_rate_limit(db: Session, username: str):
    user = db.query(models.User).filter(models.User.email == username).first()
    if user:
        return user.limit, user.window_seconds
    return None, None

async def rate_limiter(db: Session, user: str):

    redis = app.state.redis
    limit, window = await get_user_rate_limit(db, user)
    print(limit,window)
    if limit is 0:
        return  # No rate limit for this user

    redis_key = f"rate_limit:{user}"
    current_time = int(time.time())

    rate_data = await redis.get(redis_key)

    if rate_data:
        calls, timestamp = map(int, rate_data.decode().split(":"))
    else:
        calls, timestamp = 0, current_time
    

    if current_time - timestamp > window:
        calls = 0
        timestamp = current_time

    calls += 1

    if calls >= limit:
        retry_after = window - (current_time - timestamp)  # Time until the limit resets
        return True, retry_after
    
    await redis.set(redis_key, f"{calls}:{timestamp}")
    return False



@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    # Check if the request path is in the exempt routes
    try:
        if request.url.path in EXEMPT_ROUTES:
            response = await call_next(request)
            return response

        db: Session = next(get_db())

        user = await get_current_user(request.headers.get("Authorization", ""))
        limit_exceeded = await rate_limiter(db, user)
        if isinstance(limit_exceeded, tuple):
            retry_after = limit_exceeded[1]
            return JSONResponse(
                status_code=429,
                content={"detail": f"Rate limit exceeded. You can try again in {retry_after} seconds."}
            )
        response = await call_next(request)
        return response

    except HTTPException as exc:
        return await http_exception_handler(request, exc)
    
# Register API routers
app.include_router(users.router)

