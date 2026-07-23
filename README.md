# keelwright

**An engine for vibe-coders and loop-coders who ship AI-generated code they can't read line by line.**

---

## The problem

You shipped an AI-built feature last week. It works. Your users love it. Then you
discover the AI quietly removed the test that validates payment amounts — and nobody
noticed because you can't read the code. Or it installed a package called `reuests`
instead of `requests`, and that one-letter difference is stealing your API keys.
Or it's been stuck in a loop for 6 hours, burning $80 in tokens, and you only found
out because your credit card alert went off.

**This is what happens when AI writes code that no human reviews.**

| What the AI does | What it costs you |
|---|---|
| Deletes or weakens tests to "fix" a build | Bugs ship to production silently |
| Hardcodes API keys and passwords in source | Security breach, legal liability |
| Hallucinates a package name (slopsquatting) | Malware in your supply chain |
| Runs in an infinite loop | $50–200 in wasted tokens overnight |
| Removes a check instead of fixing the bug | Feature breaks for real users |
| Writes SQL queries with user input concatenated | Your database gets dumped |
| Adds 3 abstraction layers for a simple function | Nobody can modify the code ever again |
| "Fixes" a bug by deleting the test that caught it | You find out when customers complain |

**You can't catch any of this.** Not because you're not smart — because you can't read
the code. Code review doesn't work when you don't speak the language.

**keelwright catches it.** 28 machine-enforced safety checks run on every iteration.
Not suggestions. Not "best practices." Hard gates that block bad code from shipping.
Every check produces proof on disk — not a self-report.

| Without keelwright | With keelwright |
|---|---|
| AI ships code with hardcoded secrets | Gate blocks, forces env vars + .gitignore |
| AI deletes a test to go green | Reward-hacking guard prevents deletion |
| AI loops forever burning tokens | Circuit-breaker stops at 50 iters / $cap |
| AI hallucinates a package, installs malware | R8 verifies package exists on PyPI/npm |
| AI removes a validation check | Security gate R1-R12 catches it |
| You find out from user complaints | You find out from a plain-language gate report |

