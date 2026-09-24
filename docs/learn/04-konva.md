# react-konva 图层文档与视口

先记住两套坐标：

- **图层文档**（`LayerDocument`）是真相：每层位置、缩放、显隐、像素资源。导出按文档合成。
- **视口**（`useCanvasView`）只是观察：画布平移缩放。适应窗口、滚轮放大都不改导出结果。

## 数据在哪

后端：`backend/app/layers.py`

- `Layer`：id、kind（image / text / shape）、transform、opacity、visible
- `LayerDocument`：画布宽高 + 图层列表
- `resolve_layer`：可用 id 或中文名（「物体2」），未指定则取最上层可见图像

前端：`frontend/src/api/sessions.ts` 拉同一份文档；`CanvasStage.tsx` 用 `react-konva` 画出来。

视口状态在 `frontend/src/stores/canvasView.ts`（zustand）。注释写得很直：

> 观察倍率与位移，只影响编辑器视图，不参与导出。图层缩放另存于 LayerDocument。

按钮缩放走缓动 `glide`；手势拖拽直接跟手。`FIT_RATIO = 0.92` 留边，避免贴边。

## 编辑器里还能看到什么

`CanvasStage.tsx` 同一块 Stage 上叠了：

- 各图层 `KonvaImage` / `Text`
- 选区 overlay（点选 / 笔刷）
- Transformer（拖、缩放某层 → 回调改文档，不是只改视口）
- 裁切框、前后对比滑杆、调色预览滤镜

`useHeldCanvas` 在切图时短暂留住上一帧，避免闪白。滤镜预览按较低像素比缓存，滑杆才能跟手。

## 和 Agent 的关系

自然语言修图改的是 **文档**（某层 `transform`、某层像素 asset），不是你在屏幕上滚了多少。所以「放大看看」不会变成一次 `scale_layer`；你按住图层拖动才会。

## 动手

1. 打开编辑器，滚轮放大，再导出：导出图尺寸不变。
2. 选中图层拖动，看右侧图层面板坐标变化，再导出：位置变了。
3. 读 `resolve_layer`，对一下 Agent 说「背景」时怎么命中 `background` 层。

## 面试一句话

画布是文档加视口。文档可序列化、可导出、可被工具改；视口是编辑器交互状态，不要写进业务数据。
