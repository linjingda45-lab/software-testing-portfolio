from contextlib import contextmanager
from typing import Any, Iterable, Optional

import pymysql
from pymysql.cursors import DictCursor

from .config import settings


def _connect() -> pymysql.connections.Connection:
    return pymysql.connect(
        host=settings.db_host,
        port=settings.db_port,
        user=settings.db_user,
        password=settings.db_password,
        database=settings.db_name,
        charset="utf8mb4",
        cursorclass=DictCursor,
        autocommit=False,
        init_command="SET time_zone = '+08:00'",
    )


@contextmanager
def get_cursor(commit: bool = False):
    """只读或单条写入场景使用的游标上下文。"""
    conn = _connect()
    try:
        with conn.cursor() as cur:
            yield cur
        if commit:
            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


@contextmanager
def transaction():
    """多表事务：库存扣减 + 订单写入必须在同一事务中。"""
    conn = _connect()
    try:
        with conn.cursor() as cur:
            yield cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def query_one(sql: str, args: Optional[Iterable[Any]] = None) -> Optional[dict]:
    with get_cursor() as cur:
        cur.execute(sql, tuple(args) if args else ())
        return cur.fetchone()


def query_all(sql: str, args: Optional[Iterable[Any]] = None) -> list[dict]:
    with get_cursor() as cur:
        cur.execute(sql, tuple(args) if args else ())
        return list(cur.fetchall())


def execute(sql: str, args: Optional[Iterable[Any]] = None) -> int:
    with get_cursor(commit=True) as cur:
        cur.execute(sql, tuple(args) if args else ())
        return cur.rowcount
