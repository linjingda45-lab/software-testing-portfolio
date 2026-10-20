# 电商订单系统（被测系统）

项目一的被测服务，模拟电商核心交易流程。使用 FastAPI + MySQL 实现，供 `api-test-framework` 做接口自动化测试。

## 功能

- 用户登录，返回访问令牌；后续下单、查单、改状态需携带 `Authorization: Bearer <token>`
- 商品列表、关键字搜索、分页、商品详情
- 创建订单：事务内校验商品、校验库存、扣减库存、写入订单
- 幂等下单：同一用户相同 `requestId` 重复提交只生成一笔订单
- 查询订单详情、订单列表（按状态筛选）
- 修改订单状态：`CREATED -> PAID -> SHIPPED -> COMPLETED`，`CREATED -> CANCELLED`
- 取消订单自动回补库存
- 越权校验：只能查看和操作自己的订单

## 接口

| 方法 | 路径 | 说明 | 是否需要登录 |
| --- | --- | --- | --- |
| POST | `/api/auth/login` | 登录 | 否 |
| GET | `/api/auth/profile` | 当前登录信息 | 是 |
| GET | `/api/products` | 商品列表（keyword/page/size） | 否 |
| GET | `/api/products/{id}` | 商品详情 | 否 |
| POST | `/api/orders` | 创建订单 | 是 |
| GET | `/api/orders` | 订单列表（status/page/size） | 是 |
| GET | `/api/orders/{orderNo}` | 订单详情 | 是 |
| PUT | `/api/orders/{orderNo}/status` | 修改订单状态 | 是 |
| GET | `/health` | 健康检查 | 否 |

启动后访问 <http://127.0.0.1:8081/docs> 查看 Swagger 文档并直接调试。

## 启动

```powershell
cd ecommerce-order-service
python -m uvicorn app.main:app --host 127.0.0.1 --port 8081
```

首次运行先初始化数据库：

```powershell
python ..\scripts\init_databases.py
```

## 数据库

库名 `ecommerce_test`，三张表：

- `users`：用户
- `products`：商品（含库存、上下架状态）
- `orders`：订单（含幂等唯一键 `uk_user_request(user_id, request_id)`）

订单状态机：

```text
CREATED -> PAID -> SHIPPED -> COMPLETED
CREATED -> CANCELLED（回补库存）
```

数据库连接支持环境变量覆盖：`DB_HOST`、`DB_PORT`、`DB_USER`、`DB_PASSWORD`、`DB_NAME`。

## 关键实现

- 下单使用数据库事务 + `SELECT ... FOR UPDATE`，库存扣减与订单写入同事务，避免超卖
- 幂等键唯一索引兜底并发重复提交，冲突时回滚并返回已存在订单
- 统一响应结构 `{code, message, data}`；参数错误返回 4001，业务错误码按模块划分
- 订单状态流转集中定义在 `TRANSITIONS` 中，非法跳转返回 3004

## 目录

```text
ecommerce-order-service/
├── app/
│   ├── main.py            # 应用入口、异常处理器注册
│   ├── config.py          # 数据库配置（支持环境变量）
│   ├── db.py              # PyMySQL 连接、事务上下文
│   ├── security.py        # 登录与令牌校验
│   ├── schemas.py         # 请求参数模型
│   └── routers/           # 登录、商品、订单接口
├── sql/init.sql           # 建表与初始数据
└── requirements.txt
```
