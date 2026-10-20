from fastapi import APIRouter, Query

from ..db import query_all, query_one
from ..errors import ApiError, ok

router = APIRouter(prefix="/api/products", tags=["商品"])

_PRODUCT_FIELDS = "id, name, price, stock, category, status, created_at"


@router.get("")
def list_products(
    keyword: str = Query(default="", max_length=50),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1, le=50),
):
    """在售商品分页查询，支持按名称模糊搜索。"""
    where = "WHERE status = 1"
    args: list = []
    if keyword:
        where += " AND name LIKE %s"
        args.append(f"%{keyword}%")

    total_row = query_one(f"SELECT COUNT(*) AS total FROM products {where}", args)
    rows = query_all(
        f"SELECT {_PRODUCT_FIELDS} FROM products {where} ORDER BY id LIMIT %s OFFSET %s",
        [*args, size, (page - 1) * size],
    )
    return ok({"total": total_row["total"], "page": page, "size": size, "list": rows})


@router.get("/{product_id}")
def get_product(product_id: int):
    product = query_one(
        f"SELECT {_PRODUCT_FIELDS} FROM products WHERE id = %s AND status = 1",
        (product_id,),
    )
    if product is None:
        raise ApiError(404, 2001, "商品不存在或已下架")
    return ok(product)
