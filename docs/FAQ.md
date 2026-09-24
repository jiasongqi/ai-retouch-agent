# 答疑

## 打开页面

**为什么 7301 可以、7302 不行？**  
`7301` 是 Vite 开发服务器。`7302` 是 Docker 一键包（前端 + API 同源）。没跑 `up.cmd` / `docker compose --profile full` 时 7302 没有进程。

**Windows 上 `localhost` 打不开？**  
用 `http://127.0.0.1:7301/`。本机 `localhost` 有时走 IPv6。

**落地页能看、登录 / 出图不行？**  
工作台要 API。先看 `http://127.0.0.1:7302/api/health`。Postgres `:7311`、Redis `:7312`、MinIO `:7313` 都要起来。

## 环境

**必须装 Docker Desktop 吗？**  
本地中间件默认靠 Compose。也可以把 Postgres / Redis / 对象存储换到云上，改 `.env` 指向它们。没有数据库和 Redis 时后端起不来：会话、任务队列、资产都写在这上面。`IMAGE_PROVIDER=mock` 只跳过模型，不跳过存储。

**必须 Python 3.13 吗？**  
开发模式按仓库要求用 3.13 + `uv`。只体验产品时用 Docker 一键包即可。

**npm 很慢 / 装不上？**  
`npm install --registry=https://registry.npmmirror.com`。`uv sync` 可用清华 PyPI 镜像。

## 模型

**不配 Key 能做什么？**  
默认 mock：生成、修图、导出链路都可以点，图是占位图。接百炼：`.env` 里 `IMAGE_PROVIDER=dashscope` 并填写 `DASHSCOPE_API_KEY`。

**规划模型和出图模型是一个吗？**  
不是。`PLANNER_MODEL` 默认 `qwen-plus`，负责拆步骤；出图 / 图像编辑走 Provider。改规划模型不会自动改图像模型。

## 安全

**哪些东西不能进 Git？**  
`.env`、API Key、数据库连接串、账号密码、`node_modules`。仓库只跟踪 `.env.example`（本地占位，无密钥）。

**生产环境最少改什么？**  
`JWT_SECRET`（例如 `openssl rand -hex 32`）和 `S3_PUBLIC_ENDPOINT`（浏览器能访问到的对象存储地址）。

## 部署

**可以放到云服务器吗？**  
可以。2 核 4G 左右的 Linux + Docker Compose `--profile deploy` 即可。安全组放开 `7302`（站点）和对象存储端口（默认 `7313`）。不要把修图库建在别人的业务数据库里。

**一键脚本失败？**  
先确认 Docker Desktop 或远程 Docker 守护进程已启动，再看 Compose 日志：`docker compose --profile full logs --tail 200`。

## 开发

**加工具要改哪些文件？**  
见 [文字教程 §5](TUTORIAL.md#5-加一个工具)。

**测试要花钱调模型吗？**  
`cd backend && uv run pytest` 走 mock。前端落地页：`cd frontend && npm run test:e2e`。工作台主路径需要 API 已启动：`npm run test:e2e:full`。
