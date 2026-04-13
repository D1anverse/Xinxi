"""
SoulMatch 数据库连接池
使用 asyncpg 连接 PostgreSQL
"""
import asyncpg
from typing import Optional
import os

_pool: Optional[asyncpg.Pool] = None


async def get_pool() -> asyncpg.Pool:
    """获取数据库连接池"""
    global _pool
    if _pool is None:
        database_url = os.getenv(
            "DATABASE_URL",
            "postgresql://soulmatch_user:secure_password@localhost:5432/soulmatch"
        )
        _pool = await asyncpg.create_pool(
            database_url,
            min_size=5,
            max_size=20,
            command_timeout=60
        )
    return _pool


async def close_pool():
    """关闭数据库连接池"""
    global _pool
    if _pool:
        await _pool.close()
        _pool = None


async def get_connection():
    """获取数据库连接"""
    pool = await get_pool()
    return await pool.acquire()


async def release_connection(conn):
    """释放数据库连接"""
    pool = await get_pool()
    await pool.release(conn)
