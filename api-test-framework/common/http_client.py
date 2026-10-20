import logging

import allure
import requests

logger = logging.getLogger("api")


class ApiClient:
    """对 Requests 的轻量封装：统一 base_url、超时、日志与 Allure 附件。"""

    def __init__(self, base_url: str, token: str | None = None):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        if token:
            self.set_token(token)

    def set_token(self, token: str) -> None:
        self.session.headers["Authorization"] = f"Bearer {token}"

    def request(self, method: str, path: str, **kwargs) -> requests.Response:
        url = f"{self.base_url}{path}"
        kwargs.setdefault("timeout", 10)
        with allure.step(f"{method} {path}"):
            response = self.session.request(method, url, **kwargs)
            allure.attach(
                str(kwargs.get("json", "")),
                name="请求参数",
                attachment_type=allure.attachment_type.JSON,
            )
            allure.attach(
                response.text,
                name=f"{response.status_code} 响应",
                attachment_type=allure.attachment_type.JSON,
            )
        logger.info("%s %s -> %s", method, url, response.status_code)
        return response

    def get(self, path: str, **kwargs) -> requests.Response:
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs) -> requests.Response:
        return self.request("POST", path, **kwargs)

    def put(self, path: str, **kwargs) -> requests.Response:
        return self.request("PUT", path, **kwargs)
