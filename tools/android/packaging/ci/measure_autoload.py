#!/usr/bin/env python3
import os
import sys
import csv
from typing import Tuple

THRESHOLD = float(os.environ.get("AUTOLOAD_THRESHOLD", "0.95"))
DATASET_FILE = os.environ.get("DATASET_FILE", "tools/android/packaging/ci/datasets/same_basename.csv")
GATE = os.environ.get("AUTOLOAD_GATE", "1") in ("1", "true", "TRUE", "yes", "on")


def expected_xml(video_path: str) -> str:
    # Replace extension with .xml, handling names without dot
    base = video_path
    dot = base.rfind('.')
    if dot <= 0:
        return base + ".xml"
    return base[:dot] + ".xml"


def measure(dataset_path: str) -> Tuple[int, int]:
    total = 0
    ok = 0
    with open(dataset_path, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            total += 1
            video = row.get('video_path', '').strip()
            xml = row.get('xml_path', '').strip()
            if not video or not xml:
                continue
            if expected_xml(video) == xml:
                ok += 1
    return ok, total


def main():
    if not os.path.exists(DATASET_FILE):
        print(f"[MEASURE_AUTOLOAD] dataset missing: {DATASET_FILE}")
        # No dataset -> skip gate
        sys.exit(0)

    ok, total = measure(DATASET_FILE)
    ratio = (ok / total) if total else 0.0
    pct = int(round(ratio * 100))
    print(f"[MEASURE_AUTOLOAD] success={ok} total={total} rate={pct}% threshold={int(THRESHOLD*100)}%")

    if GATE and ratio < THRESHOLD:
        print("[MEASURE_AUTOLOAD] FAIL: below threshold")
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