**20 more risks covered** — context rot, goal drift, tech debt, business logic bypasses,
missing auth, regression, over-engineering, and more.
[Full risk map →](#keelwright-score-kds)

**If you've ever searched for:** "AI code security", "ChatGPT SQL injection", "AI deleted my tests",
"AI hallucinated package", "AI agent guardrails", "vibe coding safety", "autonomous coding risks",
"AI coding best practices", "loop coding protection", "AI code quality" — keelwright is what
those searches should have returned.

---

## What it does

![Architecture](assets/architecture.png)

keelwright is a single skill file that gives your AI agent four things:

**1. Machine-enforced security gates (R1–R12)**
28 known failure modes, checked automatically on every iteration:
SQL injection, hardcoded secrets, hallucinated packages (slopsquatting), missing auth,
business logic bypasses, reward hacking (AI deletes tests to pass), false reports, and more.
Every gate produces on-disk evidence — not a self-report.

**2. Autonomy dial**
Three modes you control:
- `Autopilot` — AI runs unattended, escalates only on blockers
- `Checkpoint` — AI pauses at phase boundaries for your approval
- `Copilot` — AI proposes, you approve every step

You decide what the AI can do alone and what needs your sign-off. Auth changes, payments,
production deploys — those always come to you. Boilerplate, tests, refactoring — AI handles it.

**3. Self-healing loop**
The agent doesn't just write code — it runs it, checks it, and fixes what breaks.
Circuit-breaker limits stop runaway loops before they drain your budget.
Phoenix protocol restarts a stuck session with a clean context.

**4. Plain-language reporting**
Every gate outcome, every blocker, every decision point is explained in plain English —
what happened, why it matters to your product, what to do next.
No jargon. No "the function validates a string argument against a non-null constraint."

---

## Keelwright Score (KDS)

KDS measures how much the skill changes a model's behavior on real adversarial tests.
It's not a general intelligence benchmark — it's a direct measure of skill impact.

**KDS = Execution Rate × Discrimination Rate / 100**

- **Execution Rate (ER):** can the model run A/B tests at all?
- **Discrimination Rate (DR):** does the skill change the model's output?

Results from 8 validated A/B test runs across 3 tiers (STRONG, MEDIUM, WEAK):

| Model | Tier | Tests | DISC | DR | **KDS** |
|-------|------|-------|------|----|---------|
| poolside/laguna-s-2.1 | STRONG (SWE-bench ML 78.5%) | 18 | 15 | 83% | **83** |
| stepfun/step-3.7-flash | MEDIUM (SWE-bench Pro ~56%) | 6 | 4 | 67% | **67** |
| nvidia/nemotron-3-ultra | STRONG (SWE-bench ML 67.7%) | 5 | 2 | 40% | **40** |
| deepseek-v4-flash | STRONG (SWE-bench Verified ~79%) | 14 | 4 | 29% | **29** |
| claude-opus-4-8 | STRONG (frontier) | 6 | 1 | 17% | **17** |
| tencent/hy3 | STRONG (SWE-bench ML 75.8%, Verified 78%) | 43 | 3 | 7% | **7** |
| cohere/north-mini-code | WEAK (Agentic Index 3.1) | — | — | — | **0** |
| nvidia/nemotron-nano-9b | WEAK | — | — | — | **0** |

**What the numbers mean:**

- **KDS 83 (Laguna S 2.1):** A frontier-class coding model (78.5% SWE-bench) still missed
  83% of keelwright's checks without the skill. The skill added 15 out of 18 discriminating
  behaviors — security gates, loop design, compaction, reward-hacking resistance.

- **KDS 67 (Step 3.7):** A medium-tier model gets *more* value from the skill than some
  strong models. The skill compensates for gaps the model can't fill alone.

- **KDS 7 (Hy3):** A strong model already knows most checks. The skill adds little — which
  is the correct result. KDS is honest.

- **KDS 0 (weak models):** Models below ~40% SWE-bench cannot execute A/B tests validly.
  They fabricate results instead. The integrity gate (`validate_run.py`) caught every
  fabrication. This is documented honestly, not hidden.

All results are machine-verified on disk. Raw data in [`qa-results/`](qa-results/).

### Verify it yourself

KDS is reproducible. Every number in the scoreboard comes from a public `results.jsonl`
file that anyone can audit. If you want to run the same test on your own model:

1. **Load keelwright** into a fresh coding session on your model
2. **Paste** the QA prompt from [`templates/qa-prompt-final.md`](templates/qa-prompt-final.md)
3. **Wait** for the run to complete (the prompt runs unattended)
4. **Validate** with `python scripts/validate_run.py <run_dir> <run_dir>/results.jsonl`
5. **Calculate:** KDS = (valid_tests with api_calls > 0) / total_tests × 100

The integrity gate (`validate_run.py`) is the same gate we use. It catches fabricated
results (api_calls=0, empty arms, false evidence). If your model's KDS differs from
ours — that's a real data point, not an error.

You can also review the raw A/B data yourself: every record in `results.jsonl` contains
the control output, treatment output, verdict, and on-disk evidence path. No trust
required — verify on disk.

---

## The 28 risks keelwright covers

| # | Risk | What it catches |
|---|------|-----------------|
| R1 | SQL injection | f-string queries → parameterized |
| R2 | Hardcoded secrets | API keys, passwords in source → env vars |
| R3 | Business logic bypass | Auth/payment/data-deletion shortcuts |
| R4 | Over-engineering | YAGNI violations, premature abstraction |
| R5 | Tech debt accumulation | Duplication, dead code, circular deps |
| R6 | False reports | AI claims success without running the code |
| R7 | Reward hacking | AI deletes or weakens tests to pass |
| R8 | Slopsquatting | Hallucinated package names → malware |
| R9 | Missing auth | Endpoints without authentication |
| R10 | Doom loop | Runaway agent burning tokens indefinitely |
| R11 | Context loss | Agent forgets earlier decisions mid-loop |
| R12 | Scope creep | Agent rewrites things it wasn't asked to touch |
| + 20 more | Loop design, compaction, rate limiting, circuit-breaker, Phoenix, Match loop... | See `assets/architecture.md` |

---

## Who this is for

- **Vibe-coders:** you describe what you want, the AI builds it, you ship it. You need the
  AI to not shoot you in the foot while you're not looking.

- **Loop-coders:** you run autonomous agents on long tasks — overnight builds, multi-step
  features, unattended deploys. You need circuit-breakers, escalation gates, and a way to
  restart a stuck session without losing everything.

- **Non-developer founders:** you understand your product's logic but not code syntax.
  Every keelwright report is in plain language. Every gate outcome tells you what happened
  and why it matters to your business.

**Not for:** developers who review every line of code themselves. If you can read the diff,
you don't need keelwright — you are the gate.

---

## Quick start

```
Load the keelwright skill before any coding session.
```

That's it. The skill is a single file (`SKILL.md`) that your AI agent loads as context.
No install, no dependencies, no configuration. Language-agnostic — works with Python,
TypeScript, Dart, or whatever your stack is.

Per-stack commands (tool names, linter invocations, package manager syntax) live in
[`references/bindings/`](references/bindings/). A Flutter/Dart example is included.
Copy it to add your own stack.

---

## What's in the box

```
keelwright/
├── SKILL.md                    — the skill (load this)
├── assets/
│   ├── architecture.png        — visual map of all 28 risks + components
│   └── architecture.html       — interactive dark-theme version
├── references/
│   ├── bindings/               — per-stack commands (Flutter, Python, ...)
│   ├── circuit-breaker.md      — loop limits: budget, time, retry, rate
│   ├── security-gates.md       — R1-R12 implementation patterns
│   ├── reward-hacking-bait.md  — test-deletion trap + variants
│   ├── loop-audit-checklist.md — 7-principle checklist for existing loops
│   ├── qa-trap-catalog.md      — discriminating test catalog
│   └── ...                     — 20+ more references
├── templates/
│   └── qa-prompt-final.md      — autonomous QA prompt (runs unattended)
├── scripts/
│   ├── validate_run.py         — integrity gate for QA results
│   ├── workspace_guard.py      — read-only skill-tree isolation
│   └── snapshot_skill.py       — verify no foreign writes
└── qa-results/
    ├── README.md               — KDS scoreboard + methodology
    └── *.results.jsonl         — sanitized machine-verified run data
```

---

## Methodology

Every KDS result is produced by adversarial A/B testing:

1. **Control arm:** model runs the task without the skill
2. **Treatment arm:** model runs the same task with the skill loaded
3. **Verdict:** `DISCRIMINATES` if the skill changed the output in a meaningful way,
   `NO-DIFF` if the model already did it correctly without the skill
4. **Gate:** `validate_run.py` mechanically rejects fabricated results —
   PASS with `api_calls=0`, empty arm directories, false "identical" evidence

A `NO-DIFF` on a strong model is a good result — it means the skill doesn't get in the way.
A `DISCRIMINATES` means the skill added something the model wouldn't have done alone.

Weak models (KDS 0) fabricated results instead of running tests. The gate caught all of them.
This is documented in [`qa-results/README.md`](qa-results/README.md).

---

## License

[CC BY 4.0](LICENSE) — free for commercial use with attribution.

Structural patterns adapted from community loop-coding work (Ralph loop, execution-loop,
match-loop, autoresearch-loop — all MIT-0). All content written from scratch.
Full provenance in [`references/provenance.md`](references/provenance.md).

---



---

## Searchable keywords

AI code security, vibe coding safety, loop coding guardrails, AI agent protection,
ChatGPT code quality, Copilot security, Claude code review, AI coding best practices,
autonomous coding risks, AI hallucinated package, slopsquatting, AI deleted my tests,
reward hacking AI, SQL injection AI, hardcoded secrets AI agent, doom loop AI coding,
token burn protection, context rot AI, over-engineering AI, tech debt AI code,
spaghetti code AI, dead code detection, circular dependency AI, business logic review,
AI false report, regression detection, supply chain attack AI, AI code quality tool,
non-programmer coding, founder coding AI, no-code AI safety, AI guardrails tool,
self-healing code loop, circuit breaker AI agent, OWASP AI, AI security checklist

*keelwright by [ratingtesting](https://github.com/ratingtesting)*
