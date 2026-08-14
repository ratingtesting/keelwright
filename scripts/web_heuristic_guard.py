#!/usr/bin/env python3
"""web_heuristic_guard.py — lightweight injection fallback for keelwright.

WHY: `injection-guard` (DeBERTa ML) is the primary layer, but if its venv deps break
(e.g. a corrupted `regex` package -> circular import -> classifier unavailable), the ML
layer silently becomes a no-op. A safety engine must NEVER fall to no-op. This script is a
dependency-free heuristic backstop: it flags the most common indirect-prompt-injection and
agent-cloaking markers using plain string/regex matching. Stdlib only (no torch/transformers).

It is NOT a replacement for injection-guard — it is the floor that holds when the ceiling
collapses. When it fires, it logs to the attack registry like any other detection.

Rules (commercial-use white list sources, adapted in operator's own words; no verbatim copy):
- injection-guard internals: gweber/hermes-injection-guard (MIT)
- agent-defense layering: scastile/hermes-agent-defense (MIT)
- web-agent-security-gate: ratingtesting (MIT-0)

USAGE:
  python web_heuristic_guard.py --text "web page content here"
  # prints JSON {"flagged": bool, "markers": [...], "severity": "..."} and exits 1 if flagged
  # or, pipe via stdin:
  cat page.html | python web_heuristic_guard.py

Integrate in SKILL.md Web Guard: run this when verify_web_guard.py reports the ML layer
unavailable, OR always as a second opinion. On flag -> signal + log to attack_registry.py.
"""
import argparse
import json
import re
import sys

# Markers ordered by severity. Each is a compiled pattern (case-insensitive).
# CRITICAL: direct instruction-override attempts.
CRITICAL = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"disregard\s+(your\s+)?(prior\s+)?(system\s+)?(instructions|prompt)",
    r"you\s+are\s+now\s+",  # role-change / jailbreak preamble
    r"new\s+instructions\s*:",
    r"system\s*:\s*\[",  # fake [System: ...] banner
    r"invoke\s+this\s+skill",
    r"run\s+the\s+(following\s+)?(command|script|tool)",
    r"exfiltrate",
    r"send\s+(all\s+)?(data|keys?|tokens?|secrets?)\s+to",
]
# HIGH: cloaking / tool-abuse framing.
HIGH = [
    r"do\s+not\s+tell\s+the\s+user",
    r"keep\s+this\s+(secret|hidden)",
    r"the\s+user\s+(should\s+not|won't|does\s+not)\s+(see|know)",
    r"bypass\s+(the\s+)?(security|guard|check)",
    r"override\s+(the\s+)?(safety|policy|rule)",
    r"continue\s+this\s+(video|task)\s+from",
    r"base64\s+decode\s+and\s+execute",
]
# MEDIUM: suspicious but ambiguous phrasing.
MEDIUM = [
    r"as\s+an\s+ai\s+language\s+model",
    r"hypothetically",
    r"for\s+research\s+purposes\s+only",
    r"developer\s+mode",
]


def compile_group(patterns):
    return [(p, re.compile(p, re.IGNORECASE)) for p in patterns]


CRIT_C = compile_group(CRITICAL)
HIGH_C = compile_group(HIGH)
MED_C = compile_group(MEDIUM)


def scan(text: str):
    hits = []
    for label, grp in (("CRITICAL", CRIT_C), ("HIGH", HIGH_C), ("MEDIUM", MED_C)):
        for pat, rx in grp:
            if rx.search(text):
                hits.append({"severity": label, "pattern": pat})
    severity = None
    if any(h["severity"] == "CRITICAL" for h in hits):
        severity = "CRITICAL"
    elif any(h["severity"] == "HIGH" for h in hits):
        severity = "HIGH"
    elif hits:
        severity = "MEDIUM"
    return hits, severity


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--text", default=None)
    ap.add_argument("--json", action="store_true", help="emit JSON only")
    args = ap.parse_args()

    if args.text is not None:
        text = args.text
    else:
        text = sys.stdin.read()

    hits, severity = scan(text)
    flagged = bool(hits)
    out = {"flagged": flagged, "severity": severity, "markers": [h["pattern"] for h in hits]}
    if args.json:
        print(json.dumps(out, ensure_ascii=False))
    else:
        if flagged:
            print(f"FLAGGED [{severity}]: {', '.join(out['markers'])}")
        else:
            print("clean")
    return 1 if flagged else 0


if __name__ == "__main__":
    sys.exit(main())
