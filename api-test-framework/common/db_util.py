import pymysql
from pymysql.cursors import DictCursor

from config.settings import settings


class DBUtil:
    """数据库校验工具：用于核对接口返回与数据库记录是否一致。"""

    def __init__(self):
        self.conn = pymysql.connect(
            host=settings.db_host,
            port=settings.db_port,
            user=settings.db_user,
            password=settings.db_password,
            database=settings.db_name,
            charset="utf8mb4",
            cursorclass=DictCursor,
            autocommit=True,
        )

    def query_one(self, sql: str, args=None) -> dict | None:
        with self.conn.cursor() as cur:
            cur.execute(sql, args or ())
            return cur.fetchone()

    def query_all(self, sql: str, args=None) -> list[dict]:
        with self.conn.cursor() as cur:
            cur.execute(sql, args or ())
            return list(cur.fetchall())

    def execute(self, sql: str, args=None) -> int:
        with self.conn.cursor() as cur:
            cur.execute(sql, args or ())
            return cur.rowcount

    def close(self) -> None:
        self.conn.close()
