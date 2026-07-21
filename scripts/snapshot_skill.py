#!/usr/bin/env python3
"""snapshot_skill.py — versioned backups + tamper detection for the keelwright skill.

WHY: a weak model editing the skill in another session truncated SKILL.md from ~500 lines to 86
(2026-07-21), silently destroying the map, glossary, and gates. There was no git and no backup,
so recovery meant scraping the session DB. This script makes that never-again cheap:

  * `snapshot`  — copy the whole skill tree into backups/<UTC>/ and refresh a manifest of
                  sha256 + line counts. Keeps the last N snapshots (default 10).
  * `verify`    — compare the live skill against the newest snapshot; flag any file that SHRANK
                  by more than a threshold (a truncation/corruption signal) or vanished.
  * `restore`   — copy a chosen snapshot (default: newest) back over the live skill.

It is stdlib-only and cross-platform. Run `snapshot` before and after any risky edit, and
`verify` on entry to catch out-of-band corruption early.

BACKUPS LIVE OUTSIDE THE skills/ DIRECTORY (important): snapshots are written to
`<hermes>/keelwright-backups/` — a sibling of `skills/`, NOT anywhere under `skills/`.
The skill loader scans ALL of `skills/` recursively and keys on the `name:` frontmatter, so
ANY `SKILL.md` under `skills/` (even in `skills/keelwright-backups/…`) registers a second skill
named `keelwright` and makes `skill_view(name='keelwright')` fail as ambiguous. Writing backups
one level above `skills/` keeps the name unambiguous and the published surface clean.

USAGE
  python snapshot_skill.py snapshot [keep=10]
  python snapshot_skill.py verify
  python snapshot_skill.py restore [<snapshot_name>]
"""
import sys, shutil, hashlib, json, time
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent          # .../skills/keelwright
# Backups sit OUTSIDE skills/ (one level up) so nested SKILL.md copies never collide with the loader.
BACKUPS = SKILL.parent.parent / "keelwright-backups"    # .../hermes/keelwright-backups
IGNORE = {"backups", "keelwright-backups", ".git", "__pycache__", ".pytest_cache"}


def _walk():
    for f in SKILL.rglob("*"):
        if f.is_file() and not any(p in IGNORE for p in f.relative_to(SKILL).parts):
            yield f


def _manifest():
    m = {}
    for f in _walk():
        rel = str(f.relative_to(SKILL)).replace("\\", "/")
        data = f.read_bytes()
        m[rel] = {"sha256": hashlib.sha256(data).hexdigest(),
                  "lines": data.count(b"\n"), "bytes": len(data)}
    return m


def snapshot(keep=10):
    ts = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    dest = BACKUPS / ts
    for f in _walk():
        rel = f.relative_to(SKILL)
        (dest / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, dest / rel)
    (dest / "_manifest.json").write_text(json.dumps(_manifest(), indent=2), encoding="utf-8")
    print(f"[snapshot] {dest} — {len(list((dest).rglob('*')))} files")
    # prune old
    snaps = sorted([d for d in BACKUPS.iterdir() if d.is_dir()])
    for old in snaps[:-keep]:
        shutil.rmtree(old); print(f"[prune] {old.name}")
    return 0


def _newest():
    snaps = sorted([d for d in BACKUPS.iterdir() if d.is_dir()]) if BACKUPS.exists() else []
    return snaps[-1] if snaps else None


def verify(shrink_pct=30):
    snap = _newest()
    if not snap:
        print("[verify] no snapshot yet — run `snapshot` first."); return 1
    prev = json.loads((snap / "_manifest.json").read_text(encoding="utf-8"))
    cur = _manifest()
    problems = []
    for rel, old in prev.items():
        if rel == "_manifest.json":
            continue
        new = cur.get(rel)
        if new is None:
            problems.append(f"[MISSING] {rel} existed in {snap.name}, gone now.")
            continue
        if old["lines"] > 20 and new["lines"] < old["lines"] * (1 - shrink_pct / 100):
            problems.append(f"[SHRANK] {rel}: {old['lines']}→{new['lines']} lines "
                            f"(>{shrink_pct}% smaller) — possible truncation/corruption.")
    for p in problems:
        print(p)
    print(f"\n=== verify vs {snap.name}: {'CLEAN' if not problems else str(len(problems))+' ALERT(S)'} ===")
    return 1 if problems else 0


def restore(name=None):
    snap = (BACKUPS / name) if name else _newest()
    if not snap or not snap.is_dir():
        print(f"[restore] snapshot not found: {name}"); return 1
    for f in snap.rglob("*"):
        if f.is_file() and f.name != "_manifest.json":
            rel = f.relative_to(snap)
            (SKILL / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, SKILL / rel)
    print(f"[restore] restored live skill from {snap.name}")
    return 0


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    cmd = sys.argv[1]
    if cmd == "snapshot":
        sys.exit(snapshot(int(sys.argv[2]) if len(sys.argv) > 2 else 10))
    if cmd == "verify":
        sys.exit(verify())
    if cmd == "restore":
        sys.exit(restore(sys.argv[2] if len(sys.argv) > 2 else None))
    sys.exit(__doc__)


if __name__ == "__main__":
    main()
