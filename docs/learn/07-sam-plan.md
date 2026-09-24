# SAM 点选、语义拆层、计划校验与拓扑排序

这三项经常被问在一起：选区怎么来、图层怎么拆、多步计划怎么保证能跑。

## 1. SAM 点选

`backend/app/edits/segment.py`

- 用户点的是 **归一化坐标**（0~1），和视口缩放无关
- 同一张图的 embedding 只算一次，放 LRU（最多 4 张）；点击只跑 decoder
- `warm_embedding` 在进入点选模式时预热，避免第一次点击卡顿
- `matting_provider=corner` 时用圆圈遮罩，测试和没装模型时也能点
- 失败且不是强制 rembg 时，回退圆圈，产品不至于空白

点选得到的是 **遮罩图**，不是新图层。笔刷涂抹是另一条选区路径，最后同样变成 mask 交给消除 / 替换 / 提升为层。

## 2. 语义拆层

`backend/app/edits/split.py` + `layers.py`

拆层不是「复制一张图」。大致是：

1. 用遮罩 `cut_object` 抠出主体 PNG 和包围盒
2. `fill_background` 把原位置挖掉并修补，背景层不再含主体
3. 文档里用 `background` / `subject` 等 id 替换原来的 `base` 底图
4. `promote_object_to_layer` 把当前选区再提成独立层，并修背景，避免重影

文字层走 OCR（RapidOCR），默认拆层可以不拆字；用户明确要求才 `include_text`。图层文档改完，像素合成由渲染环节按文档执行。

## 3. 计划校验与拓扑排序

`backend/app/agent/plan.py`

模型给的是「工具名 + 参数」列表。服务端还要：

1. `spec_of`：工具必须已注册
2. `tools.validate`：参数符合 Pydantic
3. `assemble`：补 `s1`、`s2`…；没写 `depends_on` 时 **默认依赖前一步**
4. 依赖必须指向存在的步骤
5. `_cyclic`：Kahn 拓扑，入度为 0 的入队，若没扫完全部节点就是有环
6. 最多 `MAX_STEPS = 8`

执行时 `ready()` 找出依赖都已 `succeeded` 的步骤；某步 `failed` / `canceled` 则下游不再开跑。`needs_confirm`：多于 1 步先问用户。

## 三者怎么拼

用户点了鞋子 → SAM 出遮罩 → 说「把这个单独成层再换背景」→ 规划成 `promote_object_to_layer` → `replace_background`，第二步默认依赖第一步。校验过了才进队列。

不要让模型「猜选区准不准」：画布摘要里已有选区就直接用。系统提示把这条写死了。

## 动手

1. 点选同一物体两次，想 embedding 缓存命中会发生什么。
2. 在 `plan.py` 里把两步互相 `depends_on`，看 `PlanError` 文案。
3. 拆层后看文档里是否还剩 `base`，还是变成 `subject` + `background`。

## 面试一句话

选区是像素掩码，图层是文档节点，计划是带依赖的 DAG。模型只提议，服务端校验和拓扑之后才能执行。
