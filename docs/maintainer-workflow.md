# Maintainer workflow (AI-assisted)

`krx-signals` is maintained with an AI-assisted workflow. This document
describes how API credits (e.g. via the Codex for OSS program) are used
in this project's maintenance. It is also the draft source for the
"API credits usage plan" field of that application.

## 1. Automated PR review

Every pull request gets an automated review pass before human review:

- run the full `pytest` suite on the CI matrix (Python 3.9–3.12),
- summarize behavioral changes (new indicators, rule changes, API changes)
  in the PR body,
- flag any wording that reads as investment advice — this project only
  publishes technical observations,
- check that new public functions have type hints, docstrings, and tests.

## 2. Release automation

Release notes are drafted from commit messages, grouped into
features / fixes / docs, in Korean and English. Version bumps follow
SemVer; the notes always link the full diff.

## 3. Issue triage

New issues are labeled by area (`indicators`, `signals`, `data`,
`docs`). Reproduction scripts use synthetic data only (no network), so
triage is fast and hermetic.

## 4. Security review

Dependencies are minimal by design (pandas + numpy). Automated review
includes a dependency and code-pattern scan on every PR; findings are
filed as issues with a proposed patch, never auto-merged.

## Why this matters

The maintainer is a solo developer. Automating review, triage, and
release chores is what makes sustained maintenance of a niche,
Korea-market-focused library feasible — the exact burnout problem these
programs aim to solve.
