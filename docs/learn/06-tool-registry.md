# 统一工具注册表

先记住：**26 个工具只登记一次。** 界面按钮、Agent function calling、参数校验、执行外壳都读 `SPECS`。

## 一个工具有什么

`backend/app/tools/base.py` 的 `ToolSpec`：

| 字段 | 作用 |
| --- | --- |
| `name` / `label` / `description` | 机器名、界面文案、给模型看的说明 |
| `params` | Pydantic 模型，同时生成 JSON Schema 和运行时校验 |
| `handler` | 真正干活；不管任务状态机 |
| `queued` | 像素工具进 ARQ；只改文档的可同步 |
| `agent_hidden` | 遮罩、素材 id 等由服务端填，不暴露给模型 |
| `detail` | 按参数细化说法，例如「水平翻转」 |

`LayerRef` 和 `MaskRef` 拆开：改哪一层 vs 改哪一块。遮罩字段在 `HIDDEN_MASK` 里，模型填了也会被服务端覆盖。

## 登记处

`backend/app/tools/__init__.py` 的 `SPECS` 元组。`spec_of(name)` 给执行用，`label_of` 给对话和进度条用。

规划侧：`llm.py` 把每个 spec 转成 OpenAI function，增减工具不必改绑定代码。

执行侧：`services/tools.py` 的 `validate()` 用同一套 `params.model_validate`。界面点按钮和 Agent 出计划，过的是同一道关。

## 加一个工具的最短路径

1. 新文件或现有分类文件里写 `ToolSpec`
2. 追加进 `SPECS`
3. Agent 要主动选用 → 补 `graph.py` 系统提示
4. 前端若有独立按钮 → 调同一 submit API，补文案
5. 单测；像素类再进 `app.eval`

不要在某个 Vue/React 页面里另写一套「去背景」HTTP 接口。

## 动手

1. 数一遍 `SPECS` 是否 26 个，和 README 工具清单对照。
2. 打开 `APPLY_STUDIO_FINISH` 或 `PREPARE_PLATFORM_EXPORT`，看 `params` 和 `handler` 怎么分。
3. 假设要加「加圆角」，列出你要改的文件，不要先写代码。

## 面试一句话

注册表是 Agent 产品的单一事实来源。Schema、校验、执行、文案同源，才能避免「按钮能做、对话却调不到」。
