# Kodi 集成 DanmakuFlameMaster（DFM）评估报告

## 摘要
- 目标：在 Kodi（xbmc）中实现“视频播放中的弹幕显示”。现有将弹幕转 ASS 走 libass 渲染在 Android 上存在明显卡顿问题。
- 结论：优先采用 Android 专用集成（新增 DFM 弹幕视图层覆盖在视频之上），最小改动、效果稳定，避开 libass 滚动弹幕瓶颈。全平台统一方案需要重做渲染通路，复杂度显著更高。

## 现状与架构要点
- 字幕/覆盖层渲染：
  - `xbmc/cores/VideoPlayer/VideoRenderers/OverlayRenderer*.{h,cpp}` 负责将字幕（含 ASS/libass）转换为纹理/几何，由 GLES 渲染，与视频帧在 `RenderManager::Render()` 中组合。
- Android 视图层级：
  - `tools/android/packaging/xbmc/res/layout/activity_main.xml` 定义 `RelativeLayout id=VideoLayout` 作为容器。
  - 视频层：`XBMCVideoView.java.in`（SurfaceView，`setZOrderMediaOverlay(true)`，透明）用于 MediaCodec(Surface) 硬解输出。
  - GUI 层：`XBMCMainView.java.in`（SurfaceView，`setZOrderOnTop(true)`，透明）始终位于最上层用于 GUI。
  - JNI 管理：`CJNIXBMCVideoView`、`XBMCApp` 负责 Surface 创建/销毁、播放事件回调。
- 机会：在 `VideoLayout` 中插入一个新的 DFM 弹幕视图层（SurfaceView/TextureView），位于“视频层之上、GUI 层之下”，实现弹幕覆盖视频而不压住 GUI 控件。

## 方案 A：Android 专用集成（推荐）
### 技术路径
- 新增 `XBMCDanmakuView`（基于 DFM 的 `DanmakuView`/`DanmakuSurfaceView`）：
  - 作为独立 SurfaceView：`setZOrderMediaOverlay(true)`，`getHolder().setFormat(PixelFormat.TRANSPARENT)`。
  - 动态添加/移除：在 `VideoLayout` 中添加到视频层之后、GUI 层之前。
- JNI 封装与播放状态联动：
  - 新建 `CJNIXBMCDanmakuView`：提供 `add()/release()/prepare()/start()/pause()/resume()/seekTo()/setRect()`。
  - 在 `XBMCApp::OnPlayBackStarted/Paused/Stopped/OnSeek` 中调用对应 JNI 方法，保证生命周期与播放一致。
- 区域/缩放同步：
  - 参考 `CJNIXBMCVideoView::setSurfaceRect`，当 Kodi 计算出视频显示矩形时，同步调用弹幕视图 `setRect(left, top, right, bottom)`（UI 线程执行）。
- 数据解析：
  - 初始支持“同名弹幕文件”（如 `movie.mp4` → `movie.xml`），用 `BaseDanmakuParser` 解析；后续可对接在线接口（DanDanPlay/B站 API）。
- 依赖与构建（Gradle）：
  - `repositories { mavenCentral() }`（必要时启用 JitPack）。
  - `implementation 'com.github.bilibili:DanmakuFlameMaster:0.9.25'`
  - `implementation 'com.github.bilibili:ndkbitmap-armv7a:0.9.21'`

### 工作项清单
- Java：新增 `XBMCDanmakuView.java.in`，封装 DFM 视图与 UI 线程 add/remove、seek、矩形同步。
- JNI：新增 `CJNIXBMCDanmakuView.{h,cpp}`；在 `XBMCApp.cpp` 播放回调中联动 DFM。
- Gradle：增加 DFM 依赖（Android packaging 子项目）。
- 播放矩形同步：仿 `setSurfaceRect` 将视频矩形同步到 DFM 视图。
- 设置/冲突处理：启用 DFM 会话时可自动关闭 ASS 弹幕（避免重复显示），Android 平台生效。
- 基础测试：暂停/恢复/seek/倍速，分辨率/缩放切换，透明度与层级验证，性能与丢帧观测。

### 难易度与人力估算
- 难度：中（主要是 JNI 生命周期/矩形同步/依赖配置）。
- 估算：
  - 基线集成（本地 xml + 生命周期 + 矩形同步）：3–7 天。
  - 加在线弹幕源 + 设置项 + 机型适配：1–2 周。

### 风险与缓解
- 多 Surface 叠加在部分安卓电视机型的合成/层级限制。
  - 缓解：优先 SurfaceView；必要时提供 `TextureView` 兜底；严格控制添加顺序与 z-order。
- Seek/倍速同步可能出现偏移。
  - 缓解：使用 Kodi 当前 PTS/播放速率驱动 DFM `seekTo()/resume()`，增加边界校正。
