# AGENTS.md — keelwright

## What this skill does

keelwright is a coding agent skill that adds 28 machine-enforced safety checks to any
AI coding session. It is designed for non-programmers who use AI to write code.

## When to load this skill

- Before any vibe-coding or loop-coding session
- When running an autonomous or unattended agent
- When an agent swarm writes code a human will not review line by line
- Before committing a feature that touches auth, payments, or data

## Key behaviors

1. **Security gates R1–R12** run automatically on every iteration (SQL injection, hardcoded
   secrets, slopsquatting, business logic, auth). These cannot be disabled.

2. **Autonomy dial** controls what the AI can do alone:
   - Autopilot: unattended, escalates on blockers
   - Checkpoint: pauses at phase boundaries
   - Copilot: proposes, human approves

3. **Circuit-breaker** stops runaway loops: 50 iterations max, 5 no-progress cap,
   2-hour timeout, 3× same-error repeat.

4. **Plain-language reports**: every gate outcome is explained in words a non-coder
   understands. No jargon in user-facing messages.

5. **Risk glossary**: 28 named failure modes mapped to enforcement mechanisms.
   See SKILL.md §Risk glossary for the full table.

## Do NOT

- Do not weaken or delete tests to make builds pass
- Do not bypass security gates even on Autopilot
- Do not invent scope without acceptance criteria
- Do not use `git add -A` (stage files by explicit path only)
- Do not trust self-reports from QA runs (verify on disk)

## File structure

```
SKILL.md              — load this (the skill itself)
references/           — detailed patterns (load on demand)
  security-gates.md   — R1-R12 implementations
  circuit-breaker.md  — loop limits
  phases.md           — build loop phases
  writing-code.md     — coding discipline
qa-results/           — verified A/B test data
scripts/              — validate_run.py, workspace_guard.py
templates/            — QA prompts
```
