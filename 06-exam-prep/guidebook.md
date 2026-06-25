<!-- ABOUTME: Guidebook for the Exam Prep track: an ordered curriculum and a deployable quiz app.
ABOUTME: The curriculum is the study path; the quiz app tests it and ships with Railway config. -->

# Exam Prep Guidebook

A learning track with two parts: a curriculum that defines what to know, and a quiz app that tests it.

## The curriculum (`curriculum/`)

`curriculum/README.md` is the ordered study path: thirteen modules from primitives (JSON-RPC,
lifecycle, transports) through systems (architecture, the registry) to the deep lane (authorization,
OWASP MCP Top 10, the NSA CSI) and the ecosystem. Each module maps to a portfolio competency, so the
study path and the code tracks line up. The fully sourced version is in
`docs/research/exam-curriculum-2026-06-23.md`.

## The quiz app (`quiz-app/`)

A FastAPI service that administers the exam:

- The question bank (`questions.yaml`) is versioned content, validated on load. It is authored to a
  researched item-writing rubric, not improvised: `docs/research/spikes/exam-item-writing.md` (the
  Haladyna and NBME multiple-choice guidelines plus the Linux Foundation associate-exam style) and
  `docs/research/spikes/mcp-question-content.md` (sourced, defensible answer keys per domain). The
  rubric is partly enforced in code: `models.Question` requires exactly four distinct options, the
  answer among them, and a rationale long enough to explain the distractors; `tests/test_quality.py`
  gates the bank on answer-position balance, an application-over-recall lean, and the key not being
  systematically the longest option (the test-wiseness tell). Every rationale explains why the key is
  correct and why each distractor is wrong.
- Scoring (`scoring.py`) is a pure function: it returns the total, a percentage, and a per-domain
  breakdown, with no IO. That is what makes it unit-testable and reusable by the API.
- The API (`app.py`) serves questions without the answer key (`GET /exam`), scores a submission
  (`POST /exam/submit`), and exposes `GET /health`. The taker never receives the answer or rationale,
  enforced by serving a `QuestionView` rather than the `Question`.

The tests cover the bank (loads, unique ids, answers valid), the scoring (perfect, zero, per-domain
totals), and the API (answers hidden, submission scored). Test output is pristine; a third-party
Starlette deprecation warning is filtered.

## Deploying on Railway

`quiz-app/railway.json` configures a Railpack build and a uvicorn start command bound to
`0.0.0.0:$PORT`, with `/health` as the healthcheck. The app reads `PORT` from the environment, which
Railway injects. Persisting results would add a Railway Postgres service (`DATABASE_URL`); scoring is
stateless today.

Creating and linking the Railway project is an account-level action, so it is left for an explicit
go-ahead. The commands are in `quiz-app/README.md`.

## Run it

```bash
cd 06-exam-prep/quiz-app
uv run pytest -q
uv run uvicorn mcp_quiz.app:app --reload
```
