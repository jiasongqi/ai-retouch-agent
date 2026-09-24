# Provider 抽象：一行配置切换 mock / 真模型

先记住：**工具和路由从来不 `import` 具体模型厂商。** 它们只调用 `ImageProvider` 协议。`.env` 里 `IMAGE_PROVIDER=mock` 或 `dashscope`，工厂函数返回不同实现。

## 结构

```text
providers/base.py      Protocol：generate / edit / upscale
providers/mock.py      本地占位图，提示词哈希决定构图
providers/dashscope.py 阿里云百炼真实调用
providers/__init__.py  get_image_provider() 按配置选实现
```

`GenerateRequest` / `EditRequest` 是不可变 dataclass，图片以 **原始字节** 传入，不把 URL 或 SDK 对象泄漏给调用方。进度通过可选的 `on_progress(percent, stage)` 回调往上抛，队列和 SSE 才能显示「生成第 2 / 4 张」。

工厂用 `@lru_cache`，进程内只建一次。未知名字抛 `ProviderError`。

配置在 `backend/app/config.py`：

- `image_provider`：`mock` | `dashscope`
- `dashscope_api_key`、出图模型、编辑模型
- `planner_model` 是另一路（规划用文本模型），不要和出图模型混为一谈

## 为什么要 mock

- pytest 和本地演示不花钱、不依赖外网
- 把「链路通不通」和「模型好不好」拆开
- 同一套工具、同一套进度、同一套画布更新

`MockImageProvider` 还会 `asyncio.sleep` 模拟耗时，方便你观察进度条。同一提示词哈希稳定，回归时可对比。

## 动手

1. 默认不改 `.env`，走一遍生成 → 编辑器。图是色块占位。
2. 有 Key 时改 `IMAGE_PROVIDER=dashscope`，**不要改任何 Python 调用点**，再生成一次。
3. 读 `get_image_provider()`，想：再加一个厂商要改哪一行。

## 常见误区

- 以为 mock 可以不启动 Postgres / Redis。不行。mock 只跳过模型。
- 在某个 Tool 里直接调 DashScope SDK。下次换厂商要改遍工具。
- 规划和出图共用一个模型名。本仓库里规划走 OpenAI 兼容接口，出图走厂商原生接口。

## 面试一句话

Provider 是端口，Tool 是用例。配置选择适配器，测试用假适配器，生产用真适配器。
