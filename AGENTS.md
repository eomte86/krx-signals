# AGENTS.md — krx-signals

Instructions for AI coding agents working in this repository.

## Project

`krx-signals`: rules-based technical analysis signals for Korean equities.
Pure-pandas indicators + a small explainable rules engine. No TA-Lib.

## Rules

1. **Never add investment-advice language.** Signals are technical
   observations. Docstrings, README text, and `describe_signals` output
   must describe *what happened* (which conditions triggered), never what
   the user should do.
2. **No network in tests.** All tests use deterministic synthetic data.
   `data.py` (pykrx adapter) is excluded from unit tests; it is an
   optional integration path.
3. **Keep the dependency footprint small.** Core = pandas + numpy only.
   New data sources go behind optional extras.
4. **Bilingual user-facing text.** Public docs and `describe_signals`
   support `lang="ko"` / `lang="en"`. Keep both in sync.
5. **Conventions:** type hints on public functions, Google-style
   docstrings, `pytest` tests for every new indicator/rule.

## Maintainer workflow (Codex-assisted)

- PR review: run the full test suite; summarize behavioral changes in the
  PR body; flag any new investment-advice-adjacent wording.
- Release notes: draft from commit messages, grouped by
  features/fixes/docs.
- Issue triage: label by area (`indicators`, `signals`, `data`, `docs`),
  reproduce with a synthetic-data script before fixing.

See `docs/maintainer-workflow.md` for the full workflow this project
intends to run on its API credits.
