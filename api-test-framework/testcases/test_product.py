import allure
import pytest

pytestmark = allure.epic("电商订单系统")


@allure.feature("商品查询")
class TestProduct:
    @allure.story("商品列表")
    @allure.title("默认查询只返回在售商品")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_list_products_default(self, anon_client):
        response = anon_client.get("/api/products")
        body = response.json()

        assert response.status_code == 200
        assert body["code"] == 0
        assert body["data"]["total"] == 4
        assert all(item["status"] == 1 for item in body["data"]["list"])

    @allure.story("商品列表")
    @allure.title("按名称关键字模糊查询可命中目标商品")
    @pytest.mark.smoke
    def test_list_products_by_keyword(self, anon_client):
        response = anon_client.get("/api/products", params={"keyword": "键盘"})
        data = response.json()["data"]

        assert data["total"] == 1
        assert data["list"][0]["name"] == "机械键盘"

    @allure.story("商品列表")
    @allure.title("关键字无匹配时返回空列表")
    @pytest.mark.regression
    def test_list_products_keyword_no_match(self, anon_client):
        response = anon_client.get("/api/products", params={"keyword": "不存在的商品"})
        data = response.json()["data"]

        assert response.status_code == 200
        assert data["total"] == 0
        assert data["list"] == []

    @allure.story("商品列表")
    @allure.title("分页参数生效，返回指定条数")
    @pytest.mark.regression
    def test_list_products_pagination(self, anon_client):
        response = anon_client.get("/api/products", params={"page": 1, "size": 2})
        data = response.json()["data"]

        assert data["page"] == 1
        assert data["size"] == 2
        assert len(data["list"]) == 2

    @allure.story("分页边界")
    @allure.title("page=0 时返回参数校验失败")
    @pytest.mark.regression
    def test_list_products_invalid_page(self, anon_client):
        response = anon_client.get("/api/products", params={"page": 0})

        assert response.status_code == 400
        assert response.json()["code"] == 4001

    @allure.story("分页边界")
    @allure.title("size 超过 50 时返回参数校验失败")
    @pytest.mark.regression
    def test_list_products_invalid_size(self, anon_client):
        response = anon_client.get("/api/products", params={"size": 51})

        assert response.status_code == 400
        assert response.json()["code"] == 4001

    @allure.story("商品详情")
    @allure.title("查询在售商品详情成功")
    @pytest.mark.smoke
    def test_get_product_detail(self, anon_client):
        response = anon_client.get("/api/products/1")
        data = response.json()["data"]

        assert response.status_code == 200
        assert data["name"] == "机械键盘"
        assert data["price"] == 299.0

    @allure.story("商品详情")
    @allure.title("查询不存在的商品返回 404")
    @pytest.mark.regression
    def test_get_product_not_exist(self, anon_client):
        response = anon_client.get("/api/products/9999")

        assert response.status_code == 404
        assert response.json()["code"] == 2001

    @allure.story("商品详情")
    @allure.title("查询已下架商品返回 404")
    @pytest.mark.regression
    def test_get_off_shelf_product(self, anon_client):
        response = anon_client.get("/api/products/5")

        assert response.status_code == 404
        assert response.json()["code"] == 2001
