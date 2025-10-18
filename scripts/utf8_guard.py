import pathlib
import sys


def main() -> int:
    data = sys.stdin.read().strip()
    if not data:
        return 0
    bad = []
    for token in data.split():
        p = pathlib.Path(token)
        if not p.exists():
            # pre-commit may feed deleted/renamed paths; ignore missing
            continue
        try:
            p.read_text(encoding="utf-8")
        except Exception as e:  # noqa: BLE001
            bad.append(f"{p}: {e}")
    if bad:
        print("Non-UTF-8 files detected:\n" + "\n".join(bad))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
