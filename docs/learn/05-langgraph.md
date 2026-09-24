# LangChain 接模型、LangGraph 编排计划

先记住：**模型只准产出工具调用，不准直接改图。** LangGraph 把「规划」和「校验」分成两个节点。

## 图长什么样

`backend/app/agent/graph.py`：

```text
START → plan → verify → END
```

- `plan`：`planner().ainvoke(系统提示 + 用户目标)`，把 `tool_calls` 收成 `[{tool, params}, ...]`
- `verify`：`validate(plan)`。未知工具、参数不合法、成环 → 清空计划，返回中文原因
- `run()` 只返回「要对用户说的话」和「尚未执行的计划」

系统提示里写死了图层 vs 选区、哪些事用哪个工具、最多 8 步。画布摘要通过 `{context}` 注入，模型靠这份上下文补参数，而不是再问一遍。

## 规划模型怎么接

`backend/app/agent/llm.py`：

- 用 `ChatOpenAI` + DashScope 的 **OpenAI 兼容** 地址（`/compatible-mode/v1`）
- `bind_tools` 绑定 `SPECS` 转成的 function schema
- `agent_hidden` 字段（遮罩、素材 id）从 schema 里抠掉，不让模型乱填
- 没配 `DASHSCOPE_API_KEY` 时抛 `PlannerUnavailable`（mock 出图仍可用，对话规划不行）

图像编辑仍走 `ImageProvider` 原生接口，和规划模型不是一条 SDK。

## 执行不在这张图里

LangGraph 在这里 **只做到计划落地**。真正跑工具是用户确认之后，由 ARQ Worker 按步骤依赖执行。多步计划会先让用户看「将按以下步骤执行：…确认后开始。」见 `spoken()` 和 `needs_confirm()`。

这和「LangGraph 里直接 ToolNode 调工具」的示例不同：本仓库把人机确认和队列执行留在图外面，面试时要能讲清。

## 动手

1. 读 `_SYSTEM` 里「局部改色用 `replace_region`」那几条，再对照工具注册表。
2. 读 `_verify`，想一个模型胡编工具名时用户会看到什么。
3. mock 下没有 Key：规划接口应失败或不可用，但按钮修图仍可走注册表。

## 面试一句话

LangChain 负责对话和 function calling；LangGraph 负责把规划与校验做成可测的状态图。副作用（改像素）放在图外，经队列执行。
