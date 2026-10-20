import uuid


def unique_request_id(prefix: str = "auto") -> str:
    """生成唯一幂等请求号，避免用例之间因重复提交相互影响。"""
    return f"{prefix}-{uuid.uuid4().hex}"


def order_payload(product_id: int = 1, quantity: int = 1, **overrides) -> dict:
    payload = {
        "productId": product_id,
        "quantity": quantity,
        "address": "广东省深圳市南山区科技园 1 号",
        "requestId": unique_request_id(),
    }
    payload.update(overrides)
    return payload
