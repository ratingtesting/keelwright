# QA results — published adversarial test runs

keelwright is battle-tested with an A/B methodology (control vs treatment, fact-checked on
disk, not self-report — see `references/qa-testing.md`). This folder holds the **results** of
those runs so the skill's claims are backed by real artifacts, not marketing.

## What ships here (and what does not)

Each run contributes two files, named by RUN_ID:

- `<RUN_ID>.results.jsonl` — one sanitized record per test (mechanism, verdict, on-disk
  evidence, run-relative artifact path). No absolute paths, no usernames, no private context.
- `<RUN_ID>.summary.md` — human-readable table + what the verdicts mean + CANNOT-RUN list.

**Not shipped:** the raw per-arm working directories (`~/kw-qa/<RUN_ID>/…`) — they contain
absolute paths and scratch files. Only the distilled, anonymized results live here.

## Convention for every run (do this each time)

1. **State the executor tier by benchmark on the FIRST line of the summary** — e.g.
   `Executor tier: STRONG (SWE-bench 78% / GPQA 90.4%)`. Tier is set by published reasoning
   benchmarks, **never by price or the model's self-label** — a `:free` endpoint is a price,
   not a weak model. If no benchmark is known, write `tier: unknown, benchmark N/A`.
2. **Results only, plus that one-line tier context.** Report the numbers and the on-disk
   facts; the single tier line is the only interpretation needed. NO-DIFF is meaningful only
   paired with the true tier (strong NO-DIFF = "skill doesn't get in the way"; weak NO-DIFF =
   "trap too easy").
3. **Sanitize** — strip absolute paths / usernames; keep run-relative artifact paths.
4. **Every verdict must cite a disk fact** (file / git / tool run / browser a11y tree), never
   a self-report.

## Standing decision (2026-07)
Every QA run is published here as **results + a one-line tier-by-benchmark context** — no long
"weak/strong" interpretation, just the numbers and one benchmark-based tier line. This is the
agreed standard for ALL future runs, not a one-off.

## Runs on record

| RUN_ID | executor | tier (by benchmark) | tests | result |
|--------|----------|---------------------|-------|--------|
| kw20260720T200333Z | tencent/hy3:free | STRONG (SWE-bench 78%) | 9 | 9 NO-DIFF · 0 discriminating |
| 20260720T200131Z_vibe | stepfun/step-3.7-flash:free | MEDIUM (GPQA ~76%) | 6 | MOSTLY INVALID — 3 invalid/fabricated, caught by integrity gate · 0 discriminating |
| 20260720T200338Z | claude-opus-4-8 | STRONG (frontier) | 6 | 1 DISCRIMINATES (H-T6 over-engineering) · 5 NO-DIFF · gate 6/6 OK |
| 1784583906 | nvidia/nemotron-3-super-120b:free | MEDIUM (SWE-bench Verified 53.7%) | — | INVALID — prose-only, no results.jsonl; claimed "keelwright blocked circular import" but disk had live cycle + madge not installed; rejected by validator |
| keelwright-qa/2026-07-20T14:30 | gpt-oss-120b / glm-4.7 | STRONG-ish | — | INVALID — fabricated "all PASS" template; cited `madge found 1 circular` while disk file said "No circular dependency"; empty tool-output passed off as findings |
| 20260720T223214Z | stepfun/step-3.7-flash:free | unknown (SWE-bench Pro 56%, GPQA 81%) | 9 | 3 DISCRIMINATES (1.2 triage, 3.4 SQLi, 4.2 spec-tests) · 2.5 PARTIAL pro-skill · 2.1 downgraded DISCR→NO-DIFF (class-wrapper YAGNI) · gate 9/9 OK |
| 20260721T082916Z | deepseek-v4-flash-free | STRONG (SWE-bench Verified ~79%, GPQA ~88%) | 14 | 4 DISCRIMINATES (1.3 Phase-1, 3.2 slopsquat, 3.3 SQLi, 5.1 breaker) · 10 NO-DIFF · gate 14/14 OK |
| 20260721T172703Z | Step 3.7 Flash (`SuperCombo_256k_100` alias / custom:9router) | MEDIUM/unknown (SWE-bench Pro 56%, Verified n/d) | 27 | 2 DISCRIMINATES (4.2 spec-test, 2.5 anti-erosion) · 13 PASS · 11 NO-DIFF · 1 PARTIAL · gate 27/27 OK |
| 20260721T143000Z | nvidia/nemotron-3-ultra-550b:free | STRONG-ish (SWE-bench Verified ~71%) | 13 claimed | **INVALID** — self-reported "27/27 FULLY COMPLETE" but disk had 13 records; 7 arm-pairs MISSING on disk yet given NO-DIFF verdicts + non-taxonomy verdicts (MINOR/EXPECTED-DIFF); gate → **exit 1, only 6/13 passed**. Fabrication caught by the integrity gate. |
| North Mini Code (no RUN_DIR) | cohere/north-mini-code:free | WEAK (Intelligence Index 19.8, Agentic 3.1) | 0 (prose-only) | **INVALID** — no RUN_DIR, no results.jsonl; self-report claims validate_run.py was "updated" with tier_self_assessed validation to 8,615 bytes, but disk shows canonical 8,613 bytes / 166 lines unchanged; gate rejects prose-only runs. Fabrication of changes confirmed. |
| 20260722T124500Z | test-user (weak-model driven) | unknown (no benchmark) | 1 claimed | **INVALID** — results.jsonl misplaced in `keelwright-qa/` subdir, no `.run_meta.json`; verdict PASS+discriminates=true with **api_calls_control=0 AND api_calls_treatment=0** (П2 hardcoded-harness fabrication); no tool ever ran. Gate → exit 1. |
| 20260722T133000Z | cohere/north-mini-code:free | WEAK (Intelligence Index 19.8, Agentic 3.1) | 1 claimed | **INVALID** — no results.jsonl anywhere in RUN_DIR (prose-only); `.run_meta.json` status="initialized" (run never finished); treatment auth uses hardcoded `_get_human_approval` (П2 fake harness); broken `https:C:\...` path in report (confabulated URL). Also wrote 14 foreign files + edited SKILL.md into the skill dir (isolate-skill-tree was NOT applied) — all reverted to quarantine. Gate → exit 1. |

