#!/usr/bin/env python3
"""export_skill.py — bundle the entire keelwright skill into a portable .zip

Packages the public skill (excludes internal/ and backups/ unless --all) plus QA results
and the current git state, so it can be unpacked on another machine in one step.

Stdlib only. Usage:
  python export_skill.py                  → export to ~/kw-qa/keelwright-export-<ts>.zip
  python export_skill.py -o /tmp/kw.zip   → export to a specific path
  python export_skill.py --all            → include internal/ and backups/ (full state)
"""
import zipfile, os, time, argparse, hashlib
from pathlib import Path

SKILL = Path(os.environ.get("KEELWRIGHT",
    os.path.expanduser("~/AppData/Local/hermes/skills/keelwright")))
SKIP_PUBLIC = {"internal", "backups", ".git", "__pycache__", ".pytest_cache"}
SKIP_ALL = {".git", "__pycache__", ".pytest_cache"}
MANIFEST_ENTRIES = []


def rel(root: Path, f: Path):
    return str(f.relative_to(root)).replace("\\", "/")


def add_to_zip(zf: zipfile.ZipFile, base: Path, pattern: str = "*",
               skip_dirs: set = None, max_bytes: int = 10 * 1024 * 1024):
    """Walk base/pattern, skip dirs in skip_dirs, add files to zf. Skip files > max_bytes."""
    if skip_dirs is None:
        skip_dirs = set()
    added = 0
    for f in sorted(base.rglob(pattern)):
        if not f.is_file():
            continue
        if any(p in skip_dirs for p in f.relative_to(base).parts):
            continue
        size = f.stat().st_size
        if size > max_bytes:
            print(f"  [SKIP] {rel(base, f)} ({size//1024}KB > {max_bytes//1024}KB limit)")
            continue
        arcname = rel(base, f)
        zf.write(f, arcname)
        data = f.read_bytes()
        MANIFEST_ENTRIES.append({
            "path": arcname, "size": size, "sha256": hashlib.sha256(data).hexdigest()
        })
        added += 1
    return added


def export(out_path: Path, include_internal: bool):
    skip = SKIP_ALL if include_internal else SKIP_PUBLIC
    total = 0

    print(f"Skill source: {SKILL}")
    if not SKILL.exists():
        print(f"[ERROR] Skill not found at {SKILL}"); return 1

    out_path.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        # 1. Skill files
        print("\n--- Skill files ---")
        total += add_to_zip(zf, SKILL, skip_dirs=skip)

        # 2. QA results (always included — public)
        qa = SKILL / "qa-results"
        if qa.exists():
            print(f"\n--- QA results ---")
            total += add_to_zip(zf, qa.parent, skip_dirs=skip)

        # 3. External QA run dirs (kw-qa/) — only if NOT already inside the skill's qa-results/
        #    This avoids duplicate entries when qa-results/ is already part of the skill tree.
        qa_inside_skill = (SKILL / "qa-results").exists()
        kwqa = SKILL.parent.parent / "kw-qa"  # ~/kw-qa/
        if kwqa.exists() and kwqa != SKILL and not qa_inside_skill:
            print(f"\n--- External QA runs (kw-qa/) ---")
            for run in sorted(kwqa.iterdir()):
                if not run.is_dir():
                    continue
                rj = run / "results.jsonl"
                if rj.exists():
                    total += add_to_zip(zf, run, skip_dirs={"__pycache__", "node_modules"})
                    print(f"  included: {run.name}")
        elif qa_inside_skill:
            print(f"\n--- QA runs already inside skill/qa-results/ (skipping external scan) ---")

        # 4. Context transfer prompt
        ct = kwqa / "CONTEXT-TRANSFER-PROMPT.md" if kwqa.exists() else None
        if ct and ct.exists():
            zf.write(ct, "_CONTEXT-TRANSFER-PROMPT.md")
            total += 1

        # 5. Manifest (sha256 of every file — tamper detection on import)
        import json as _json
        zf.writestr("_MANIFEST.json", _json.dumps({
            "exported": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "skill_path": str(SKILL),
            "files": len(MANIFEST_ENTRIES),
            "total_bytes": sum(e["size"] for e in MANIFEST_ENTRIES),
            "entries": MANIFEST_ENTRIES,
        }, indent=2))
        total += 1

    size = out_path.stat().st_size
    print(f"\n=== EXPORTED ===")
    print(f"  {out_path}")
    print(f"  {total} files, {size:,} bytes ({size//1024}KB)")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Export keelwright skill to portable .zip")
    parser.add_argument("-o", "--output", help="Output .zip path")
    parser.add_argument("--all", action="store_true", help="Include internal/ and backups/")
    args = parser.parse_args()

    if args.output:
        out = Path(args.output)
    else:
        ts = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
        out = Path(os.path.expanduser("~/kw-qa")) / f"keelwright-export-{ts}.zip"

    return export(out, args.all)


if __name__ == "__main__":
    exit(main())
