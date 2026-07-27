# Keelwright Publishing Registry
Goal: canonical KDS leaderboard on GitHub + cross-posting to drive stars.
Rule: every external publication must link back to `https://github.com/ratingtesting/keelwright`.

## Master Links
- GitHub repo: https://github.com/ratingtesting/keelwright
- HF Space: https://huggingface.co/spaces/ratingtesting/keelwright
- HF Discussion (live KDS table, edited): https://huggingface.co/spaces/ratingtesting/keelwright/discussions/1
- dev.to: https://dev.to/ratingtesting/my-ai-deleted-a-test-to-make-the-build-pass-so-i-built-28-safety-checks-to-stop-it-14mf

## Channels

### 1. Local artifacts (read/write)
- Path: `C:\Users\Unicorn\AppData\Local\hermes\skills\keelwright\` (Hermes skill folder)
- Files to sync: `README.md`, `qa-results/README.md`, `huggingface-card.md`, `devto-article-draft.md`, `index.html` (HF Space), `PUBLISHING_REGISTRY.md`, `habr-article-human.md`, `cover.png`
- Update rule: when KDS changes → edit local → push to all channels below

### 2. GitHub (DONE)
- Repo: ratingtesting/keelwright, branch master
- Auth: gh CLI (device flow, already done)
- Update: edit local `README.md` + `qa-results/README.md` → commit → `git push`
- Last updated: 2026-07-27 (12-model KDS table + Ling 22, MiMo 18, kimi-k3 25)

### 3. HuggingFace Space (DONE)
- Space: ratingtesting/keelwright
- Files: README.md (card), index.html (visual page with KDS table)
- Auth: HF token `API_HUGGINGFACE_KEY` from `C:\Users\Unicorn\AppData\Local\hermes\.env`
- Update: use proven commands below. Do NOT `git clone` whole repo for small edits; use `huggingface_hub` SDK for files and `edit_discussion_comment` for discussions.
- Last updated: 2026-07-27 (12-model KDS table + Discussion #1)

#### HF Proven Commands (tested 2026-07-27)
```python
from huggingface_hub import HfApi

with open(r"C:\Users\Hermes\AppData\Local\hermes\.env", "r") as f:
    token = next(line.strip().split("=", 1)[1] for line in f if line.startswith("API_HUGGINGFACE_KEY="))

api = HfApi(token=token)

# 1. Update README/README (card)
api.upload_file(
    path_or_fileobj=b"...",  # bytes or file path
    path_in_repo="README.md",
    repo_id="ratingtesting/keelwright",
    repo_type="space",
    commit_message="update KDS table",
)

# 2. Update index.html (visual page)
api.upload_file(
    path_or_fileobj=b"...",
    path_in_repo="index.html",
    repo_id="ratingtesting/keelwright",
    repo_type="space",
    commit_message="update KDS table on page",
)

# 3. Edit a discussion comment
details = api.get_discussion_details(
    repo_id="ratingtesting/keelwright",
    discussion_num=1,
    repo_type="space",
)
events = [e for e in details.events if e.type == "comment"]
first_comment = events[0]
api.edit_discussion_comment(
    repo_id="ratingtesting/keelwright",
    discussion_num=1,
    comment_id=first_comment.id,
    new_content="new markdown...",
    repo_type="space",
)
```
- ⚠️ gotcha: `Discussion` has no `get_comments()`. Use `details.events` and filter `type == "comment"`.
- ⚠️ gotcha: discussion edit requires explicit `repo_type="space"`.
- ⚠️ gotcha: main discussion post is a DiscussionComment event, not a Discussion object — this is the one to edit.

### 4. dev.to (DONE)
- Article ID: 4217414
- Auth: `API_DEV_TO_KEY` from `.env`
- Update: `PUT https://dev.to/api/articles/{id}` with full markdown body
- Last updated: 2026-07-27

### 5. HF Discussion #1 (DONE)
- Discussion num: 1, comment id: `6a629e7c9dba857834cf1000`
- Auth: same HF token
- Update: `api.edit_discussion_comment(repo_id, discussion_num=1, comment_id, new_content, repo_type="space")`
- ⚠️ gotcha: primary post is a DiscussionComment event, not a Discussion object; need `get_discussion_details` first, then `details.events`
- Last updated: 2026-07-27

### 6. habr.ru (PARTIAL — in Sandbox, awaiting moderation)
- Account: ratingtesting (registered 2026-07-27, status `readonly` due to new account)
- URL: https://habr.com/ru/sandbox/296542/ (submitted to Sandbox, awaiting moderation)
- Auth: email + password (human login)
- Update: manual via browser — `https://habr.com/ru/sandbox/new/`
- Article: `habr-article-human.md` (human-language rewrite, 1 GitHub link, cover.png 780x440)
- Status: SUBMITTED to Sandbox 2026-07-27. If approved → account becomes full-rights.
- Note: API blocked (readonly group); no automation possible. Human submits only.

