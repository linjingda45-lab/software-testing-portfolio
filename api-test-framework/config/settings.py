import os
from dataclasses import dataclass


@dataclass(frozen=True)
class TestSettings:
    """测试环境配置，支持通过环境变量覆盖，方便切换本地/测试环境。"""

    base_url: str = os.getenv("API_BASE_URL", "http://127.0.0.1:8081")
    db_host: str = os.getenv("DB_HOST", "127.0.0.1")
    db_port: int = int(os.getenv("DB_PORT", "3307"))
    db_user: str = os.getenv("DB_USER", "tester")
    db_password: str = os.getenv("DB_PASSWORD", "Test@123456")
    db_name: str = os.getenv("DB_NAME", "ecommerce_test")

    test_username: str = "testuser"
    test_password: str = "123456"
    other_username: str = "otheruser"
    other_password: str = "123456"


settings = TestSettings()
