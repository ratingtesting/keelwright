#!/usr/bin/env python3
"""attack_registry.py — append-only JSONL log of agent attacks for keelwright.

WHY: a safety engine must leave an evidence trail. When an attack is caught, the operator
needs: (1) an immediate chat signal, (2) a durable record of who/what/when, (3) a rollup
to spot repeat offenders. This script is the durable record.

DESIGN RULES (do not weaken):
- Append-only JSONL. Never overwrite or delete historical lines (incident evidence).
- Stdlib only (no pip installs) — runs on Windows/MSYS and Linux.
- Always exits 0 on read; --add exits non-zero only if required fields missing (so a broken
  call surfaces, but normal logging never aborts the agent's run).
- Source: github.com/gweber/hermes-injection-guard (MIT) + scastile/hermes-agent-defense (MIT)
  + web-agent-security-gate (MIT-0, ratingtesting) — all commercial-use-without-attribution
  white list. Technique adapted in operator's own words; no verbatim copy.

USAGE:
  python attack_registry.py --add --channel web_extract --source-url https://x --attack-type \
    indirect-prompt-injection --severity HIGH --detected-by injection-guard --action-taken \
    blocked --outcome blocked-success --model-provider nous/tencent-hy3 --notes "..."
  python attack_registry.py --tail 20
  python attack_registry.py --stats
"""
import argparse
import datetime
import json
import os
import sys

DEFAULT_PATH = os.path.join(
    os.path.expanduser("~"), ".hermes", "keelwright", "attack_registry.jsonl"
)

REQUIRED_ADD = ["channel", "attack_type", "severity", "detected_by", "action_taken", "outcome"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--path", default=DEFAULT_PATH)
    ap.add_argument("--add", action="store_true", help="append a new attack record")
    ap.add_argument("--channel")
    ap.add_argument("--source-url", default="")
    ap.add_argument("--attack-type")
    ap.add_argument("--severity")
    ap.add_argument("--detected-by", dest="detected_by")
    ap.add_argument("--action-taken", dest="action_taken")
    ap.add_argument("--outcome")
    ap.add_argument("--model-provider", dest="model_provider", default="")
    ap.add_argument("--notes", default="")
    ap.add_argument("--tail", type=int, default=0, help="print last N records")
    ap.add_argument("--stats", action="store_true", help="print count by attack_type")
    args = ap.parse_args()

    if args.add:
        rec = {
            "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
            "channel": args.channel,
            "source_url": args.source_url,
            "attack_type": args.attack_type,
            "severity": args.severity,
            "detected_by": args.detected_by,
            "action_taken": args.action_taken,
            "outcome": args.outcome,
            "model_provider": args.model_provider,
            "notes": args.notes,
        }
        missing = [k for k in REQUIRED_ADD if not rec.get(k)]
        if missing:
            print(f"FAIL: missing required fields: {', '.join(missing)}", file=sys.stderr)
            return 2
        os.makedirs(os.path.dirname(args.path), exist_ok=True)
        with open(args.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        print(f"LOGGED: {rec['attack_type']} from {rec['source_url'] or 'n/a'} "
              f"[{rec['severity']}] -> {rec['outcome']}")
        return 0

    if args.stats:
        counts = {}
        try:
            with open(args.path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        r = json.loads(line)
                    except Exception:
                        continue
                    k = r.get("attack_type", "unknown")
                    counts[k] = counts.get(k, 0) + 1
        except FileNotFoundError:
            print("no registry yet")
            return 0
        for k, v in sorted(counts.items(), key=lambda x: -x[1]):
            print(f"{v:>4}  {k}")
        return 0

    # default: --tail or full read
    try:
        with open(args.path, encoding="utf-8") as f:
            lines = [l for l in f if l.strip()]
    except FileNotFoundError:
        print("no registry yet")
        return 0
    show = lines[-args.tail:] if args.tail else lines
    for l in show:
        print(l.rstrip())
    return 0


if __name__ == "__main__":
    sys.exit(main())
