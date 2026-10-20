"""初始化两个项目的数据库（建库、建账号、建表、写入初始数据）。

支持环境变量：
DB_HOST、DB_PORT、DB_ROOT_USER、DB_ROOT_PASSWORD、DB_USER、DB_PASSWORD
"""

import os
import pathlib

import pymysql

ROOT = pathlib.Path(__file__).resolve().parents[1]

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", "3307"))
DB_ROOT_USER = os.getenv("DB_ROOT_USER", "root")
DB_ROOT_PASSWORD = os.getenv("DB_ROOT_PASSWORD", "")
APP_USER = os.getenv("DB_USER", "tester")
APP_PASSWORD = os.getenv("DB_PASSWORD", "Test@123456")

ROOT_CONN = {
    "host": DB_HOST,
    "port": DB_PORT,
    "user": DB_ROOT_USER,
    "password": DB_ROOT_PASSWORD,
    "charset": "utf8mb4",
    "autocommit": True,
}

DATABASES = {
    "ecommerce_test": ROOT / "ecommerce-order-service" / "sql" / "init.sql",
    "content_manage": ROOT / "digital-content-system" / "sql" / "init.sql",
}


def run_script(database: str, script: pathlib.Path) -> None:
    conn = pymysql.connect(database=database, **ROOT_CONN)
    try:
        sql = script.read_text(encoding="utf-8")
        with conn.cursor() as cur:
            for statement in sql.split(";"):
                if statement.strip():
                    cur.execute(statement)
        print(f"[OK] {database} <- {script.name}")
    finally:
        conn.close()


def main() -> None:
    conn = pymysql.connect(**ROOT_CONN)
    try:
        with conn.cursor() as cur:
            for database in DATABASES:
                cur.execute(
                    f"CREATE DATABASE IF NOT EXISTS {database} "
                    "DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
                )
            cur.execute(
                f"CREATE USER IF NOT EXISTS '{APP_USER}'@'%' "
                f"IDENTIFIED WITH mysql_native_password BY '{APP_PASSWORD}'"
            )
            for database in DATABASES:
                cur.execute(f"GRANT ALL PRIVILEGES ON {database}.* TO '{APP_USER}'@'%'")
            cur.execute("FLUSH PRIVILEGES")
    finally:
        conn.close()

    for database, script in DATABASES.items():
        run_script(database, script)
    print("数据库初始化完成。")


if __name__ == "__main__":
    main()
