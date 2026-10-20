import random
import time
from decimal import Decimal

import pymysql
from fastapi import APIRouter, Depends, Query

from ..db import query_all, query_one, transaction
from ..errors import ApiError, ok
from ..schemas import OrderCreateRequest, OrderStatusRequest
from ..security import require_user

router = APIRouter(prefix="/api/orders", tags=["订单"])

VALID_STATUS = {"CREATED", "PAID", "SHIPPED", "COMPLETED", "CANCELLED"}
# 订单状态机：只允许合法的正向流转
TRANSITIONS = {
    "CREATED": {"PAID", "CANCELLED"},
    "PAID": {"SHIPPED"},
    "SHIPPED": {"COMPLETED"},
    "COMPLETED": set(),
    "CANCELLED": set(),
}

_ORDER_SQL = """
SELECT o.id, o.order_no, o.user_id, o.product_id, p.name AS product_name,
       o.quantity, o.total_amount, o.status, o.address, o.request_id,
       o.created_at, o.updated_at
FROM orders o
JOIN products p ON p.id = o.product_id
"""


def _serialize(row: dict) -> dict:
    return {
        "id": row["id"],
        "orderNo": row["order_no"],
        "productId": row["product_id"],
        "productName": row["product_name"],
        "quantity": row["quantity"],
        "totalAmount": float(row["total_amount"]),
        "status": row["status"],
        "address": row["address"],
        "requestId": row["request_id"],
        "createdAt": row["created_at"],
        "updatedAt": row["updated_at"],
    }


def _find_order(order_no: str) -> dict:
    row = query_one(_ORDER_SQL + " WHERE o.order_no = %s", (order_no,))
    if row is None:
        raise ApiError(404, 3001, "订单不存在")
    return row


def _generate_order_no() -> str:
    return "ORD" + time.strftime("%Y%m%d%H%M%S") + f"{random.randint(0, 999999):06d}"


@router.post("")
def create_order(body: OrderCreateRequest, user: dict = Depends(require_user)):
    """创建订单：校验商品与库存 -> 扣减库存 -> 写入订单，保证数据一致性。"""
    try:
        with transaction() as cur:
            # 幂等校验：同一用户的相同 requestId 直接返回已有订单，避免重复下单
            cur.execute(
                _ORDER_SQL + " WHERE o.user_id = %s AND o.request_id = %s",
                (user["userId"], body.requestId),
            )
            existing = cur.fetchone()
            if existing is not None:
                data = _serialize(existing)
                data["duplicated"] = True
                return ok(data, message="重复提交，返回已创建订单")

            cur.execute(
                "SELECT id, name, price, stock, status FROM products WHERE id = %s FOR UPDATE",
                (body.productId,),
            )
            product = cur.fetchone()
            if product is None or product["status"] != 1:
                raise ApiError(404, 2001, "商品不存在或已下架")
            if product["stock"] < body.quantity:
                raise ApiError(400, 2004, "商品库存不足")

            cur.execute(
                "UPDATE products SET stock = stock - %s WHERE id = %s AND stock >= %s",
                (body.quantity, body.productId, body.quantity),
            )
            if cur.rowcount == 0:
                raise ApiError(400, 2004, "商品库存不足")

            total_amount = Decimal(str(product["price"])) * body.quantity
            order_no = _generate_order_no()
            cur.execute(
                """
                INSERT INTO orders
                    (order_no, user_id, product_id, quantity, total_amount, status, request_id, address)
                VALUES (%s, %s, %s, %s, %s, 'CREATED', %s, %s)
                """,
                (
                    order_no,
                    user["userId"],
                    body.productId,
                    body.quantity,
                    total_amount,
                    body.requestId,
                    body.address,
                ),
            )
            cur.execute(_ORDER_SQL + " WHERE o.order_no = %s", (order_no,))
            data = _serialize(cur.fetchone())
            data["duplicated"] = False
            return ok(data, message="下单成功")
    except pymysql.err.IntegrityError:
        # 并发重复提交时由唯一索引兜底，回滚后读取已存在订单
        row = query_one(
            _ORDER_SQL + " WHERE o.user_id = %s AND o.request_id = %s",
            (user["userId"], body.requestId),
        )
        if row is None:
            raise
        data = _serialize(row)
        data["duplicated"] = True
        return ok(data, message="重复提交，返回已创建订单")


@router.get("")
def list_orders(
    status: str = Query(default=""),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1, le=50),
    user: dict = Depends(require_user),
):
    """查询当前用户订单，支持按状态筛选。"""
    if status and status not in VALID_STATUS:
        raise ApiError(400, 3003, f"非法的订单状态：{status}")

    where = "WHERE o.user_id = %s"
    args: list = [user["userId"]]
    if status:
        where += " AND o.status = %s"
        args.append(status)

    total_row = query_one(f"SELECT COUNT(*) AS total FROM orders o {where}", args)
    rows = query_all(
        _ORDER_SQL + f" {where} ORDER BY o.id DESC LIMIT %s OFFSET %s",
        [*args, size, (page - 1) * size],
    )
    return ok(
        {
            "total": total_row["total"],
            "page": page,
            "size": size,
            "list": [_serialize(row) for row in rows],
        }
    )


@router.get("/{order_no}")
def get_order(order_no: str, user: dict = Depends(require_user)):
    row = _find_order(order_no)
    if row["user_id"] != user["userId"]:
        raise ApiError(403, 3002, "无权查看他人订单")
    return ok(_serialize(row))


@router.put("/{order_no}/status")
def update_order_status(
    order_no: str,
    body: OrderStatusRequest,
    user: dict = Depends(require_user),
):
    """修改订单状态，按状态机校验；取消订单时回补库存。"""
    if body.status not in VALID_STATUS:
        raise ApiError(400, 3003, f"非法的订单状态：{body.status}")

    with transaction() as cur:
        cur.execute(
            "SELECT id, user_id, product_id, quantity, status FROM orders WHERE order_no = %s FOR UPDATE",
            (order_no,),
        )
        order = cur.fetchone()
        if order is None:
            raise ApiError(404, 3001, "订单不存在")
        if order["user_id"] != user["userId"]:
            raise ApiError(403, 3002, "无权操作他人订单")

        current = order["status"]
        if body.status not in TRANSITIONS[current]:
            raise ApiError(
                400,
                3004,
                f"订单状态不允许从 {current} 变更为 {body.status}",
            )

        cur.execute(
            "UPDATE orders SET status = %s WHERE id = %s",
            (body.status, order["id"]),
        )
        if body.status == "CANCELLED":
            cur.execute(
                "UPDATE products SET stock = stock + %s WHERE id = %s",
                (order["quantity"], order["product_id"]),
            )

    return ok(_serialize(_find_order(order_no)), message="状态更新成功")
