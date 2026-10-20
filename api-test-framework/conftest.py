import pytest

from common.db_util import DBUtil
from common.http_client import ApiClient
from config.settings import settings

# 各商品在 init.sql 中的初始库存，用例执行前后用于数据还原
SEED_STOCK = {1: 50, 2: 100, 3: 20, 4: 0, 5: 10}


@pytest.fixture(scope="session")
def anon_client() -> ApiClient:
    """未登录的客户端，用于登录及鉴权异常场景。"""
    return ApiClient(settings.base_url)


@pytest.fixture(scope="session")
def token(anon_client: ApiClient) -> str:
    response = anon_client.post(
        "/api/auth/login",
        json={"username": settings.test_username, "password": settings.test_password},
    )
    assert response.status_code == 200, f"登录失败：{response.text}"
    return response.json()["data"]["token"]


@pytest.fixture(scope="session")
def other_token(anon_client: ApiClient) -> str:
    response = anon_client.post(
        "/api/auth/login",
        json={"username": settings.other_username, "password": settings.other_password},
    )
    assert response.status_code == 200, f"其他用户登录失败：{response.text}"
    return response.json()["data"]["token"]


@pytest.fixture(scope="session")
def api(token: str) -> ApiClient:
    """已登录客户端，业务用例主要使用该 fixture。"""
    return ApiClient(settings.base_url, token=token)


@pytest.fixture(scope="session")
def other_api(other_token: str) -> ApiClient:
    return ApiClient(settings.base_url, token=other_token)


@pytest.fixture(scope="session")
def db():
    util = DBUtil()
    yield util
    util.close()


@pytest.fixture(autouse=True)
def clean_order_data(db):
    """每个用例执行前后清理订单并还原库存，保证用例独立、可重复执行。"""

    def reset():
        db.execute("DELETE FROM orders WHERE user_id IN (1, 2)")
        for product_id, stock in SEED_STOCK.items():
            db.execute("UPDATE products SET stock = %s WHERE id = %s", (stock, product_id))

    reset()
    yield
    reset()
