#!/usr/bin/env python3
import os
import sys
import statistics

LOG_FILE = os.environ.get("LOG_FILE", "tools/android/packaging/ci/datasets/perf_log_sample.txt")
PCTL = float(os.environ.get("PERF_PCTL", "95"))
THRESHOLD_MS = float(os.environ.get("PERF_95TH_MS", "25"))
GATE = os.environ.get("PERF_GATE", "0") in ("1", "true", "TRUE", "yes", "on")


def load_ticks(path):
    vals = []
    try:
        with open(path, 'r') as f:
            for line in f:
                line = line.strip()
                # Example: perf.tick_ms=16.667, density=1.0, speed=1.0
                if "perf.tick_ms=" in line:
                    try:
                        part = line.split("perf.tick_ms=")[1]
                        num = part.split(",")[0]
                        vals.append(float(num))
                    except Exception:
                        continue
    except FileNotFoundError:
        print(f"[PERF_GATE] log file not found: {path}")
    return vals


def percentile(data, p):
    if not data:
        return None
    s = sorted(data)
    k = (len(s) - 1) * (p / 100.0)
    f = int(k)
    c = min(f + 1, len(s) - 1)
    if f == c:
        return s[int(k)]
    d0 = s[f] * (c - k)
    d1 = s[c] * (k - f)
    return d0 + d1


def main():
    vals = load_ticks(LOG_FILE)
    if not vals:
        print("[PERF_GATE] No perf ticks found; skipping gate")
        sys.exit(0)
    pctl = percentile(vals, PCTL)
    print(f"[PERF_GATE] p{int(PCTL)}={pctl:.3f}ms threshold={THRESHOLD_MS:.3f}ms (samples={len(vals)})")
    if GATE and pctl is not None and pctl > THRESHOLD_MS:
        print("[PERF_GATE] FAIL: percentile exceeds threshold")
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
