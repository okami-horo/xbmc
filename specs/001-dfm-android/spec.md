# Feature Specification: Android Danmaku Overlay

**Feature Branch**: `001-dfm-android`  
**Created**: 2025-11-06  
**Status**: Draft  
**Input**: User description: "目前xbmc缺少视频播放过程中显示弹幕的逻辑（可以将弹幕转化为ass作为滚动字幕显示，但是libass渲染的弹幕卡顿严重，几乎不可用）。目前最常用的弹幕处理与显示方案是DanmakuFlameMaster（github仓库地址：bilibili/DanmakuFlameMaster）。很多支持弹幕的播放器软件app都是用的这个库（DanDanPlayForAndroid）。我要为xbmc也集成DFM来处理与显示视频弹幕，xbmc是一个全平台项目，但是我使用xbmc kodi主要是用于安卓系统的TV，因此集成适配android平台即可，工作量小且实现容易。这是评估的结论。"

## Clarifications

### Session 2025-11-06

- Q: 定义支持的弹幕来源与加载顺序？ → A: Phase 1 仅加载同名本地文件（local-only）。
- Q: Android TV 会话弹幕默认状态？ → A: 检测到同名弹幕文件时默认开启，否则保持关闭。
- Q: 默认弹幕密度上限是多少？ → A: 默认不限制，由用户在设置中自行设定上限。

## User Scenarios & Testing (mandatory)

### User Story 1 - Play video with danmaku overlay (Priority: P1)

As an Android TV user playing a local video, I can enable a danmaku overlay so that scrolling comments display smoothly, synchronized to playback.

**Why this priority**: Core user value; replaces unusable libass-based scrolling.

**Independent Test**: Play a video with a same-name danmaku file. Toggle overlay ON. Observe smooth scrolling and sync during pause/resume/seek/speed change without touching other features.

**Acceptance Scenarios**:

1. Given a video with a same-name danmaku file present, When playback starts and danmaku is enabled, Then the danmaku appears within the video region and scrolls smoothly.
2. Given playback is paused, When I resume, Then danmaku resumes from the correct timestamp with no noticeable drift.
3. Given I seek ±30s, When playback continues, Then danmaku positions update within an acceptable sync error (<150ms) after seek completes.
4. Given I change playback speed to 1.5x, When danmaku is enabled, Then danmaku timing matches the new speed.

---

### User Story 2 - Configure danmaku experience (Priority: P2)

As a user, I can configure core danmaku options (enable/disable, density, speed, font size, opacity, no-overlap) so the overlay is readable and non-intrusive on Android TV.

**Why this priority**: Ensures accessibility and usability across devices and user preferences.

**Independent Test**: Adjust each setting independently and verify it applies immediately or on next playback, without impacting video playback itself.

**Acceptance Scenarios**:

1. Given danmaku is enabled, When I reduce density to minimum, Then only a small number of comments are visible at once.
2. Given danmaku is enabled, When I increase font size, Then text size increases while maintaining legibility and layout stability.
3. Given no-overlap is enabled, When multiple comments would collide, Then they are deferred or re-routed to avoid overlap beyond the configured threshold.

---

### User Story 3 - Source discovery and fallback (Priority: P3)

As a user, when a same-name danmaku file is absent, the system communicates that danmaku is unavailable or allows optional configuration of online sources.

**Why this priority**: Predictable behavior and optional extensibility without breaking local-first use.

**Independent Test**: Remove the local danmaku file and verify fallback messaging and settings behavior without exceptions.

**Acceptance Scenarios**:

1. Given no same-name danmaku file exists, When playback starts, Then the overlay stays off and a non-intrusive indicator or setting state reflects "no danmaku found".
2. Given optional online sources are configured, When playback starts without a local file, Then the system fetches danmaku and displays after preparation, or communicates failure gracefully.

---

### Edge Cases

- No associated danmaku file or unreadable format.
- Extremely high comment density or very long comments.
- Rapid, repeated seeks and speed changes.
- Display rectangle changes (resolution/zoom/aspect ratio/refresh rate swaps) during playback.
- Low-end Android TV devices with limited composition layers.
- Conflicts with other overlays/subtitles (e.g., ASS) and GUI controls.
- HDR/tonemap modes where overlay legibility must be preserved.

## Requirements (mandatory)

### Functional Requirements

- FR-001: System MUST allow enabling/disabling a danmaku overlay during video playback on Android.
- FR-002: System MUST automatically discover and load a same-basename local danmaku file when present (e.g., movie.mp4 → movie.xml or supported formats) (per FR-011 Phase 1 scope).
- FR-003: System MUST keep danmaku timing synchronized with playback position across play, pause, resume, seek, and speed changes.
- FR-004: System MUST align danmaku overlay to the active video display rectangle and update alignment when the rectangle changes.
- FR-005: System MUST provide configurable parameters: density, scroll speed, font size, opacity, and optional no-overlap behavior (setting key: no_overlap; minimum vertical spacing unit: line-height; default: 1.0).
- FR-006: System MUST ensure the overlay does not occlude Kodi GUI controls; GUI remains fully visible and interactive.
- FR-007: System MUST prevent duplicated scrolling overlays; if danmaku overlay is ON, conflicting scrolling subtitle modes MUST be OFF for the session.
- FR-008: System MUST handle lifecycle cleanly: allocate on start, pause/resume with app state, release on stop/destroy without leaks.
- FR-009: System MUST degrade gracefully when no danmaku is available or loading fails (no crashes, clear state).
- FR-010: System MUST meet performance targets defined in Success Criteria under typical densities on reference Android TV devices.
- FR-011: System MUST load danmaku only from same-basename local files in Phase 1; online sources are out of scope and handled by future plugins.
- FR-012: System MUST default danmaku to ON when a same-basename local file is detected at playback start; otherwise the overlay remains OFF until the user enables it.
- FR-013: System MUST expose a user-configurable maximum visible danmaku count per screen; by default no cap is applied until the user sets one.

