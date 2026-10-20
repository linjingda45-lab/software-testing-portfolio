# 数字内容管理系统

项目二：基于 Java 17 + Spring Boot 2.7 + JdbcTemplate + MySQL 的数字内容管理后台，覆盖登录、内容新增、修改、条件查询、内容状态管理、任务状态管理与数据一致性验证。

## 接口

| 方法 | 路径 | 说明 | 是否需要登录 |
| --- | --- | --- | --- |
| POST | `/api/auth/login` | 登录 | 否 |
| POST | `/api/contents` | 新增内容（自动生成一条待处理任务） | 是 |
| GET | `/api/contents` | 条件查询（status/contentType/keyword/page/size） | 是 |
| GET | `/api/contents/{id}` | 内容详情 | 是 |
| PUT | `/api/contents/{id}` | 修改内容（仅草稿/已驳回可改） | 是 |
| PUT | `/api/contents/{id}/status` | 修改内容状态 | 是 |
| GET | `/api/contents/{id}/tasks` | 查询内容的关联任务 | 是 |
| GET | `/api/tasks` | 任务列表（status/page/size） | 是 |
| PUT | `/api/tasks/{id}/status` | 修改任务状态 | 是 |
| GET | `/api/health` | 健康检查 | 否 |

## 状态机

内容状态：

```text
DRAFT -> PENDING -> PUBLISHED -> OFFLINE -> PENDING
                 -> REJECTED -> DRAFT
```

任务状态：

```text
PENDING -> RUNNING -> SUCCESS
                    -> FAILED
```

数据一致性规则：内容从 `PENDING` 发布时，关联的待处理任务自动置为 `SUCCESS`；内容被驳回时自动置为 `FAILED`。内容处于 `PENDING/PUBLISHED` 时不允许再编辑，必须先按状态机流转。

## 构建与启动

前置条件：MySQL 已启动，`content_manage` 库已初始化（可在项目根目录执行 `python scripts/init_databases.py`）。

```powershell
cd digital-content-system
mvn -DskipTests package
java -jar target\digital-content-system-1.0.0.jar
```

服务地址：<http://127.0.0.1:8082>，健康检查：<http://127.0.0.1:8082/api/health>。

数据库连接支持环境变量覆盖：`DB_HOST`、`DB_PORT`、`DB_USER`、`DB_PASSWORD`、`DB_NAME`。

## 功能测试

### Postman

导入 `postman/digital-content.postman_collection.json`，先执行「01 登录」自动写入 token，再按编号顺序执行。

- 正向链路：新增、修改、条件查询、提交审核、发布、任务查询、任务更新
- 异常场景：未登录 401、非法状态流转、必填参数校验

执行结果：**11 个请求 / 22 条断言 / 0 失败**。

也可以使用 Newman 在命令行执行：

```powershell
npx --yes newman run postman\digital-content.postman_collection.json -r cli
```

### SQL 数据一致性核对

接口操作后执行 `sql/verify.sql`，重点看：

- 内容状态分布、任务状态分布
- 内容与其关联任务的状态明细
- 异常项：已发布内容仍存在待处理/执行中的任务
- 异常项：待审核内容没有待处理任务

### 测试账号

| 用户名 | 密码 | 角色 |
| --- | --- | --- |
| admin | 123456 | ADMIN |
| editor | 123456 | EDITOR |

> 仅用于本地演示。

## 数据库

库名 `content_manage`，三张表：

- `sys_user`：系统用户
- `content`：内容（标题、类型、作者、正文、状态）
- `content_task`：内容处理任务（类型、状态）

## 代码结构

```text
digital-content-system/
├── src/main/java/com/example/content/
│   ├── ContentManageApplication.java
│   ├── common/          # 统一响应、异常处理、登录拦截器
│   ├── controller/      # 登录、内容、任务、健康检查接口
│   ├── dto/             # 请求参数与校验注解
│   ├── dao/             # JdbcTemplate 数据访问
│   ├── model/           # 实体与分页结果
│   └── service/         # 业务规则与状态机
├── src/main/resources/application.yml
├── sql/init.sql         # 建表与初始数据
├── sql/verify.sql       # 数据一致性核对 SQL
└── postman/             # Postman 功能测试集合
```
