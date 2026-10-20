from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1, max_length=50)


class OrderCreateRequest(BaseModel):
    productId: int = Field(..., gt=0)
    quantity: int = Field(..., ge=1, le=99)
    address: str = Field(..., min_length=1, max_length=200)
    requestId: str = Field(..., min_length=8, max_length=64, description="幂等请求号，防重复提交")


class OrderStatusRequest(BaseModel):
    status: str = Field(..., min_length=1, max_length=20)
