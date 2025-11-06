# Data Model: Android Danmaku Overlay

## Entities

- DanmakuItem
  - fields: text, start_ms, type (scrolling/top/bottom), duration_ms, color, size_sp, stroke, priority
  - relationships: belongs to a DanmakuSource
  - validation: non-empty text; reasonable length; start_ms ≥ 0

- DanmakuSource
  - fields: local_path, format, status (loaded/failed), last_loaded_at
  - validation: file exists/readable; supported format

- DanmakuSettings
  - fields: enabled (bool), density (0..1), speed (px/s or rel), font_size_sp, opacity (0..1), no_overlap (bool), max_visible (int|optional)
  - validation: clamp ranges; apply defaults if unset

## State Transitions

- Session start → discover source → load/parse → ready
- Play → overlay start
- Pause → overlay pause
- Seek → overlay reposition to new base time
- Speed change → overlay speed scale
- Stop/Destroy → overlay release
