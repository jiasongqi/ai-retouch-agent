# 学习笔记

对着本仓库代码学，不是空讲概念。建议顺序：

| # | 笔记 | 先记住 |
| --- | --- | --- |
| 1 | [FastAPI + SQLAlchemy + JWT Cookie](01-fastapi-sqlalchemy-jwt.md) | 鉴权走 httpOnly Cookie，接口不自己查用户 |
| 2 | [Provider 抽象](02-provider.md) | 工具只认协议，mock / 真模型一行配置切换 |
| 3 | [ARQ + Redis + SSE](03-arq-sse.md) | API 只投递，Worker 干活，进度推到浏览器 |
| 4 | [react-konva 图层与视口](04-konva.md) | 图层文档是数据，视口缩放不参与导出 |
| 5 | [LangChain / LangGraph](05-langgraph.md) | 模型只规划，校验节点拦住再动手 |
| 6 | [统一工具注册表](06-tool-registry.md) | UI 按钮和 Agent 共用同一份 SPECS |
| 7 | [SAM、拆层、计划校验](07-sam-plan.md) | 选区 / 图层 / 步骤依赖是三套东西 |
| 8 | [Docker 多阶段与 profile](08-docker.md) | 默认只起中间件；full / deploy 才起应用 |

走通产品后再读也可以，入口仍是 [文字教程](../TUTORIAL.md)。
