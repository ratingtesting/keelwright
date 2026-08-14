#!/usr/bin/env python3
"""check_update.py — non-blocking Keelwright self-update check.

WHY: a safety skill running on an old version is a risk (new gates, fixed holes).
But we NEVER block the human's work on an update. This script checks the latest
GitHub release and compares it to the version pinned in this skill's SKILL.md.

DESIGN RULES (do not weaken):
- Always exits 0 (non-blocking). Never aborts the agent's run.
- Silent on ANY failure (no network, no python, rate limit) — safe to call unconditionally.
- Caches the result 24h in ~/.cache so we don't hammer the GitHub API every load.
- Stdlib only (urllib) — runs on Windows/MSYS and Linux with no pip installs.

OUTPUT: one plain-language line if an update exists, nothing if up to date or on error.
The human decides; the script only informs.
"""
import json
import os
import re
import sys
import datetime
import urllib.request

SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_FILE = os.path.join(os.path.expanduser("~"), ".cache", "keelwright_update_check.json")
REPO = "ratingtesting/keelwright"
API_URL = f"https://api.github.com/repos/{REPO}/releases/latest"
CACHE_TTL_HOURS = 24


def local_version() -> str | None:
    skill_md = os.path.join(SKILL_ROOT, "SKILL.md")
    try:
        with open(skill_md, encoding="utf-8") as f:
            for line in f:
                if line.startswith("version:"):
                    return line.split(":", 1)[1].strip().strip('"')
    except Exception:
        return None
    return None


def parse_ver(v: str):
    m = re.match(r"^(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z.-]+))?$", v or "")
    if not m:
        return None
    return (int(m.group(1)), int(m.group(2)), int(m.group(3)), m.group(4) or "")


def cache_get() -> str | None:
    try:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, encoding="utf-8") as f:
                data = json.load(f)
            ts = datetime.datetime.fromisoformat(data.get("ts", "2000-01-01T00:00:00"))
            if (datetime.datetime.now() - ts).total_seconds() < CACHE_TTL_HOURS * 3600:
                return data.get("latest")
    except Exception:
        pass
    return None


def cache_set(latest: str) -> None:
    try:
        os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump({"ts": datetime.datetime.now().isoformat(), "latest": latest}, f)
    except Exception:
        pass


def main() -> int:
    lv = local_version()
    if not lv:
        return 0
    latest = cache_get()
    if not latest:
        try:
            req = urllib.request.Request(API_URL, headers={"User-Agent": "keelwright-update-check"})
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            latest = (data.get("tag_name") or "").lstrip("v")
            if latest:
                cache_set(latest)
        except Exception:
            return 0  # silent on any network/API error
    if not latest:
        return 0
    lp = parse_ver(lv)
    rp = parse_ver(latest)
    if lp and rp and rp > lp:
        print(
            f"⚠️ Keelwright update available: v{latest} (you have v{lv}). "
            f"Reinstall from https://clawhub.ai/ratingtesting/skills/keelwright "
            f"or pull ratingtesting/keelwright."
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
