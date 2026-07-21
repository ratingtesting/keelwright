# Stability + Phoenix + Autoresearch + self-improvement cron

Three self-learning mechanisms, one layer. Stability works within a session; Phoenix and
Autoresearch are cross-run (they only live if you keep the loop log — see phases.md); the cron
runs weekly.

## Layer 3: Stability Check (5 failure modes)

Every 3 iterations (or before any progress claim) scan 5 named failure modes:

### 1. Dead Retry — each iteration does the same thing
- **Signal:** same error, same fix, same result
- **Action:** change the approach fundamentally (not a variation)
- **Escalate after:** 3 in a row

### 2. Oscillation — fix A breaks B, fix B breaks A
- **Signal:** reverting last iteration's change
- **Action:** stop and ask, or write a plan addressing both
- **Escalate after:** 2

### 3. Drift — the original task is forgotten
- **Signal:** tangents, "while I was at it", improving unrelated code
- **Action:** re-read the goal, discard the tangent
- **Counter:** every 5 turns, restate the original goal

### 4. Amplification — each change makes things worse
- **Signal:** more errors after each iteration, metrics degrade
- **Action:** revert to the last good state, ask for help
- **Escalate after:** 2

### 5. Feedback Starvation — tests/lint green, but UI broken / feature doesn't work
- **Signal:** green checkmarks but something is wrong
- **Action:** launch the Match Loop (visual inspection, `match-loop.md`)
- **Escalate after:** 1 round of visual QA still failing

## Layer 3b: Autoresearch Loop (bounded Modify→Verify→Decide)

Use when the user explicitly asks for iterative improvement toward a measurable metric.

### Run contract (do NOT start without confirming ALL fields)

| Field | Description | Example |
|---|---|---|
| **Model pin** (R9) | provider/model-id fixed for the run | "anthropic/claude-x.y" |
| **Goal** | one sentence, measurable | "render time <200ms" |
| **Metric** | number, direction, baseline, target | "render_time: 350ms → <200ms" |
| **Verify command** | exact command to measure | `<your benchmark command>` |
| **Guard command** | must keep passing | `<your full test command>` |
| **Scope** | files allowed to change | `src/widgets/` |
| **Forbidden scope** | files NEVER changed | `src/auth/`, `migrations/` |
| **Rollback** | how to revert | `git revert HEAD` |
| **Iteration cap** | max iterations | 20 |
| **Run mode** | foreground (default) / background | foreground |

### Core loop
```
1. Confirm approved run contract
2. Read lessons (autoresearch-lessons.md)
3. Pick ONE hypothesis
4. Make ONE atomic change inside scope
5. COMMIT/SNAPSHOT before verification (clean rollback)
6. Run VERIFY command
7. Run GUARD command
8. Decision: keep / discard / rework
   - Verify+Guard PASS → keep, extract lesson
   - Verify PASS + Guard FAIL → rework (max 2), then discard
   - Verify FAIL → discard via approved rollback
9. Log in the iteration log
10. Read the original goal every 10 iterations (anti-drift)
11. Repeat until: goal met, cap reached, user stops, blocker
```

### Escalation ladder
| Trigger | Action |
|---|---|
| 3 discards in a row | REFINE — adjust within the same strategy |
| 5 discards in a row | PIVOT — change strategy fundamentally |
| 2 PIVOTs without improvement | Ask the user before web search |
| 3 PIVOTs without improvement | SOFT BLOCKER — stop, report |

A single successful keep **resets all counters**.

### Safety (CRITICAL)
- Default: foreground only. Background = explicit approval + iteration cap
- Never modify guard files
- Never reset unrelated user work
- Never push/deploy/prod without explicit approval
- Never send private code/secrets to external sinks

### Lessons file
Extract structured lessons after every keep / PIVOT / run completion. Store in
`autoresearch-lessons.md` in the repo root (don't commit without asking). ~50 entries, fold older.

## Layer 4: Phoenix Loop (cross-run learning)

A layer on top that turns repeated errors into durable knowledge.
**Trigger:** Stability detects a failure mode repeating ≥2 times across sessions.

```
1. DIAGNOSE: which exact pattern fails? (exact message, scenario, rationalization)
2. EXTRACT: a structured lesson in autoresearch-lessons.md or durable memory:
   - Pattern: what triggers the failure
   - Root cause: why
   - Fix: how to avoid it next time
   - Example: the actual error
3. CRYSTALLISE: if it repeats 3+ times across sessions:
   - Propose a new skill (skill_manage) OR update the agent-instructions with a new rule
4. VERIFY: next session — does the fix prevent recurrence?
```

Phoenix does NOT replace the scanner. It fires AFTER the scanner detects recurrence.

### ⚠️ L4 is inert without persistent files
Phoenix/Autoresearch fire on cross-session counters. A fresh chat doesn't remember the iteration
number. Triggers only fire if the counters live in files (see phases.md, loop log):

| L4 trigger | How it's counted | Action |
|---|---|---|
| Autoresearch "every 10 iterations" | `grep -c '## Iteration' PROGRESS.md` | summarize lessons |
| Phoenix "3 rollbacks of one feature" | count discard/revert per feature in PROGRESS.md | root cause in phoenix-log |
| Stagnation | 3 iterations in a row with no Next-Step progress | escalate to the user |

## Weekly self-improvement cron

Instead of installing a "proactive/self-improving agent" skill, use a scheduled job:

```
cronjob (weekly)
  ├─ search past sessions for "corrections, fixes, best practices"
  │   └─ extract patterns seen 3+ times
  ├─ memory(add) — if a new rule
  ├─ skill_manage(patch) — if a pitfall for this skill
  └─ SILENT pass — if nothing new (don't spam)
```

| Event | Action |
|---|---|
| User corrected the agent the same way 3+ times | Promote to memory / skill |
| A command fails the same way > 2 times | Promote to a skill pitfall |
| A better approach found for a frequent task | Record as best practice |
| Nothing new | Don't spam |

Why a cron and not a skill: your runtime's memory + session search already cover what file-based
"self-improving agent" skills did; a cron runs automatically, dedups against memory, and stays
silent when there's nothing to add.
