# ARQ + Redis Pub/Sub + SSE 实时进度

先记住：**API 进程不跑像素和模型。** 它只写入 `ToolRun`、投递 ARQ 任务；Worker 执行；进度经 Redis 频道发布；浏览器用 SSE 订阅。

## 一条任务怎么走

```text
前端 POST 修图
  → services/tools.submit  落库 ToolRun（queued）
  → queue.enqueue("run_tool", run_id)     任务 ID = run_id，避免重复执行
  → Worker app.tasks.tools.run_tool
  → tools.execute  调注册表 handler，回调里 publish 进度
  → Redis channel  run:{run_id}
  → GET /events/runs/{run_id}  SSE 推给浏览器
```

对照代码：

| 角色 | 文件 |
| --- | --- |
| 入队 | `backend/app/queue.py` |
| Worker 配置 | `backend/app/worker.py` |
| 真正执行 | `backend/app/tasks/tools.py` |
| 发布 / 订阅 | `backend/app/events.py` |
| SSE 路由 | `backend/app/routers/events.py` |
| 前端合并 SSE 与快照 | `frontend/src/hooks/useRun.ts` |

`enqueue` 用 `_job_id=str(run_id)`：同一 run 被重投或 Worker 重启，ARQ 不会再跑一遍。Worker 里若 `run.status.is_terminal` 直接返回，防止二次扣费。

## SSE 几个容易漏的细节

1. **先订阅再读快照。** 否则任务在两步之间结束，连接会空等。见 `stream_run`。
2. 空闲超时产出 `None`，路由写成 `: ping\n\n` 心跳，避免代理掐连接。
3. 结束状态（成功 / 失败 / 取消）后立刻断开。前端 `isTerminal` 后不再挂 EventSource，避免反复打快照。
4. SSE 挂在 `/events` 而不是 `/api`，注释写明方便反向代理单独关缓冲。响应头有 `X-Accel-Buffering: no`。
5. 最长 600 秒主动断开，客户端重连会再收一份快照，不丢最终状态。

前端 `useRun`：SSE 管实时 `progress` / `status`；TanStack Query 管刷新后的候选图和结果。切换 `runId` 时丢掉旧连接的残留帧。

## 为什么不用 API 里 `await` 模型

修图可能几十秒。占着 Uvicorn worker 会拖垮健康检查和别的请求。队列还能水平加 Worker（`max_jobs = 4`，`job_timeout = 300`）。

纯改图层文档、不必算像素的工具可以 `queued=False` 当场执行，不必每一步都进 ARQ。见 `ToolSpec.queued`。

## 动手

1. 开发模式开两个终端：Uvicorn 和 `uv run arq app.worker.WorkerSettings`。只开 API、不开 Worker，任务会一直 queued。
2. 浏览器开发者工具看 `EventSource`：`/events/runs/...` 的 `data:` 帧。
3. 读 `useRun`，说出「刷新页面进度为什么还能对上」。

## 面试一句话

长任务进队列；Pub/Sub 扇出进度；SSE 是浏览器能用的单向流。快照接口负责恢复，SSE 负责跟手。
