# Reddit r/ChatGPTCoding — draft post (v2, audit-fixed)

**Title:** AI deleted my payment validation tests. Here is the open-source safety net I built (28 checks, adversarially tested, all data public)

---

I'm a non-developer founder. I use AI for almost everything — including writing code.

Over the last few months, I've seen recurring failure patterns in AI-generated code:

- The AI quietly removed a test that validates payment amounts
- It hardcoded my Stripe API key in the source code
- It installed a package called `reuests` instead of `requests` — one letter off, and it's malware
- It ran in an infinite loop for 6 hours, burning $80 in tokens
- It "fixed" a bug by deleting the test that caught it

I can't catch any of this. Not because I'm not smart — because I can't read the code.

So I built an open-source tool called keelwright — 28 machine-enforced safety checks that run automatically on every AI coding iteration. Not suggestions. Hard gates.

**What it catches:**
- SQL injection, hardcoded secrets, hallucinated packages (slopsquatting)
- Reward hacking (AI deletes tests), doom loops (infinite token burn)
- False reports, over-engineering, missing auth, business logic bypasses

**The interesting part:** I ran adversarial A/B tests across 6 models and created a metric called KDS (Keelwright Score) — measures how much the skill actually changes behavior:

| Model | KDS |
|---|---|
| Laguna S 2.1 (SWE-bench 78%) | 83 |
| Step 3.7 (medium) | 67 |
| Nemotron 3 Ultra | 40 |
| DeepSeek V4 Flash | 29 |
| Claude Opus 4.8 | 17 |
| Hy3 (SWE-bench 78%) | 7 |

Medium models benefit MORE than some strong ones — they score low on R1 (SQL injection) and R8 (slopsquatting), and the skill short-circuits both before code is written.

All results verified on disk with a public integrity gate. Raw data: `qa-results/README.md` in the repo.

GitHub: https://github.com/ratingtesting/keelwright
Full article: https://dev.to/ratingtesting/my-ai-deleted-a-test-to-make-the-build-pass-so-i-built-28-safety-checks-to-stop-it-14mf

---

**EDDIT — full links for those who asked:**
- Architecture diagram: https://ratingtesting.github.io/keelwright/assets/architecture.html
- QA methodology + how to reproduce: `templates/qa-prompt-final.md`
