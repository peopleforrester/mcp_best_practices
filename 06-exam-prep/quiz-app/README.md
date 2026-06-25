<!-- ABOUTME: The MCP exam quiz app: a validated question bank, pure scoring, and a FastAPI service.
ABOUTME: Tested offline with the FastAPI TestClient; Railway deploy is config-only until approved. -->

# MCP Exam Quiz App

A small FastAPI service that administers an MCP exam.

- `questions.yaml` : the versioned question bank, validated on load (`models.Question` checks that
  each answer is one of its options).
- `scoring.py` : `score_exam(questions, answers)`, a pure function returning totals, a percentage,
  and a per-domain breakdown.
- `app.py` : `GET /` serves a minimal browser quiz UI, `GET /exam` serves questions without answers,
  `POST /exam/submit` scores a submission, `GET /health` for the platform health check, and FastAPI's
  `GET /docs` gives an interactive API explorer. `create_app()` builds it; module-level `app` is the
  uvicorn entrypoint.
- `static/index.html` : the vanilla-JS frontend (no build step) that loads `/exam`, renders radio
  options, and posts to `/exam/submit` to show a scored, per-domain result.

```bash
uv run pytest -q
uv run ruff check .
uv run uvicorn mcp_quiz.app:app --reload   # local dev at http://127.0.0.1:8000
```

## Railway deploy (live)

Deployed on Railway: **https://mcp-exam-quiz-production.up.railway.app**
(`/health`, `/exam`, `/exam/submit`). Project `mcp-exam-quiz`, production environment.

`railway.json` configures a Railpack build with the uvicorn start command bound to `0.0.0.0:$PORT`
and `/health` as the healthcheck. Railpack detects the uv project from `uv.lock` and runs
`uv sync --locked`. Results storage would use a Railway Postgres service exposing `DATABASE_URL`
(not wired yet; scoring is currently stateless).

Redeploy after changes from this directory:

```bash
railway up             # deploy the current directory to the linked service
railway add -d postgres # optional: add a Postgres service for results
```

The directory is linked per-machine (`~/.railway/config.json`); on another machine,
`railway link --project mcp-exam-quiz` re-binds it.