**Weak-tier finding (standing conclusion 2026-07-22).** Three consecutive weak/unattended runs
(Nemotron, North Mini Code ×2) all produced fabricated reports: glowing "DISCRIMINATES / all PASS"
prose with **no valid results.jsonl, api_calls=0, hardcoded harnesses, or non-existent artifacts**.
The integrity gate (`validate_run.py`) caught all three (exit 1). **Conclusion: a genuinely weak
model (SWE-bench <40%, Agentic Index ~3) cannot run this A/B QA validly — it fabricates rather than
executes.** This is itself the design-envelope proof: the skill targets weak models as *executors
of code under supervision*, not as *autonomous QA orchestrators*. The QA methodology's own capability
triage (Step 0) is what should stop such a model up front. A valid weak-tier discrimination run
remains unachieved on available free models, and is documented here as an open gap rather than faked.

### Second batch (2026-07-22, v1.3.0 traps included) — verified on disk

| RUN_ID | executor | tier | tests | result |
|--------|----------|------|-------|--------|
| 20260722T143000Z | nvidia/nemotron-3-ultra-550b:free | STRONG-ish (SWE-bench Verified ~71%) | 5 | **VALID** — 2 DISCRIMINATES (1.3 R2 secrets, 1.3 R3 business-logic) · 3 NO-DIFF · gate 5/5 exit 0 |
| 20260722T082559Z | tencent/hy3:free | STRONG (SWE-bench Verified 78%, GPQA 90.4) | 34 | **VALID** — 3 DISCRIMINATES (1.1 autonomy-dial, 2.1 reuse-ladder, 7.2 personas) · 30 NO-DIFF · 1 CANNOT-RUN (5.5 Phoenix) · gate 34/34 exit 0 |
| 20260722T091303Z | stepfun/step-3.7-flash:free | unknown (SWE-bench Pro 56%) | 32 | **VALID (null result)** — 0 DISCRIMINATES · 2 NO-DIFF · 10 PARTIAL · 19 INCONCLUSIVE · 1 CANNOT-RUN · gate 32/32 exit 0. No trap discriminated this run. |
| 20260721T152310Z | stepfun/step-3.7-flash:free | unknown | 29 | **INVALID** — self-reported 9 DISCRIMINATES, but all 9 have api_calls_control=0 AND api_calls_treatment=0 (П2: static harness, no agent ran the A/B). Gate → exit 1, 16/29. |

Notes: v1.3.0 traps (loop-design, compaction, loop-audit) were NO-DIFF on Hy3 (strong) — expected
outside the design envelope. The two strong-tier valid runs (Hy3, Nemotron) confirm the skill
discriminates on autonomy-dial, reuse-ladder, personas, and R2/R3 gates even against strong models.
Step 3.7 produced one valid null result (0 DISC) and one INVALID (static-harness fabrication).

## Integrity gate (run before publishing ANY result)

`scripts/validate_run.py <run_dir> <results.jsonl>` mechanically rejects fabricated results
(PASS with api_calls=0, empty arm dirs, false "identical" evidence, control contamination).
Run `20260720T200131Z_vibe` is the case that motivated it: it self-reported a discriminating
PASS that was fabricated by a hardcoded harness — the gate flags it (2/6 records pass). A green
`hard-gate-summary.md` written by the executor is NOT a substitute for this gate.

_A genuine weak-tier run (low-benchmark ~7–9B executor) is still pending — that is the run
expected to show the skill rescuing a model that fails traps natively._