### Acceptance Criteria per FR (testable)

- FR-001: User can enable/disable overlay via Settings and JSON-RPC `Danmaku.Toggle`. Toggling takes effect within 1s during playback; state persists for the current session.
- FR-002: Given `movie.mp4` and `movie.xml` (Bilibili XML), overlay autoloads `movie.xml` at playback start with ≥95% success (see SC-005). Only `.xml` is accepted in Phase 1; unsupported or unreadable files do not crash and leave overlay OFF.
- FR-003: After pause/resume/seek/speed change, danmaku timing error ≤150ms within 1s of operation (SC-002), verified by instrumentation or visual test harness.
- FR-004: Overlay bounds match active video rectangle; when rectangle changes, overlay updates within 200ms. Visual check: overlay top-left within 2px of video region in all tested resolutions/aspect ratios.
- FR-005: Settings (`density`, `speed`, `font size`, `opacity`, `no_overlap`) modify overlay behavior within 1s (or next playback if documented). Inputs are range-clamped; invalid values are rejected without crash.
- FR-006: With overlay ON, Kodi GUI remains fully visible/interactive on all tested screens; overlay applies margins or z-order so controls are unobscured (SC-003).
- FR-007: Enabling danmaku disables conflicting scrolling ASS for the session; both cannot be active simultaneously.
- FR-008: Create/attach on playback start, pause/resume with app state, release on stop/destroy. Stability: 0 crashes and no leaks attributable to overlay over 60 minutes (SC-004).
- FR-009: When no danmaku is available or load fails, overlay remains OFF, logs a non-intrusive state, and playback continues normally.
- FR-010: Under “typical” density (≤30 visible per screen @1080p), 95th-percentile overlay frame interval ≤25ms; scroll stutter ≤1/min (SC-001).
- FR-011: No online/network fetching occurs in Phase 1; attempts are ignored or clearly reported as unsupported in logs.
- FR-012: If a same-basename `.xml` exists at playback start, overlay defaults to ON; otherwise remains OFF until the user enables it.
- FR-013: If `max_visible` is set to N, measured visible danmaku per screen ≤ N for ≥95% of frames under typical conditions.

### Key Entities (if data involved)

- DanmakuItem: display text/content, start time, type (scrolling/top/bottom), duration, style (color, size, stroke), priority.
- DanmakuSource: origin and format of danmaku (local file path), status, last fetch time.
- DanmakuSettings: per-user preferences (enable, density, speed, size, opacity, no-overlap), per-session effective values.

## Assumptions & Dependencies

- Danmaku input is limited to local same-basename files in Phase 1; online acquisition is deferred to future plugins/extensions.
- Default behavior auto-enables danmaku only when such a local file is present; other sessions start with overlay disabled.
- Default density is unrestricted; users can opt-in to caps for performance or readability.
- Overlay layering uses Android composition with a danmaku view between video and GUI; device composition layer limits may affect availability on some models.
- File I/O permissions to read local danmaku files are available; network access may be required if online sources are enabled later.
- Performance expectations are based on typical Android TV hardware; extremely low-end devices may require reduced density defaults.

## Scope & Constraints

- In scope (Phase 1): Local-file danmaku playback, lifecycle sync (play/pause/seek/speed), video-rectangle alignment, core settings (density/speed/size/opacity/no-overlap), conflict avoidance with scrolling subtitles.
- Out of scope (Phase 1): Cross-platform rendering, deep customization (fonts/themes beyond basic), advanced filters, account-linked online services, and non-Android targets.

## Success Criteria (mandatory)

### Measurable Outcomes

- SC-001: Smoothness: During 10-minute playback on a reference Android TV device, scroll stutter events ≤ 1 per minute, and 95th-percentile frame interval for overlay rendering ≤ 25ms under "typical" density defined as ≤30 visible comments per screen at 1080p.
- SC-002: Sync: After seek/pause/resume, absolute timing error between danmaku and playback position ≤ 150ms within 1s of the operation.
- SC-003: Layering: Kodi GUI elements remain visible and interactive with danmaku ON in 100% of tested screens.
- SC-004: Stability: 0 crashes and no memory leaks attributable to the overlay across 60 minutes of continuous playback (validated via instrumentation).
- SC-005: Discoverability: For media with a same-name danmaku file, automatic load success rate ≥ 95% in test suite.
- SC-006: User satisfaction: ≥ 80% of test participants rate danmaku smoothness as "good" or better on Android TV.
