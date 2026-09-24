# 文字教程

跟着本仓库把「一句话出可上架商品图」跑通，再顺着代码看请求怎么走。启动命令以根目录 [README](../README.md#快速开始) 为准。

## 1. 你在学什么

这不是聊天框里塞一张图。用户说一句自然语言，系统拆成可校验的工具计划，由 Worker 执行，进度经 SSE 推到 Konva 画布。UI 按钮和 Agent 调用的是同一份 `ToolRegistry`。

默认 `IMAGE_PROVIDER=mock`，不配 API Key 也能走完全流程。接百炼后把同一套工具切到真实模型。

## 2. 启动

- 有 Docker Desktop：根目录执行 `up.cmd`（Windows）或 `./up.sh`，打开 [http://127.0.0.1:7302](http://127.0.0.1:7302)
- 只看落地页：前端 `npm run dev`，打开 [http://127.0.0.1:7301](http://127.0.0.1:7301)（Windows 不要用 `localhost`）
- 开发模式：Compose 只起 Postgres / Redis / MinIO，再分别起 FastAPI、ARQ Worker、Vite。细节见 README。

健康检查：`GET http://127.0.0.1:7302/api/health` 三个字段都是 `ok`。

## 3. 跟着点一遍

1. 注册登录（JWT Cookie）。
2. 落地页或创作页输入「白底主图，主体居中」，生成 4 张候选。
3. 选一张进入编辑器：左侧对话，中间画布，右侧图层。
4. 说「去背景，补接触阴影，再出淘宝主图」。确认计划后看步骤进度。
5. 导出页用场景库、Brand Kit 或「一键套图」，拿到白底 + 场景 + 卖点 + 9:16。

观察这几件事：

- 计划会先出现在对话里，可确认 / 单步重试 / 取消，不是模型一说就执行。
- 图层和选区是两套东西：改哪一层用 `layer_id`，改哪一块用选区。
- 投放尺寸走 `prepare_delivery_sizes` / `prepare_platform_export`，不要用画布裁切硬砍主体。

## 4. 一次修图怎么走

```text
自然语言
  → LangGraph 规划 JSON 计划
  → 工具存在性 / 参数 / 依赖校验 + 拓扑排序
  → 用户确认（可单步重试 / 取消）
  → ARQ Worker 按依赖执行工具
  → Redis Pub/Sub + SSE 推进度
  → 画布更新图层与像素
```

对应代码：

| 环节 | 位置 |
| --- | --- |
| 规划提示与图 | `backend/app/agent/graph.py` |
| 计划校验 | `backend/app/agent/plan.py` |
| 工具注册 | `backend/app/tools/__init__.py` |
| 队列与进度 | `backend/app/tasks/`、SSE 路由 |
| 画布 | `frontend/src/components/editor/` |
| 上架能力 | `backend/app/listing/` |

## 5. 加一个工具

1. 在 `backend/app/tools/` 写 `ToolSpec`（名字、参数、执行函数）。
2. 登记进 `SPECS`。界面按钮和 Agent 会同时看见。
3. 若 Agent 需要主动选用，补 `graph.py` 里的系统提示。
4. 前端如需单独入口，加调用与文案（如 `ACTION_LABELS`）。
5. 补单测；涉及像素的再加 `app.eval` 回归。

## 6. 接下来读什么

- 简历怎么写：[RESUME.md](RESUME.md)
- 面试怎么答：[INTERVIEW.md](INTERVIEW.md)
- 启动与部署卡住了：[FAQ.md](FAQ.md)
