# Research: Android Danmaku Overlay

## Decisions

- Decision: Use DanmakuFlameMaster (DFM) for rendering
  Rationale: Mature, widely used on Android TV/mobile; optimized for scrolling danmaku with rich layout.
  Alternatives considered: libass scrolling (rejected: stutter), custom renderer (rejected: longer time-to-ship).

- Decision: Limit Phase 1 sources to same-basename local files
  Rationale: Simplifies scope and avoids network/privacy concerns; aligns with spec.
  Alternatives: Online sources/plugins (deferred to future phase).

- Decision: Overlay view layered above video and below Kodi GUI
  Rationale: Leverages Android View composition; easiest integration path.
  Alternatives: Render into video surface or GLSurfaceTexture (higher complexity), separate process overlay (not applicable on TV).

- Decision: Sync via explicit player events bridged over JNI
  Rationale: Deterministic state propagation for play/pause/seek/speed; avoids polling.
  Alternatives: Polling player position (inefficient/inaccurate), timestamps from audio clock only.

- Decision: Mutual exclusion with scrolling ASS
  Rationale: Prevent duplicate overlays and visual conflicts.
  Alternatives: Allow both (rejected: UX clutter, performance hit).

- Decision: Performance budget and fallbacks
  Rationale: Meet SC-001/002 with density caps; auto-disable overlay if budget exceeded on low-end devices.
  Alternatives: Unbounded density (rejected).

## Open Items (resolved or next steps)

- Library version for DFM
  Status: RESOLVED. Pin to `com.github.bilibili:DanmakuFlameMaster:0.9.25`. Note: verify ABI coverage on Android TV (arm64-v8a). Fallback: exclude ndkbitmap auxiliary libs or vendor a fork providing arm64 if required.

- License compatibility (Apache-2.0 with GPL-2.0-or-later)
  Status: RESOLVED. DFM is Apache-2.0 and compatible with repository license GPL-2.0-or-later when distributed under GPLv3+. Action: include Apache-2.0 NOTICE/attribution in APK/docs and ensure PR notes distribution under GPLv3 or later.

- Supported danmaku formats and file extensions
  Status: RESOLVED. Phase 1 supports Bilibili XML (.xml) only. Other formats/plugins are out of scope.

- Android minSdk/CI matrix
  Status: RESOLVED. minSdk 24, targetSdk 36 (per `cmake/platform/android/android.cmake`). Validate CI emulator config accordingly.

## Experiments/Findings Summary

- DFM integration approach: Gradle dependency in `tools/android/packaging/xbmc/build.gradle.in` with proguard rules if needed.
- Overlay alignment: Listen for video rectangle changes in Kodi Android activity and update DFM view layout params.
- Timing: Bridge `onPlay/onPause/onSeek/onSpeedChanged` events; set base time on seek completion; validate ≤150ms within 1s.
