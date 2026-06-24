<!-- ABOUTME: The MCP exam quiz app: a validated question bank, pure scoring, and a FastAPI service.
ABOUTME: Tested offline with the FastAPI TestClient; Railway deploy is config-only until approved. -->

# MCP Exam Quiz App

A small FastAPI service that administers an MCP exam.

- `questions.yaml` : the versioned question bank, validated on load (`models.Question` checks that
  each answer is one of its options).
- `scoring.py` : `score_exam(questions, answers)`, a pure function returning totals, a percentage,
  and a per-domain breakdown.
- `app.py` : `GET /exam` serves questions without answers, `POST /exam/submit` scores a submission,
  `GET /health` for the platform health check. `create_app()` builds it; module-level `app` is the
  uvicorn entrypoint.

```bash
uv run pytest -q
uv run ruff check .
uv run uvicorn mcp_quiz.app:app --reload   # local dev at http://127.0.0.1:8000
```

## Railway deploy (config only)

`railway.json` configures a Railpack build with the uvicorn start command bound to `0.0.0.0:$PORT`
and `/health` as the healthcheck. Results storage would use a Railway Postgres service exposing
`DATABASE_URL` (not wired yet; scoring is currently stateless).

Creating and linking the Railway project is an account-level action. The commands, once approved:

```bash
railway init           # creates the project (account action)
railway link           # bind this directory
railway up             # deploy
railway add -d postgres # optional: add a Postgres service for results
```