### 7. vc.ru (DONE)
- Account: ratingtesting
- URL: https://vc.ru/ai/3049326-kak-founder-bez-programmirovaniya-predotvratil-udaleniye-testov-ii
- Auth: email + password (human login)
- Update: manual via browser — `https://vc.ru/editor`
- Article: same `habr-article-human.md` text, cover.png as cover
- Status: PUBLISHED 2026-07-27
- Note: API requires `access_token` from localStorage (cookies insufficient → 401 strict auth). Human publishes only.

### 8. skills.sh (WORKING, NOT YET PUBLISHED)
- URL: https://skills.sh
- Purpose: Open Agent Skills catalog (Vercel, 1M+ installs leaderboard)
- Auth: none for search; publish via GitHub PR in https://github.com/vercel-labs/skills
- Update command:
  ```bash
  # Publish path: owner/repo/slug → https://skills.sh/<owner>/<repo>/<slug>
  # Requires: push a repo with SKILL.md + optional scripts/assets to GitHub first
  ```
- Status: NOT YET PUBLISHED
- Note: Hermes can install from here (`hermes skills install skills.sh/<owner>/<repo>/<slug>`)

### 9. clawhub.ai (WORKING, NOT YET PUBLISHED)
- URL: https://clawhub.ai/skills/publish
- Purpose: OpenClaw agent skills registry (vector search, CLI)
- Auth: none for search; publish via `clawhub publish` CLI or web form at `/skills/publish`
- Update command:
  ```bash
  npm install -g @openclaw/clawhub
  clawhub publish ./keelwright-skill --type skill
  # OR via web form: https://clawhub.ai/skills/publish
  ```
- Status: NOT YET PUBLISHED
- Note: keelwright needs OpenClaw-compatible manifest (`package.json` + `SKILL.md`) for this

### 10. AgentSkills.io (WORKING, NOT YET PUBLISHED)
- URL: https://agentskills.io
- Purpose: Universal SKILL.md registry (spec-first, open standard)
- Auth: none for search; submit via GitHub PR in https://github.com/agentskills/agentskills
- Update command:
  ```bash
  # Fork https://github.com/agentskills/agentskills
  # Add skill under skills/<your-handle>/
  # PR with SKILL.md matching spec
  ```
- Status: NOT YET PUBLISHED

### 11. Cursor / Composer (no public catalog)
- URL: https://cursor.com
- Purpose: Cursor editor — no public skill/submission form found
- Update: promote via README/docs and community; no submit form
- Status: NOT STARTED

### 12. OpenAI GPT Store / Actions (TODO)
- URL: https://platform.openai.com
- Purpose: GPTs / Actions / Assistants catalog
- Auth: OpenAI account + API key
- Update: create GPT wrapper that loads keelwright instructions, with link to GitHub
- Status: NOT STARTED

### 13. Anthropic Claude Tool Use (TODO)
- URL: https://console.anthropic.com
- Purpose: no public "skill catalog"; Claude uses tool use / prompt-based instructions
- Update: publish Claude-optimized system prompt derived from keelwright with GitHub backlink
- Status: NOT STARTED

### 14. Reddit (blocked until stars)
- Target: r/ClaudeCode, r/ChatGPTCoding, r/LocalLLaMA, r/selfhosted
- Condition: need GitHub stars first
- Update: manual via browser or API
- Status: BLOCKED (stars < threshold)

### 15. Product Hunt (TODO)
- URL: https://www.producthunt.com
- Purpose: launch product, drive GitHub traffic
- Auth: need account
- Update: manual
- Status: NOT STARTED

### 16. Medium / HackerNoon (TODO)
- URL: https://medium.com, https://hackernoon.com
- Purpose: English long-form, SEO
- Auth: Medium — Google/Twitter OAuth (blocked in RU by RKN); HN — no account needed, email submit
- Update: manual publishing + GitHub link
- Status: NOT STARTED

## Publishing Proof Points
To avoid depending on unclear upstream catalog workflows:
- Main proof point is `https://github.com/ratingtesting/keelwright`
- All external pages MUST link back to GitHub
- Catalog presence is nice-to-have, not required for core launch

## Verified Formats
- skills.sh expects existing `SKILL.md` repo; not adding speculative workflows here
- AgentSkills.io is spec-only documentation; actual registry linking not verified for non-maintainer publish
- clawhub.ai publish flow not yet validated for this format

## Credentials (read-only, never log full token)
- HF: `API_HUGGINGFACE_KEY` in `C:\Users\Unicorn\AppData\Local\hermes\.env`
- dev.to: `API_DEV_TO_KEY` in same `.env`
- GitHub: gh CLI device flow (`~/bin/gh.exe`), user `ratingtesting`
