from dotenv import load_dotenv
load_dotenv()
from src.routers import balance as balance_router
import asyncio
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from fastapi import FastAPI
from contextlib import asynccontextmanager

from src.config.database import init_db_pool, close_db_pool
from src.middlewares.trace_middleware import trace_middleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db_pool()
    yield
    await close_db_pool()



app = FastAPI(
    lifespan=lifespan,
    title="Core Saldo API",
    version="1.0.0"
)

app.middleware("http")(trace_middleware)

app.include_router(balance_router.router, prefix="/core2", tags=["Balance"])

@app.get("/")
def read_root():
    return {"service": "core-saldo", "status": "ok"}