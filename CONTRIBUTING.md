# Contributing

## How to contribute

1. Fork the repo and create a branch from `main`.
2. Add or update tests in `tests/` (synthetic data only — no network).
3. Keep user-facing text bilingual (`ko`/`en`) where applicable.
4. Open a pull request. CI runs `pytest` on Python 3.9–3.12.

## What we look for

- New indicators: reference the definition (e.g. Wilder 1978) in the
  docstring and add a test with known values or bounds.
- New rules: must be explainable in one sentence and covered by
  `describe_signals`.
- No investment-advice language anywhere — observations only.

## Maintainer workflow

PRs get an automated review pass (tests + behavioral summary) before human
review. See `docs/maintainer-workflow.md`.
