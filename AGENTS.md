# Repository Guidelines

## Project Structure & Module Organization
Core C++ lives in `xbmc/` (e.g., `cores/VideoPlayer`, `guilib/`, `pvr/`, `games/`) with unit tests beside each module (`xbmc/utils/test`). Build and packaging logic resides in `CMakeLists.txt`, `cmake/`, and `project/`. Third-party recipes live in `tools/depends/`, shipped add-ons in `addons/`, and docs in `docs/`. Runtime assets sit in `media/` and `system/`, while `userdata/` stores portable profiles via `kodi -p`. Treat every `build*/` directory as disposable output.

## Build, Test & Development Commands
Use an out-of-tree workflow:
- `cmake -S . -B build -DCMAKE_INSTALL_PREFIX=/usr/local -DCORE_PLATFORM_NAME="x11 wayland gbm" -DAPP_RENDER_SYSTEM=gl`
- `cmake --build build -j$(getconf _NPROCESSORS_ONLN)` to compile binaries such as `./build/kodi-x11`
- `cmake --build build --target install` to stage the bundle
- `cmake --build build --target kodi-test` or (inside `build/`) `make check` for the gtest suite
- `./build/kodi-test --gtest_filter=VideoPlayer.*` and `--gtest_list_tests` for scoped runs
See `docs/README.<platform>.md` for additional flags and dependency lists per OS.

## Coding Style & Naming Conventions
Kodi targets C++20, Allman braces, two-space indentation, and a 100-column limit. Namespaces/constants are `UPPER_SNAKE_CASE`, classes use a `C` prefix, interfaces `I`, and every method is PascalCase. Locals stay camelCase, members take `m_` or `ms_`, and globals (avoid them) start with `g_`. Format new code with `clang-format` ≥9 using the repository configuration and follow the include-order, logging, and documentation rules in `docs/CODE_GUIDELINES.md`.

## Testing Guidelines
Add tests beside the code they verify and keep fixtures deterministic. Prefer reusing the existing `xbmc/**/test/testdata` directories for sample media or XML payloads, documenting any new assets as needed. Ensure `make check`/`kodi-test` passes locally before requesting review, and share the exact `--gtest_filter` commands used to reproduce or verify bugs.

## Commit & Pull Request Guidelines
Work on topic branches rebased onto `master`, keep commits focused, and follow the subject pattern `[Component][Area] concise summary` (e.g., `[VideoPlayer][Clock] Tighten drift guard`). PR descriptions must explain the behavior change, link issues or forum threads, and list the tests or platforms exercised. Wait for Jenkins formatting/build jobs to go green and attach screenshots, logs, or sample media notes whenever UI or playback behavior changes.

## Security & Configuration Tips
Use portable mode (`./build/kodi-x11 -p`) or a throwaway `userdata/` path when experimenting with settings so real profiles stay intact. Never commit credentials, signing keys, or closed media; keep them outside the repo. Document any `system/` or `tools/depends/` change that affects attack surface.