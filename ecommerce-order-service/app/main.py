from fastapi import FastAPI

from .errors import ok, register_exception_handlers
from .routers import auth, orders, products

app = FastAPI(
    title="电商订单系统",
    description="模拟电商核心交易流程：登录、商品查询、下单、订单查询与状态流转。",
    version="1.0.0",
)
register_exception_handlers(app)

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(orders.router)


@app.get("/health", tags=["系统"])
def health():
    return ok({"status": "UP"})


@app.get("/", tags=["系统"])
def index():
    return ok(
        {
            "service": "ecommerce-order-service",
            "docs": "/docs",
            "endpoints": [
                "POST /api/auth/login",
                "GET /api/products",
                "GET /api/products/{id}",
                "POST /api/orders",
                "GET /api/orders",
                "GET /api/orders/{orderNo}",
                "PUT /api/orders/{orderNo}/status",
            ],
        }
    )
