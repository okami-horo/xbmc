# Implementation Plan: [FEATURE]

**Branch**: `001-dfm-android` | **Date**: 2025-11-06 | **Spec**: /workspace/xbmc/specs/001-dfm-android/spec.md
**Input**: Feature specification from `/specs/001-dfm-android/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Integrate DanmakuFlameMaster (DFM) to render a smooth danmaku (scrolling comments) overlay during video playback on Android TV. Phase 1 limits sources to same-basename local files and defaults to ON when such a file is detected. The overlay aligns to the active video rectangle, stays in sync across play/pause/seek/speed changes, exposes core settings (density, speed, size, opacity, no-overlap), and avoids conflicts with scrolling subtitles. Target outcomes include 60 fps UX with overlay 95th-percentile frame interval ≤ 25ms and post-operation timing error ≤ 150ms.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Android Java 8+ (Kotlin interop), C++17 (Kodi core via NDK). Min Android API 24; Target SDK 36.  
**Primary Dependencies**: DanmakuFlameMaster 0.9.25 (Apache-2.0); AndroidX AppCompat/Annotations; existing Kodi player callbacks and settings framework.  
**Storage**: Local file I/O only (same-basename danmaku files; Phase 1 supports Bilibili XML, .xml extension).  
**Testing**: Manual acceptance per spec; Android instrumentation smoke test for toggle/sync (CI emulator permitting).  
**Target Platform**: Android TV devices (Leanback), minSdk 24, targetSdk 36 (per cmake/platform/android/android.cmake).  
**Project Type**: mobile + native (Android UI layer + JNI bridge to Kodi core).  
**Performance Goals**: 60 fps UX; overlay 95th-percentile frame interval ≤ 25ms; post-seek/pause/resume timing error ≤ 150ms; stability: no leaks across 60 min playback.  
**Constraints**: Android-only feature behind guards; no regressions on other platforms; no online sources in Phase 1; avoid occluding Kodi GUI; mutual exclusion with scrolling ASS. CI emulator/API level pinned to plan’s min/target.  
**Scale/Scope**: Single feature touching Android packaging and platform layer; no new top-level modules.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Cross-Platform First: PASS. Android-only implementation behind `#ifdef ANDROID` and runtime feature guard. No changes to non-Android builds; CI must remain green across platforms.
- Add-on APIs Are Stable: PASS. No public add-on/binary API breaks. Settings added via existing framework; any new APIs are internal to Android layer.
- Quality Gates and Reviews: PASS. PR will run full CI including Android. Feature flag/time-boxed; remove if not shipping.
- Performance & UX Smoothness: PASS WITH MEASUREMENTS. Commit includes perf checks; target overlay 60 fps and ≤ 25ms 95th-percentile rendering under typical density; fallback to disable overlay if budget exceeded.
- Internationalization & Accessibility: PASS. All user-visible strings translatable; remote-friendly controls; legibility options (size/opacity/no-overlap).
- Licensing: PASS. Repository is GPL-2.0-or-later. DFM (Apache-2.0) is compatible when the combined Android artifact is distributed under GPLv3+. Include Apache-2.0 NOTICE/attribution (T004) and document distribution terms in release notes/changelog.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
# Kodi Android danmaku integration (no new top-level modules)
tools/
└── android/
    └── packaging/
        └── xbmc/
            ├── build.gradle.in                 # DFM dependency + proguard/consumer rules
            └── src/overlay/
                ├── DanmakuOverlayView.java.in  # Hosts DFM view/lifecycle
                └── DanmakuController.java.in   # Loads sources, applies settings, syncs state

xbmc/
└── platform/android/
    └── activity/
        ├── JNIDanmakuBridge.cpp               # JNI bridge: player events + layout updates
        ├── JNIXBMCMainView.cpp                # existing: obtain video rectangle and pass to JNI
        └── PlatformAndroid.cpp                # feature guard usage for enabling overlay

xbmc/
└── settings/danmaku/
    ├── DanmakuSettings.h
    └── DanmakuSettings.cpp                   # enable, density, speed, size, opacity, no_overlap, max_visible
```

**Structure Decision**: Mobile + native Android integration within existing Kodi tree. No new projects; augment Android packaging (Gradle) and platform layer (Java/JNI) with settings under `xbmc/settings`.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