- 资源释放与泄漏。
  - 缓解：统一在 `OnPlayBackStopped/onPause/onDestroy` 释放，引用置空。

### 性能预期
- DFM 作为 Android 原生弹幕引擎，滚动弹幕渲染相对 libass 更流畅；Surface 合成开销可控。

## 方案 B：全平台统一集成（跨平台渲染）
### 技术路径（两种可选）
1) 仅复用 DFM 解析，重写渲染为 Kodi Overlay：
- 在 `OverlayRendererGLES` 分支中新增“弹幕渲染器”，把弹幕布局（滚动轨迹/碰撞/行轨/运动）按帧转换为纹理/几何批次，由 GLES 绘制，与现有 overlay 管线一致。
- 新增 overlay 类型与编码：时间轴驱动、缓存、样式、屏蔽与轨道分配。

2) 尝试“OpenGL 化” DFM：
- 把 DFM 的绘制输出转接到 OpenGL 纹理或 VBO；但 DFM 官方主要是 Android View/Canvas/Surface 路径，OpenGL 化需要大量重构。

### 工作项清单
- 弹幕排布/碰撞/轨道/生命周期管理（引擎层）。
- 渲染缓存与批渲染（纹理图集/字形/描边/阴影/混排）。
- Kodi overlay 生命周期/设置融合（位置、对齐、立体模式、校准等）。
- 字体/国际化/富文本支持（含图片 Span）。
- 跨平台构建与 CI、自动测试。

### 难易度与人力估算
- 难度：高（等同于实现一个跨平台弹幕渲染引擎并与 Kodi 视频/overlay 管线深度融合）。
- 估算：
  - 原型（单平台 GLES + 子集特性）：4–6 周。
  - 可用版本（多平台适配 + 设置融合 + 稳定性）：8–12+ 周。

### 风险与维护
- 大规模代码侵入，后续升级/维护成本高。
- 弹幕引擎本身的性能与边界条件需要长期打磨。
- 与现有字幕/overlay 设置交互复杂，回归测试面大。

### 收益
- 统一渲染通路，无多 Surface 叠加问题。
- 平台覆盖更广，可在非 Android 平台提供一致弹幕体验。

## A vs B 对比（要点）
- 开发成本：A 低/中，B 高。
- 落地速度：A 快（数天到 1–2 周），B 慢（> 1–2 月）。
- 平台覆盖：A 仅 Android，B 全平台。
- 性能与流畅度：A 借力 DFM，滚动弹幕成熟；B 需要自研优化与长期调优。
- 兼容与风险：A 关注 Android 合成/z-order；B 关注引擎正确性/渲染性能与大范围回归。
- 维护成本：A 低（少量 JNI/Java 代码）；B 高（核心渲染路径与引擎维护）。
- 对 Kodi 侵入：A 小；B 大。

## 推荐路径与里程碑
- 阶段 1（Android 优先，推荐）：
  - M1：本地 xml 弹幕 + 生命周期/seek 同步 + 矩形同步（3–7 天）。
  - M2：弹幕设置项（开关、防重叠/速度/字号等）+ 在线源接入（1–2 周）。
- 阶段 2（如有需要）：
  - 评估在特定非 Android 平台的用户需求，再考虑 B 的子集（例如仅解析 + 简化渲染）。

## 验收标准（阶段 1）
- 播放含同名 xml 弹幕视频，弹幕滚动流畅，无明显卡顿/丢帧。
- 暂停、恢复、seek、倍速行为与弹幕同步。
- 分辨率/缩放/刷新率切换时弹幕区域与视频对齐。
- GUI 控件显示正常，不被弹幕遮挡。
- 打开/关闭弹幕时与 ASS 字幕不冲突（同会话仅一种启用）。

## 关键触点（落地参考）
- Overlay/字幕：`OverlayRenderer*.{h,cpp}`、`RenderManager.cpp`。
- Android 视图：`activity_main.xml` 的 `VideoLayout`、`XBMCVideoView.java.in`（视频层）、`XBMCMainView.java.in`（GUI 层）。
- JNI/Activity：`CJNIXBMCVideoView`、`CJNIXBMCMainView`、`XBMCApp.cpp`（`OnPlayBackStarted/Paused/Stopped/OnSeek`）。
- DFM 依赖（示例）：
  - `implementation 'com.github.bilibili:DanmakuFlameMaster:0.9.25'`
  - `implementation 'com.github.bilibili:ndkbitmap-armv7a:0.9.21'`

---
本文档基于对 Kodi 源码（Android 窗口/视图/渲染与字幕管线）的静态分析与 DFM 文档/示例的调研，供方案决策与实施落地参考。
