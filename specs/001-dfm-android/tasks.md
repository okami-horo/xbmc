# Tasks: Android Danmaku Overlay

**Input**: Design documents from `/specs/001-dfm-android/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Android packaging setup, dependency, and scaffolding

- [X] T001 Add DFM dependency in tools/android/packaging/xbmc/build.gradle.in (implementation 'com.github.ctiao:DanmakuFlameMaster:0.9.25')
- [X] T002 Create package directories for overlay Java in tools/android/packaging/xbmc/src/overlay/
- [X] T003 [P] Add proguard/consumer rules for DFM in tools/android/packaging/xbmc/proguard-rules.pro and reference from build.gradle.in
- [X] T004 [P] Add third-party NOTICE for DFM in docs/third-party/dfm.md and include in Android packaging (tools/android/packaging/xbmc)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core wiring and feature flags required before story work

- [X] T005 Create settings module files xbmc/settings/danmaku/DanmakuSettings.h and xbmc/settings/danmaku/DanmakuSettings.cpp (enable, density, speed, font size, opacity, no_overlap, max_visible)
- [X] T006 [P] Register danmaku settings in xbmc/settings/danmaku/DanmakuSettings.cpp and ensure defaults per spec
- [X] T007 [P] Add feature guard usage in Android platform entry points xbmc/platform/android/PlatformAndroid.cpp to check settings before enabling overlay
- [X] T008 Create JNI bridge file xbmc/platform/android/activity/JNIDanmakuBridge.cpp exposing onPlay/onPause/onSeek/onSpeedChanged and layout update hooks to Java
- [X] T009 [P] Add Android packaging to load overlay classes at startup in xbmc/platform/android/activity/JNIMainActivity.cpp (invoke JNIDanmakuBridge attach/detach)
- [X] T010 Implement JSON-RPC operations for danmaku in xbmc/interfaces/json-rpc/DanmakuOperations.h and xbmc/interfaces/json-rpc/DanmakuOperations.cpp (methods: Danmaku.Toggle, Danmaku.SetSettings)
- [X] T011 [P] Register new JSON-RPC methods in xbmc/interfaces/json-rpc/JSONServiceDescription.cpp and add schemas under xbmc/interfaces/json-rpc/schema/danmaku.json

---

## Phase 3: User Story 1 - Play video with danmaku overlay (Priority: P1) 

**Goal**: Show smooth, synchronized danmaku overlay aligned to video rectangle during playback on Android

**Independent Test**: Place movie.xml next to movie.mp4. Start playback, enable overlay. Verify smooth scrolling and sync across pause/resume/seek/speed change.

### Implementation for User Story 1

- [X] T012 [P] [US1] Create overlay view class in tools/android/packaging/xbmc/src/overlay/DanmakuOverlayView.java.in (hosts DFM view)
- [X] T013 [P] [US1] Create controller class in tools/android/packaging/xbmc/src/overlay/DanmakuController.java.in (load source, apply settings, lifecycle)
- [X] T014 [US1] Implement JNI calls in xbmc/platform/android/activity/JNIDanmakuBridge.cpp to forward player events to DanmakuController (onPlay/onPause/onSeek/onSpeedChanged)
- [X] T015 [US1] Update xbmc/platform/android/activity/JNIXBMCMainView.cpp to obtain active video rectangle and pass to overlay via JNI
- [X] T016 [US1] Implement same-basename local file discovery in tools/android/packaging/xbmc/src/overlay/DanmakuController.java.in (e.g., movie.mp4 → movie.xml)
- [X] T017 [US1] Ensure mutual exclusion with scrolling ASS: disable conflicting scrolling subtitle mode when overlay enabled in xbmc/cores/VideoPlayer/Process/android/ProcessInfoAndroid.cpp
- [X] T018 [US1] Ensure clean lifecycle: attach overlay on playback start, pause/resume appropriately, and release on stop in xbmc/platform/android/activity/JNIDanmakuBridge.cpp
- [X] T019 [US1] Validate 60fps budget paths in tools/android/packaging/xbmc/src/overlay/DanmakuController.java.in (density caps hook; early-return if frame budget exceeded)
- [X] T020 [US1] Log and surface non-intrusive state when overlay unavailable (no same-name file) in tools/android/packaging/xbmc/src/overlay/DanmakuController.java.in
- [X] T039 [US1] Implement default enablement when a same-basename file is detected at playback start in tools/android/packaging/xbmc/src/overlay/DanmakuController.java.in and verify via acceptance test (FR-012).

**Checkpoint**: User Story 1 independently functional and testable on Android TV

---

## Phase 4: User Story 2 - Configure danmaku experience (Priority: P2)

**Goal**: User can adjust density, speed, font size, opacity, no-overlap, and max_visible; applied immediately or next playback

**Independent Test**: Change each setting and verify visual effect without impacting playback stability

### Implementation for User Story 2

- [X] T021 [P] [US2] Add getters/setters and range clamping in xbmc/settings/danmaku/DanmakuSettings.cpp
- [X] T022 [P] [US2] Bridge settings to Java: add JNI applySettings(enabled, density, speed, size, opacity, no_overlap, max_visible) in xbmc/platform/android/activity/JNIDanmakuBridge.cpp
- [X] T023 [US2] Apply settings live in tools/android/packaging/xbmc/src/overlay/DanmakuController.java.in
- [X] T024 [US2] Expose JSON-RPC method Danmaku.SetSettings in xbmc/interfaces/json-rpc/DanmakuOperations.cpp (maps to contracts/openapi.yaml)
- [X] T025 [US2] Expose JSON-RPC method Danmaku.Toggle in xbmc/interfaces/json-rpc/DanmakuOperations.cpp (maps to contracts/openapi.yaml)
- [X] T026 [US2] Persist user preference defaults using existing settings framework in xbmc/settings/danmaku/DanmakuSettings.cpp
- [X] T027 [US2] Ensure GUI visibility: keep Kodi GUI unobscured by adjusting overlay margins in tools/android/packaging/xbmc/src/overlay/DanmakuOverlayView.java.in
- [X] T028 [US2] Implement optional max_visible cap handling in tools/android/packaging/xbmc/src/overlay/DanmakuController.java.in

**Checkpoint**: User Stories 1 and 2 independently functional

---

## Phase 5: User Story 3 - Source discovery and fallback (Priority: P3)

**Goal**: Clear behavior when no same-basename file is present; optional future online sources are cleanly out of scope

**Independent Test**: Remove movie.xml and verify overlay stays off, status reports "no danmaku found", no crashes

### Implementation for User Story 3

- [ ] T029 [P] [US3] Add discovery status reporting to JSON-RPC in xbmc/interfaces/json-rpc/DanmakuOperations.cpp (e.g., Danmaku.Status)
- [ ] T030 [US3] On playback start without local file, ensure overlay remains disabled and state logged in tools/android/packaging/xbmc/src/overlay/DanmakuController.java.in
- [ ] T031 [US3] Add user-facing non-intrusive indicator via logs/UI hooks in xbmc/platform/android/activity/JNIDanmakuBridge.cpp (no danmaku found)
- [ ] T032 [US3] Guard paths to avoid exceptions on missing/invalid XML in tools/android/packaging/xbmc/src/overlay/DanmakuController.java.in
- [ ] T033 [US3] Document deferred online source support and plugin hook points in docs/third-party/dfm.md

**Checkpoint**: All user stories independently functional

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Hardening, documentation, and performance tuning

- [ ] T034 [P] Add instrumentation/perf logging hooks for frame interval and timing error in tools/android/packaging/xbmc/src/overlay/DanmakuController.java.in
- [ ] T035 Improve error handling and user logs across bridge and controller in xbmc/platform/android/activity/JNIDanmakuBridge.cpp and tools/android/packaging/xbmc/src/overlay/DanmakuController.java.in
- [ ] T036 [P] Update documentation with usage and settings in docs/features/android-danmaku.md
- [ ] T037 [P] Validate quickstart in specs/001-dfm-android/quickstart.md and update as needed
- [ ] T038 Security review: ensure no unintended network access; local-file only paths enforced in xbmc/platform/android/activity/JNIDanmakuBridge.cpp and tools/android/packaging/xbmc/src/overlay/DanmakuController.java.in
- [ ] T040 [P] SC-005 measurement: add autoload success measurement harness and dataset; run on CI/emulator and report ≥95% success.
- [ ] T041 SC-006 measurement: add a brief usability test plan doc and capture satisfaction metric; record outcomes in docs/features/android-danmaku.md.
- [ ] T042 [P] CI perf budget gate: collect frame-interval/timing-error metrics (from T034) and fail CI or flag when thresholds regress; togglable for local runs.
- [ ] T043 [P] Changelog/wiki update: add user-visible changes and licensing distribution note per constitution.
- [ ] T044 [P] Pin CI Android emulator API level to minSdk/targetSdk per plan; document in tools/android/packaging CI config.

---

## Dependencies & Execution Order

### Phase Dependencies

- Setup (Phase 1): none
- Foundational (Phase 2): depends on Setup completion; blocks all stories
- User Stories (Phase 3+): depend on Foundational completion
  - Priority order: P1 → P2 → P3 (can run in parallel after Phase 2 if staffed)
- Polish (Final): after targeted stories complete

### User Story Dependencies

- User Story 1 (P1): no dependency on other stories
- User Story 2 (P2): independent, integrates with US1 via settings but testable standalone
- User Story 3 (P3): independent, reads discovery state; no hard dependency on US1/US2

### Parallel Opportunities

- [P]-marked tasks can run in parallel: T003, T006, T007, T009, T011, T012, T013, T021, T022, T034, T036, T037
- After Phase 2 completes, US1/US2/US3 work can be split across team members

---

## Parallel Example: User Story 1

```
Task: "Create overlay view class in tools/android/packaging/xbmc/src/overlay/DanmakuOverlayView.java.in"
Task: "Create controller class in tools/android/packaging/xbmc/src/overlay/DanmakuController.java.in"
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001–T004)
2. Complete Phase 2: Foundational (T005–T011)
3. Complete Phase 3: User Story 1 (T012–T020)
4. Stop and validate US1 independently on device/emulator

### Incremental Delivery

1. Setup + Foundational → base ready
2. Add US1 → test → demo (MVP)
3. Add US2 → test → demo
4. Add US3 → test → demo

