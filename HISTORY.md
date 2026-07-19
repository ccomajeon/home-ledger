# HISTORY

This file is the compact working log for agent-driven development.
Read the latest entries first to reduce context usage.

## Entry Template

- Date: YYYY-MM-DD HH:mm (local)
- Files: path1, path2
- Summary: what changed
- Tests: command -> pass/fail (or not run)
- Next: next planned step

## 2026-07-20 00:58 (local)

- Files: `.gitignore`, `backend/*`, `frontend/*`, `scripts/*`, `README.md`, `RELEASE.md`, `HISTORY.md`
- Summary: Added the Argon2-backed `SYSTEM` local OWNER login, login throttling, auth capability discovery, and a full modern responsive redesign for the login shell and finance dashboard. Hardened the one-command build harness to stop on every failed native command.
- Tests: `scripts/build.ps1` passed with backend Black/Ruff and Pytest 16 passed, frontend Prettier/ESLint and Vitest 4 passed, Vite production build passed, and npm audit 0 vulnerabilities; `scripts/smoke.ps1 -Port 8766` passed; live browser login, OWNER admin access, desktop/mobile layout, and console errors verified.
- Next: Review the final secret-safe diff, commit the release, then push when GitHub authentication is available.

## 2026-07-19 23:02 (local)

- Files: `backend/*`, `frontend/*`, `scripts/*`, `README.md`, `RELEASE.md`, `HISTORY.md`
- Summary: Completed the v0.2.0 household-ledger MVP with Google OAuth sessions, ledger CRUD and summaries, settings, OWNER administration, audit logging, SQLite backup/restore, responsive UI, and one-command build/start harnesses.
- Tests: `scripts/build.ps1` -> pass; backend `pytest` 14 passed; Ruff/Black passed; frontend ESLint/Vitest 4 passed/Vite build passed; `npm audit` 0 vulnerabilities; `scripts/smoke.ps1` -> API and frontend pass.
- Next: Review the final diff, commit the release, push the feature branch, and open a draft PR.

## 2026-03-03 22:58 (local)

- Files: AGENTS.md, HISTORY.md
- Summary: Added mandatory history logging policy to AGENTS and created HISTORY.md baseline template.
- Tests: not run
- Next: Continue feature work while appending concise entries after each meaningful step.

## Backfilled Timeline (2026-03-03)

### 2026-03-03 22:12 (local)

- Files: repository baseline
- Summary: Remote repository initial commit exists (`8d66756`).
- Tests: not run
- Next: Create project skeleton for backend/frontend/scripts.

### 2026-03-03 22:22 (local)

- Files: root, `backend/*`, `frontend/*`, `scripts/*`, `.codex/config.toml`
- Summary: Added household ledger project skeleton (`8e5da59`) including FastAPI and React/Vite structure, env examples, and script stubs.
- Tests: not run
- Next: Align ignore policy for internal planning files and push safely.

### 2026-03-03 22:17-22:24 (local)

- Files: `.gitignore`, index state
- Summary: Applied ignore policy for `AGENTS.md` and `PROJECT_SPECIFICATION.md` and committed (`998f926`). Rebase conflict occurred on `README.md` during sync with remote, conflict resolved, rebase completed, then pushed.
- Tests: git rebase/push flow completed successfully
- Next: Finalize public-facing README language/tone.

### 2026-03-03 22:25 (local)

- Files: `README.md`
- Summary: Rewrote root README for public-facing Korean documentation and pushed commit (`300a690`).
- Tests: not run
- Next: Keep docs concise, avoid exposing internal process details.

### 2026-03-03 22:58 (local)

- Files: `AGENTS.md`, `HISTORY.md`
- Summary: Added mandatory HISTORY logging policy and created this file template for context-efficient continuation.
- Tests: not run
- Next: Append one concise entry after each meaningful implementation step.

## 2026-03-03 22:36 (local)

- Files: `AGENTS.md`, `RELEASE.md`, `HISTORY.md`
- Summary: Added mandatory release-note policy in AGENTS and created root RELEASE.md with version/date/new/improved/fixed structure plus initial `v0.1.0` entry.
- Tests: not run
- Next: Before each push, append a new release entry and include RELEASE.md in the same commit.

## 2026-03-03 22:40 (local)

- Files: `AGENTS.md`, `RELEASE.md`, `HISTORY.md`
- Summary: Added mandatory Korean policy for release notes in AGENTS and translated RELEASE.md content/template to Korean (`신규`, `개선`, `오류수정`).
- Tests: not run
- Next: Keep release entries updated in Korean before every push.

## 2026-03-03 22:41 (local)

- Files: `RELEASE.md`, `HISTORY.md`
- Summary: Added `v0.1.1` release entry for this push and synchronized history log with the release-process update.
- Tests: not run
- Next: Commit and push both logs together.
