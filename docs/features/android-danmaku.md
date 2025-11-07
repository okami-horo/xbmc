# Android Danmaku Overlay

This document explains how to use and configure the Android danmaku (scrolling comments) overlay integrated via DanmakuFlameMaster (DFM).

## Overview

- Platform: Android TV (minSdk 24, targetSdk 36)
- Renderer: DanmakuFlameMaster 0.9.25
- Sources: Local same-basename XML only (Phase 1). Example: movie.mp4 + movie.xml
- Defaults: Overlay auto-enables when a matching XML is found at playback start

See third-party attribution in docs/third-party/dfm.md.

## Usage

1. Build and install Kodi for Android (packaging under tools/android/packaging/xbmc).
2. Place a same-basename danmaku file next to your video (e.g., movie.mp4 + movie.xml).
3. Start playback.
4. If not auto-enabled, toggle the overlay via Settings or JSON-RPC (see below).
5. Adjust settings (density, speed, font size, opacity, no-overlap, max_visible) to your preference.

## Settings

The following runtime settings are supported and applied immediately when possible:

- enabled: boolean
- density: number [0..1]
- speed: number (relative scroll speed factor)
- font_size_sp: number (scale relative to 24sp default)
- opacity: number [0..1]
- no_overlap: boolean (prevent overlapping comments)
- max_visible: integer (cap visible comments; 0 or unset = DFM default)

These map to the existing settings framework and are bridged to Java via JNI.

## JSON-RPC

Two primary operations are exposed (see specs/001-dfm-android/contracts/openapi.yaml):

- Danmaku.Toggle (POST /danmaku/toggle)
- Danmaku.SetSettings (PUT /danmaku/settings)

Example payloads:

```json
// Toggle
{"enabled": true}
```

```json
// Settings
{
  "density": 0.7,
  "speed": 1.0,
  "font_size_sp": 24,
  "opacity": 0.9,
  "no_overlap": true,
  "max_visible": 60
}
```

## Performance

- Target: Smooth 60 fps.
- Guardrails: Overlay start is skipped if simple frame budget heuristics indicate risk of jank.
- Instrumentation: Periodic perf ticks are logged when enabled to aid CI/manual profiling.

## Security and Privacy

- Local-file only: The overlay loads danmaku from same-basename local XML files.
- No networking: No network calls are performed by the overlay or its bridge.
- Safety checks: Missing/invalid files are handled gracefully; overlay remains disabled if no source is present.

## Troubleshooting

- No overlay appears: Ensure movie.xml exists next to the video file and is readable.
- Stutter or jank: Reduce density or max_visible; verify device performance; perf ticks can help diagnose.
- Overlay obscures UI: Adjust margins/overlay rect; GUI is kept unobscured by design.

## Usability Test Plan (SC-006)

- Goal: Validate user satisfaction with danmaku controls and defaults.
- Protocol: 5 users on Android TV; 10-minute session. Tasks: enable/disable overlay, adjust density/speed/font size/opacity/no-overlap, confirm readability and unobscured UI during playback.
- Metric: 5-point satisfaction (1–5) on discoverability and visual comfort. Target: ≥4.0 average; ≥80% rate 4 or 5.
- Data capture: Record per-user ratings and key qualitative notes; summarize outcomes in this document under Results.
- Results: [to be filled after running the session]

## Notes

- Mutual exclusion is enforced with scrolling ASS to avoid conflicts.
- Future online sources are explicitly out of scope for this phase.

## Changelog / Distribution Notes

- Adds Android danmaku overlay via DanmakuFlameMaster (DFM) 0.9.25.
- Default behavior: auto-enable overlay when a same-basename XML file is detected at playback start.
- JSON-RPC operations: Danmaku.Toggle and Danmaku.SetSettings.
- Performance: basic guardrails and optional perf tick logging to support CI monitoring.
- Licensing: Repository is GPL-2.0-or-later. Android APKs that include DFM must be distributed under GPLv3+ terms to satisfy license compatibility. See third-party attribution: docs/third-party/dfm.md.
