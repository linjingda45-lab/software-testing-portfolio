import allure
import pytest

from config.settings import settings

pytestmark = allure.epic("电商订单系统")


@allure.feature("用户登录")
class TestLogin:
    @allure.story("正常登录")
    @allure.title("使用正确的用户名和密码登录成功")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    def test_login_success(self, anon_client):
        response = anon_client.post(
            "/api/auth/login",
            json={"username": settings.test_username, "password": settings.test_password},
        )
        body = response.json()

        assert response.status_code == 200
        assert body["code"] == 0
        assert len(body["data"]["token"]) == 32
        assert body["data"]["username"] == settings.test_username
        assert body["data"]["userId"] == 1

    @allure.story("密码校验")
    @allure.title("密码错误登录失败并返回 1002")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.regression
    def test_login_wrong_password(self, anon_client):
        response = anon_client.post(
            "/api/auth/login",
            json={"username": settings.test_username, "password": "wrong-password"},
        )
        body = response.json()

        assert response.status_code == 401
        assert body["code"] == 1002
        assert body["data"] is None

    @allure.story("账号校验")
    @allure.title("不存在的用户登录失败")
    @pytest.mark.regression
    def test_login_unknown_user(self, anon_client):
        response = anon_client.post(
            "/api/auth/login",
            json={"username": "not-exist-user", "password": "123456"},
        )
        assert response.status_code == 401
        assert response.json()["code"] == 1002

    @allure.story("必填校验")
    @allure.title("缺少密码时返回参数校验失败")
    @pytest.mark.regression
    def test_login_missing_password(self, anon_client):
        response = anon_client.post(
            "/api/auth/login", json={"username": settings.test_username}
        )
        assert response.status_code == 400
        assert response.json()["code"] == 4001

    @allure.story("必填校验")
    @allure.title("缺少用户名时返回参数校验失败")
    @pytest.mark.regression
    def test_login_missing_username(self, anon_client):
        response = anon_client.post(
            "/api/auth/login", json={"password": settings.test_password}
        )
        assert response.status_code == 400
        assert response.json()["code"] == 4001

    @allure.story("必填校验")
    @allure.title("用户名为空字符串时返回参数校验失败")
    @pytest.mark.regression
    def test_login_empty_username(self, anon_client):
        response = anon_client.post(
            "/api/auth/login", json={"username": "", "password": settings.test_password}
        )
        assert response.status_code == 400
        assert response.json()["code"] == 4001

    @allure.story("令牌校验")
    @allure.title("使用伪造令牌访问个人信息返回 401")
    @pytest.mark.regression
    def test_profile_with_invalid_token(self, anon_client):
        response = anon_client.get(
            "/api/auth/profile", headers={"Authorization": "Bearer invalid-token"}
        )
        assert response.status_code == 401
        assert response.json()["code"] == 1003
