---
title: keelwright — 28 machine-enforced safety checks for AI-generated code
emoji: 🛡️
colorFrom: green
colorTo: blue
license: cc-by-4.0
sdk: static
pinned: false
---

# 🛡️ keelwright

**Engine for vibe-coders and loop-coders who ship AI-generated code they can't read line by line.**

## The problem

You use AI to write code. You can't review it line by line. Somewhere in that code:

- SQL injection in database queries
- Hardcoded API keys and passwords
- Hallucinated package names installing malware (slopsquatting)
- AI deleted a test to make the build pass (reward hacking)
- Infinite loops burning $50-200 in tokens overnight (doom loop)
- AI removed a validation check instead of fixing it

## What keelwright does

28 machine-enforced safety checks that run automatically on every iteration:

| Category | Checks |
|---|---|
| **Security (R1-R12)** | SQL injection, hardcoded secrets, slopsquatting, missing auth, business logic bypass, OWASP top 10 |
| **Code quality** | Reward hacking, over-engineering, tech debt, false reports, dead code, circular dependencies |
| **Agent safety** | Doom loop circuit-breaker (50 iters / 2h / $cap), token burn prevention, context rot, goal drift |

## Keelwright Score (KDS)

KDS measures how much the skill changes a model's behavior on real A/B tests.

**KDS = Execution Rate × Discrimination Rate / 100** (0-100 scale)

| Model | Tier | SWE-bench | KDS |
|---|---|---|---|
| poolside/laguna-s-2.1 | STRONG | ML 78.5% | **83** |
| stepfun/step-3.7-flash | MEDIUM | Pro ~56% | **67** |
| nvidia/nemotron-3-ultra | STRONG | ML 67.7% | **40** |
| deepseek-v4-flash | STRONG | Verified ~79% | **29** |
| claude-opus-4-8 | STRONG | frontier | **17** |
| tencent/hy3 | STRONG | ML 75.8%, Verified 78% | **7** |
| cohere/north-mini-code | WEAK | Agentic 3.1 | **0** |

**Key findings:**
- Medium models (Step 3.7, KDS 67) get MORE value from the skill than some strong models
- Weak models (KDS 0) can't execute A/B tests — they fabricate results instead
- All results verified on disk with `validate_run.py`

## How to use

1. Load the keelwright skill into your AI coding session
2. That's it — no install, no dependencies, no configuration

## Links

- **GitHub:** [ratingtesting/keelwright](https://github.com/ratingtesting/keelwright)
- **Architecture:** [Interactive diagram](https://ratingtesting.github.io/keelwright/assets/architecture.html)
- **QA data:** [Verified A/B test results](https://github.com/ratingtesting/keelwright/tree/master/qa-results)
- **Dev.to:** [Full article](https://dev.to/ratingtesting/my-ai-deleted-a-test-to-make-the-build-pass-so-i-built-28-safety-checks-to-stop-it-14mf)

## License

CC BY 4.0 — free for commercial use with attribution.
