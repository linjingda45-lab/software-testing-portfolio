import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """服务配置，全部支持环境变量覆盖，便于本地与 CI 切换环境。"""

    db_host: str = os.getenv("DB_HOST", "127.0.0.1")
    db_port: int = int(os.getenv("DB_PORT", "3307"))
    db_user: str = os.getenv("DB_USER", "tester")
    db_password: str = os.getenv("DB_PASSWORD", "Test@123456")
    db_name: str = os.getenv("DB_NAME", "ecommerce_test")


settings = Settings()
