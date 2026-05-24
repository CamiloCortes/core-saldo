import asyncpg
import os

_pool = None

async def init_db_pool():
    global _pool
    _pool = await asyncpg.create_pool(
        host=os.getenv("POSTGRES_HOST"),
        port=int(os.getenv("POSTGRES_PORT")),
        database=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        min_size=2,
        max_size=10,
    )
    print("Pool de PostgreSQL inicializado")

async def close_db_pool():
    global _pool
    if _pool:
        await _pool.close()
        print("Pool de PostgreSQL cerrado")

def get_db_pool():
    if _pool is None:
        raise RuntimeError("Pool no inicializado")
    return _pool
