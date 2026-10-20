import allure
import pytest

from common.data_factory import order_payload, unique_request_id

pytestmark = allure.epic("电商订单系统")


def create_order(api, **overrides):
    return api.post("/api/orders", json=order_payload(**overrides))


@allure.feature("订单交易")
class TestOrder:
    @allure.story("创建订单")
    @allure.title("正常下单成功并同步扣减库存")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    def test_create_order_success(self, api, db):
        response = create_order(api, product_id=1, quantity=2)
        data = response.json()["data"]

        assert response.status_code == 200
        assert response.json()["code"] == 0
        assert data["duplicated"] is False
        assert data["status"] == "CREATED"
        assert data["totalAmount"] == 598.0

        row = db.query_one(
            "SELECT * FROM orders WHERE order_no = %s", (data["orderNo"],)
        )
        assert row is not None
        assert row["product_id"] == 1
        assert row["quantity"] == 2
        assert float(row["total_amount"]) == 598.0
        assert row["status"] == "CREATED"

        stock = db.query_one("SELECT stock FROM products WHERE id = 1")["stock"]
        assert stock == 48

    @allure.story("重复提交")
    @allure.title("相同 requestId 重复提交只生成一笔订单")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    def test_create_order_duplicate_request(self, api, db):
        payload = order_payload(product_id=1, quantity=2)

        first = api.post("/api/orders", json=payload).json()["data"]
        second_response = api.post("/api/orders", json=payload)
        second = second_response.json()["data"]

        assert second_response.status_code == 200
        assert second["duplicated"] is True
        assert second["orderNo"] == first["orderNo"]

        count = db.query_one(
            "SELECT COUNT(*) AS c FROM orders WHERE request_id = %s",
            (payload["requestId"],),
        )["c"]
        assert count == 1
        assert db.query_one("SELECT stock FROM products WHERE id = 1")["stock"] == 48

    @allure.story("库存校验")
    @allure.title("库存为 0 时下单失败")
    @pytest.mark.regression
    def test_create_order_out_of_stock(self, api, db):
        response = create_order(api, product_id=4, quantity=1)

        assert response.status_code == 400
        assert response.json()["code"] == 2004
        assert db.query_one("SELECT COUNT(*) AS c FROM orders")["c"] == 0

    @allure.story("库存校验")
    @allure.title("购买数量超过库存时下单失败")
    @pytest.mark.regression
    def test_create_order_quantity_exceed_stock(self, api):
        response = create_order(api, product_id=3, quantity=99)

        assert response.status_code == 400
        assert response.json()["code"] == 2004

    @allure.story("商品校验")
    @allure.title("商品不存在时下单失败")
    @pytest.mark.regression
    def test_create_order_product_not_exist(self, api):
        response = create_order(api, product_id=9999, quantity=1)

        assert response.status_code == 404
        assert response.json()["code"] == 2001

    @allure.story("商品校验")
    @allure.title("商品已下架时下单失败")
    @pytest.mark.regression
    def test_create_order_off_shelf_product(self, api):
        response = create_order(api, product_id=5, quantity=1)

        assert response.status_code == 404
        assert response.json()["code"] == 2001

    @allure.story("参数边界")
    @allure.title("购买数量为 0 时返回参数校验失败")
    @pytest.mark.regression
    def test_create_order_quantity_zero(self, api):
        response = create_order(api, quantity=0)

        assert response.status_code == 400
        assert response.json()["code"] == 4001

    @allure.story("参数边界")
    @allure.title("购买数量为负数时返回参数校验失败")
    @pytest.mark.regression
    def test_create_order_quantity_negative(self, api):
        response = create_order(api, quantity=-1)

        assert response.status_code == 400
        assert response.json()["code"] == 4001

    @allure.story("参数边界")
    @allure.title("购买数量超过单笔上限 99 时返回参数校验失败")
    @pytest.mark.regression
    def test_create_order_quantity_over_limit(self, api):
        response = create_order(api, quantity=100)

        assert response.status_code == 400
        assert response.json()["code"] == 4001

    @allure.story("必填校验")
    @allure.title("缺少收货地址时返回参数校验失败")
    @pytest.mark.regression
    def test_create_order_missing_address(self, api):
        payload = order_payload()
        payload.pop("address")

        response = api.post("/api/orders", json=payload)

        assert response.status_code == 400
        assert response.json()["code"] == 4001

    @allure.story("必填校验")
    @allure.title("缺少幂等请求号时返回参数校验失败")
    @pytest.mark.regression
    def test_create_order_missing_request_id(self, api):
        payload = order_payload()
        payload.pop("requestId")

        response = api.post("/api/orders", json=payload)

        assert response.status_code == 400
        assert response.json()["code"] == 4001

    @allure.story("必填校验")
    @allure.title("幂等请求号长度不足时返回参数校验失败")
    @pytest.mark.regression
    def test_create_order_short_request_id(self, api):
        response = create_order(api, requestId="abc")

        assert response.status_code == 400
        assert response.json()["code"] == 4001

    @allure.story("鉴权")
    @allure.title("未登录用户下单返回 401")
    @pytest.mark.regression
    def test_create_order_without_token(self, anon_client):
        response = anon_client.post("/api/orders", json=order_payload())

        assert response.status_code == 401
        assert response.json()["code"] == 1003

    @allure.story("订单查询")
    @allure.title("根据订单号查询订单详情成功")
    @pytest.mark.smoke
    def test_get_order_detail(self, api):
        created = create_order(api, product_id=2, quantity=1).json()["data"]

        response = api.get(f"/api/orders/{created['orderNo']}")
        data = response.json()["data"]

        assert response.status_code == 200
        assert data["orderNo"] == created["orderNo"]
        assert data["productName"] == "无线鼠标"
        assert data["quantity"] == 1
        assert data["totalAmount"] == 99.0

    @allure.story("订单查询")
    @allure.title("查询不存在的订单返回 404")
    @pytest.mark.regression
    def test_get_order_not_exist(self, api):
        response = api.get("/api/orders/ORD-NOT-EXIST")

        assert response.status_code == 404
        assert response.json()["code"] == 3001

    @allure.story("越权校验")
    @allure.title("查看他人订单返回 403")
    @pytest.mark.regression
    def test_get_other_user_order_forbidden(self, api, other_api):
        created = create_order(api, product_id=2, quantity=1).json()["data"]

        response = other_api.get(f"/api/orders/{created['orderNo']}")

        assert response.status_code == 403
        assert response.json()["code"] == 3002

    @allure.story("越权校验")
    @allure.title("操作他人订单状态返回 403")
    @pytest.mark.regression
    def test_update_other_user_order_forbidden(self, api, other_api):
        created = create_order(api, product_id=2, quantity=1).json()["data"]

        response = other_api.put(
            f"/api/orders/{created['orderNo']}/status", json={"status": "PAID"}
        )

        assert response.status_code == 403
        assert response.json()["code"] == 3002

    @allure.story("订单列表")
    @allure.title("按状态筛选订单，结果与数据库一致")
    @pytest.mark.smoke
    def test_list_orders_filter_by_status(self, api, db):
        created = create_order(api, product_id=2, quantity=1).json()["data"]
        api.put(f"/api/orders/{created['orderNo']}/status", json={"status": "PAID"})

        response = api.get("/api/orders", params={"status": "PAID"})
        data = response.json()["data"]

        assert response.status_code == 200
        assert data["total"] == 1
        assert all(item["status"] == "PAID" for item in data["list"])
        assert db.query_one(
            "SELECT status FROM orders WHERE order_no = %s", (created["orderNo"],)
        )["status"] == "PAID"

    @allure.story("订单列表")
    @allure.title("使用非法状态筛选订单返回 400")
    @pytest.mark.regression
    def test_list_orders_invalid_status(self, api):
        response = api.get("/api/orders", params={"status": "UNKNOWN"})

        assert response.status_code == 400
        assert response.json()["code"] == 3003

    @allure.story("状态流转")
    @allure.title("取消订单后库存回补")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_cancel_order_restore_stock(self, api, db):
        created = create_order(api, product_id=2, quantity=3).json()["data"]
        assert db.query_one("SELECT stock FROM products WHERE id = 2")["stock"] == 97

        response = api.put(
            f"/api/orders/{created['orderNo']}/status", json={"status": "CANCELLED"}
        )
        data = response.json()["data"]

        assert response.status_code == 200
        assert data["status"] == "CANCELLED"
        assert db.query_one("SELECT stock FROM products WHERE id = 2")["stock"] == 100
        assert db.query_one(
            "SELECT status FROM orders WHERE order_no = %s", (created["orderNo"],)
        )["status"] == "CANCELLED"

    @allure.story("状态流转")
    @allure.title("订单状态不允许跳变：CREATED 直接变更为 SHIPPED 被拒绝")
    @pytest.mark.regression
    def test_invalid_status_transition(self, api, db):
        created = create_order(api, product_id=1, quantity=1).json()["data"]

        response = api.put(
            f"/api/orders/{created['orderNo']}/status", json={"status": "SHIPPED"}
        )

        assert response.status_code == 400
        assert response.json()["code"] == 3004
        assert db.query_one(
            "SELECT status FROM orders WHERE order_no = %s", (created["orderNo"],)
        )["status"] == "CREATED"

    @allure.story("状态流转")
    @allure.title("订单完整正向流转：CREATED -> PAID -> SHIPPED -> COMPLETED")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    def test_full_status_flow(self, api, db):
        created = create_order(api, product_id=1, quantity=1).json()["data"]
        order_no = created["orderNo"]

        for status in ("PAID", "SHIPPED", "COMPLETED"):
            response = api.put(f"/api/orders/{order_no}/status", json={"status": status})
            assert response.status_code == 200
            assert response.json()["data"]["status"] == status

        assert db.query_one(
            "SELECT status FROM orders WHERE order_no = %s", (order_no,)
        )["status"] == "COMPLETED"

    @allure.story("状态流转")
    @allure.title("更新不存在订单的状态返回 404")
    @pytest.mark.regression
    def test_update_status_order_not_exist(self, api):
        response = api.put("/api/orders/ORD-NOT-EXIST/status", json={"status": "PAID"})

        assert response.status_code == 404
        assert response.json()["code"] == 3001

    @allure.story("鉴权")
    @allure.title("未登录查询订单列表返回 401")
    @pytest.mark.regression
    def test_list_orders_without_token(self, anon_client):
        response = anon_client.get("/api/orders")

        assert response.status_code == 401
        assert response.json()["code"] == 1003

    @allure.story("鉴权")
    @allure.title("未登录修改订单状态返回 401")
    @pytest.mark.regression
    def test_update_status_without_token(self, anon_client):
        response = anon_client.put(
            "/api/orders/ORD-NOT-EXIST/status", json={"status": "PAID"}
        )

        assert response.status_code == 401
        assert response.json()["code"] == 1003
