# 项目一：电商订单系统接口自动化测试框架

基于 Python + Requests + Pytest + Allure + MySQL 的接口自动化框架，被测系统为上一级目录中的 `ecommerce-order-service`。

## 目录结构

```text
api-test-framework/
├── config/settings.py       # 接口地址、数据库、测试账号配置
├── common/
│   ├── http_client.py       # Requests 封装：base_url、超时、日志、Allure 附件
│   ├── db_util.py           # MySQL 查询工具，用于数据一致性校验
│   └── data_factory.py      # 测试数据构造（唯一 requestId 等）
├── conftest.py              # 会话级登录、客户端、数据库 fixture；用例数据清理
├── testcases/
│   ├── test_login.py        # 登录与令牌异常
│   ├── test_product.py      # 商品查询、分页与边界
│   └── test_order.py        # 下单、幂等、库存、越权、状态流转、DB 校验
├── pytest.ini
├── run.ps1
└── requirements.txt
```

## 运行

前置条件：MySQL 与电商订单服务（8081）已启动，数据库已初始化。

```powershell
cd api-test-framework
python -m pytest
```

只跑冒烟用例：

```powershell
python -m pytest -m smoke
```

只跑回归用例：

```powershell
python -m pytest -m regression
```

生成 Allure 报告：

```powershell
.\run.ps1
```

`run.ps1` 会优先使用 PATH 中的 `allure`，否则读取 `ALLURE_HOME`（默认 `%USERPROFILE%\allure-cli\allure-2.29.0`）。也可以手动执行：

```powershell
allure generate reports/allure-results -o reports/allure-report --clean
allure open reports/allure-report
```

## 用例覆盖（共 41 条）

| 模块 | 用例数 | 覆盖点 |
| --- | --- | --- |
| 登录 | 7 | 正常登录、密码错误、用户不存在、缺少用户名/密码、空用户名、伪造令牌 |
| 商品 | 9 | 在售商品列表、关键字搜索、无匹配、分页、page=0、size 超限、详情、不存在、已下架 |
| 订单 | 25 | 正常下单、幂等重复提交、库存不足、超库存、商品不存在/下架、数量 0/负数/超上限、缺少地址/幂等号、未登录、订单详情、不存在、查看/操作他人订单、状态筛选、非法状态、取消回补库存、非法状态跳变、完整正向流转、未登录查询/改状态 |

## 框架设计要点

- **登录态复用**：`token`、`api` 为 session 级 fixture，只登录一次，避免每条用例重复登录。
- **数据工厂**：`unique_request_id()` 生成唯一幂等号，防止用例之间因重复提交互相影响。
- **数据隔离**：`clean_order_data` 在每条用例执行前后清理测试订单并还原商品库存，用例可重复执行。
- **接口 + 数据库双校验**：不仅断言响应，还用 `DBUtil` 查询订单表、商品库存表，验证接口结果真正落库。
- **Allure 附件**：`ApiClient` 自动把请求参数和响应写入报告，失败时可直接定位问题。
- **标记分层**：`smoke` 覆盖核心正向链路，`regression` 覆盖异常与边界，可按需选择执行范围。

## 配置

默认值见 `config/settings.py`，也可以通过环境变量覆盖：

| 环境变量 | 默认值 |
| --- | --- |
| `API_BASE_URL` | `http://127.0.0.1:8081` |
| `DB_HOST` | `127.0.0.1` |
| `DB_PORT` | `3307` |
| `DB_USER` | `tester` |
| `DB_PASSWORD` | `Test@123456` |
| `DB_NAME` | `ecommerce_test` |
