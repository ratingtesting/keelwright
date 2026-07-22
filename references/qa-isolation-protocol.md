# QA Isolation Protocol

Hard-won rules for running QA/agent sessions without corrupting the skill tree.
Every rule here was discovered the hard way on 2026-07-21/22.

## The problem

Prompt-level rules (П10/П11 "don't edit the skill dir") are NOT enforced by weak models.
Observed: Nemotron 3 Ultra, Step 3.7 Flash, North Mini Code, DeepSeek V4 Flash all wrote
into the skill directory despite explicit prohibitions. Nemotron even overwrote the
integrity gate itself (`validate_run.py`). This is not a bug in the prompt — weak models
genuinely cannot reliably follow negative instructions under task pressure.

## Protocol (before → during → after)

### Before the run
```bash
python workspace_guard.py isolate-skill-tree <skill_dir>
python snapshot_skill.py snapshot   # baseline BEFORE any run touches the tree
```
- `isolate-skill-tree` sets read-only on all skill files at the OS level.
  The model CANNOT write to them, regardless of what the prompt says.
- Take the snapshot BEFORE the run, not after. A post-run snapshot bakes in
  any modifications as the new baseline.

### During the run
- The run writes only to its designated RUN_DIR (e.g. `~/kw-qa/<run_id>/`).
- If the model tries to write to the skill dir, the OS rejects it (Permission denied).
  This is the only isolation that actually holds.

### After the run
```bash
python workspace_guard.py restore-skill-tree <skill_dir>
python snapshot_skill.py verify          # catches SHRINKAGE (truncation)
python snapshot_skill.py verify-additions  # catches ADDITIONS + MODIFICATIONS (via git diff HEAD)
git status --short                       # manual check: nothing unexpected changed
git diff HEAD                            # inspect any changes
```
- Restore write permissions ONLY after verify-additions confirms CLEAN.
- Stage files by explicit path: `git add <file1> <file2>`.
  **NEVER `git add -A`** — it sweeps in stale uncommitted edits from prior sessions.
- If verify-additions shows MODIFIED or UNTRACKED files you didn't touch →
  investigate before committing. Do not trust "it's fine."

## The three-layer protection model

| Layer | Catches | Tool |
|---|---|---|
| **OS read-only** | Write attempts by weak models | `workspace_guard.py isolate-skill-tree` |
| **Git diff HEAD** | Additions, modifications, stale edits | `snapshot_skill.py verify-additions` |
| **Snapshot shrinkage** | Truncation, deletion | `snapshot_skill.py verify` |

All three are needed. Any single layer has blind spots:
- OS read-only doesn't catch modifications made BEFORE isolation was applied.
- Git diff doesn't catch shrinkage within a file (verify does).
- Snapshot verify doesn't catch additions (verify-additions does).

## Pitfall: snapshot verify is misleading after rogue writes

`snapshot_skill.py verify` compares the live tree against the NEWEST snapshot. If a
snapshot was taken AFTER a rogue write, the modification is baked in as the baseline
and verify reports CLEAN. Real case: QA executors wrote 5 new files + edited SKILL.md
(+39 lines) and 7 references; a snapshot taken afterward reported CLEAN.

**Fix:** always compare against git HEAD (the last known-good commit), not against a
post-hoc snapshot. Use `verify-additions` + `git diff HEAD`.

## Pitfall: `git add -A` is a trap

`git add -A` stages everything in the working tree, including:
- Uncommitted changes from prior sessions
- Edits made by QA models during the run
- Stale files that should not be in this commit

Real case: `git add -A` pulled two stale SKILL.md maintaining-notes from an earlier
turn into an unrelated commit.

**Fix:** `git add <specific-files>` only. Check `git status --short` before committing.
If a staged file is one you did not touch this turn, decide deliberately.

## Pitfall: classify by benchmark, not alias

`.run_meta.json` may record a model alias (`SuperCombo_256k_100`) that says nothing
about tier. Always read the published SWE-bench/GPQA number. `unknown` is the honest
tier when the gating benchmark is unpublished — do not upgrade a guess to "strong."
A wrong tier label inverts the meaning of every NO-DIFF in the report.
