# FastAPI + SQLAlchemy + JWT Cookie

先记住：**登录态放在 httpOnly Cookie 里，路由用依赖注入拿当前用户。** 浏览器不会、也不该把 token 塞进 `Authorization` 头。SSE 也因此能带上同一份 Cookie。

## 分层怎么走

```text
routers/auth.py     只做 HTTP：设 Cookie、返回 UserOut
    ↓
deps.py             current_user：读 Cookie → 解 JWT → 查库
    ↓
services/auth.py    注册、校验密码
    ↓
models/user.py      SQLAlchemy 映射
db.py               异步引擎 + 一次请求一个 Session
```

对照代码：

- Cookie 名与 JWT 签发 / 解析：`backend/app/security.py`
- 登录、注册、登出、`/me`：`backend/app/routers/auth.py`
- `CurrentUser` 依赖：`backend/app/deps.py`
- 异步 Session：`backend/app/db.py`
- 用户表：`backend/app/models/user.py`，主键与时间戳在 `models/base.py`
- 配置：`backend/app/config.py` 的 `jwt_secret`、`jwt_ttl_hours`

登录成功后 `set_cookie(SESSION_COOKIE, issue_token(user.id), httponly=True, samesite="lax")`。生产环境再开 `secure`。前端 `fetch` 默认带同源 Cookie，`frontend/src/api/client.ts` 没有手写 token。

开发时 Vite 把 `/api` 和 `/events` 代理到 `7302`，前后端看起来同源，Cookie 和 SSE 都不用跨域配置。见 `frontend/vite.config.ts`。

## 为什么不用 Header 里的 Bearer

修图进度是 `EventSource`。浏览器的 EventSource **不能自定义 Header**。token 放 Cookie 后，SSE 和普通 REST 走同一套登录态。这和「JWT 一定放 Authorization」的教程写法不同，是这个产品自己的约束。

## 数据库侧要点

- SQLAlchemy 2 声明式：`Mapped[...]` + `mapped_column`
- 异步：`create_async_engine` + `async_sessionmaker`，驱动 `asyncpg`
- `get_session` 用 `yield`，请求结束自动关闭
- UUID 主键、`timestamptz`，枚举存 VARCHAR 而不是 Postgres 原生 ENUM（增删值不用 `ALTER TYPE`）
- 表结构变更走 Alembic，不在运行时 `create_all`

## 动手

1. 读 `issue_token` / `read_token`，看 `sub` 和 `exp` 怎么写。
2. 给一个需要登录的路由加上 `user: CurrentUser`，体会「路由不自己解 token」。
3. 打开 `/api/docs`，对 `/api/auth/login` 试一次，再看响应头 `Set-Cookie`。

## 面试一句话

登录签发 JWT 写入 httpOnly Cookie；业务路由只声明 `CurrentUser`。SSE 无法带自定义头，所以不能把鉴权只放在 `Authorization`。
