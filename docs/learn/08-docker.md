# Docker 多阶段构建与 compose profile

先记住：**不带 profile 只起中间件。** 应用容器要显式 `--profile full` 或 `deploy`。所以只 `docker compose up -d` 时，`7302` 是空的。

## 多阶段镜像

根目录 `Dockerfile`：

```text
阶段 frontend   node:22-alpine → npm ci → npm run build → dist
阶段 运行时      python:3.13-slim + uv
                uv sync --frozen --all-extras --no-dev
                COPY 后端
                COPY --from=frontend dist → /app/frontend/dist
```

前端打进后端镜像后，`main.py` 发现 `frontend/dist` 存在就 `StaticFiles` 挂到 `/`。浏览器只访问 `7302`，API 和 SPA 同源，Cookie 与 SSE 都简单。

开发时不要走这套：Vite 在 `7301`，通过 proxy 打到 API。

## Compose profile

`docker-compose.yml`：

| 服务 | 默认 | `full` / `deploy` |
| --- | --- | --- |
| postgres / redis / minio | 起 | 起 |
| migrate（`alembic upgrade head`，跑完退出） | 否 | 是 |
| app（Uvicorn `:7302`） | 否 | 是 |
| worker（ARQ） | 否 | 是 |

`x-app-env` 锚点给容器内主机名（`postgres`、`redis`、`minio`）。宿主机端口是 `7311` / `7312` / `7313`，给本机 `uv run` 用。

`migrate` 设 `restart: "no"`，且 `app` / `worker` `depends_on: migrate: service_completed_successfully`，避免没建表就接流量。

`cv_models` 卷缓存抠图模型，避免每次构建重下。

一键脚本 `up.cmd` / `up.sh` 等价于：

```bash
docker compose --profile full up -d --build
```

生产：`--profile deploy`，并改 `JWT_SECRET`、`S3_PUBLIC_ENDPOINT`。

## 动手

1. 只执行 `docker compose up -d`，确认 `127.0.0.1:7311` 有库、`7302` 无站点。
2. 再 `--profile full`，看 `migrate` 退出码 0 后 app 才 healthy。
3. 读 Dockerfile 两段 `FROM`，说出为什么最终镜像里没有 `node_modules`。

## 常见误区

- 以为 `IMAGE_PROVIDER=mock` 可以不跑 Compose。mock 只替代模型。
- 生产把 `S3_ENDPOINT` 配成容器内 `http://minio:9000` 给浏览器用。浏览器打不开这个主机名，要用 `S3_PUBLIC_ENDPOINT`。
- 在 Windows 上用 `localhost:7302`。优先 `127.0.0.1`。

## 面试一句话

多阶段构建把 SPA 打进 API 镜像，用同源省掉 CORS；Compose profile 把「仅中间件」和「整站」分开，开发机不必默认拉起应用容器。
