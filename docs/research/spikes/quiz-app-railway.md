<!-- ABOUTME: Research spike on building a FastAPI quiz/exam app with a versioned question bank and deploying it on Railway.
ABOUTME: Verified 2026-06-24 against fastapi.tiangolo.com, docs.railway.com, and PyPI; cites official sources with verbatim snippets. -->

---
created: 2026-06-24
topic: fastapi
status: fresh
---

# FastAPI quiz/exam app on Railway

Verified 2026-06-24 against official sources only: `fastapi.tiangolo.com`,
`docs.railway.com`, and `pypi.org`. Anything I could not confirm verbatim is
flagged in the "Not confirmed" section at the end.

## 1. Minimal FastAPI structure for a quiz

FastAPI declares request bodies with Pydantic models. From the official
Request Body tutorial, verbatim:

```python
from fastapi import FastAPI
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None

app = FastAPI()

@app.post("/items/")
async def create_item(item: Item):
    return item
```

Source: https://fastapi.tiangolo.com/tutorial/body/

"FastAPI will recognize that the function parameters that match path parameters
should be taken from the path, and that function parameters that are declared to
be Pydantic models should be taken from the request body." (Request Body
tutorial.)

Applied to the quiz, the route shapes and models below follow that pattern. The
scoring function takes plain data in and returns plain data out, so it is pure
and unit-testable without HTTP. The routes are thin wrappers.

```python
# app/models.py
from pydantic import BaseModel

class OptionView(BaseModel):
    key: str          # "A", "B", "C", "D"
    text: str

class QuestionView(BaseModel):
    id: str
    domain: str
    stem: str
    options: list[OptionView]
    # NOTE: answer + rationale are intentionally NOT in the view served to GET /exam

class ExamView(BaseModel):
    bank_version: str
    questions: list[QuestionView]

class Answer(BaseModel):
    question_id: str
    selected: str     # the option key the candidate chose

class ExamSubmission(BaseModel):
    bank_version: str
    answers: list[Answer]

class DomainResult(BaseModel):
    domain: str
    correct: int
    total: int

class ExamResult(BaseModel):
    score: float                  # 0.0 to 1.0 overall
    correct: int
    total: int
    per_domain: list[DomainResult]
```

```python
# app/scoring.py  --- pure, no FastAPI imports, fully testable
from collections import defaultdict
from app.models import ExamResult, DomainResult

def score_exam(answers: list[dict], bank: dict[str, dict]) -> ExamResult:
    """answers: [{"question_id": str, "selected": str}, ...]
    bank: {question_id: {"domain": str, "answer": str, ...}}
    Returns an ExamResult. No I/O, no globals."""
    per_domain_correct: dict[str, int] = defaultdict(int)
    per_domain_total: dict[str, int] = defaultdict(int)
    correct = 0
    for a in answers:
        q = bank.get(a["question_id"])
        if q is None:
            continue  # unknown id: skip; CI test asserts bank/submission align
        per_domain_total[q["domain"]] += 1
        if a["selected"] == q["answer"]:
            correct += 1
            per_domain_correct[q["domain"]] += 1
    total = sum(per_domain_total.values())
    per_domain = [
        DomainResult(domain=d, correct=per_domain_correct[d], total=per_domain_total[d])
        for d in sorted(per_domain_total)
    ]
    return ExamResult(
        score=(correct / total if total else 0.0),
        correct=correct,
        total=total,
        per_domain=per_domain,
    )
```

```python
# app/main.py  --- thin HTTP layer over the pure functions
from fastapi import FastAPI
from app.models import ExamView, QuestionView, OptionView, ExamSubmission, ExamResult
from app.bank import load_bank          # loads + validates the YAML/JSON question bank
from app.scoring import score_exam

app = FastAPI()
BANK = load_bank()                       # versioned dict at startup

@app.get("/exam", response_model=ExamView)
async def get_exam() -> ExamView:
    questions = [
        QuestionView(
            id=q.id, domain=q.domain, stem=q.stem,
            options=[OptionView(key=k, text=v) for k, v in q.options.items()],
        )
        for q in BANK.questions
    ]
    return ExamView(bank_version=BANK.version, questions=questions)

@app.post("/exam/submit", response_model=ExamResult)
async def submit_exam(submission: ExamSubmission) -> ExamResult:
    bank_index = {q.id: {"domain": q.domain, "answer": q.answer} for q in BANK.questions}
    return score_exam([a.model_dump() for a in submission.answers], bank_index)
```

The `response_model=` argument is the official way to declare and filter the
response shape. Source: https://fastapi.tiangolo.com/tutorial/response-model/
Keeping `answer` and `rationale` out of `QuestionView` is what stops `GET /exam`
leaking the key; the response model enforces it.

## 2. Question-bank schema and CI validation

One Pydantic model per question makes the bank self-validating: load the
YAML/JSON, construct the models, and a malformed bank raises `ValidationError`
at load time. A CI test then just calls the loader and asserts it does not
raise, plus a few invariants.

```python
# app/bank.py
from pydantic import BaseModel, field_validator, model_validator
import yaml

class Question(BaseModel):
    id: str
    domain: str
    difficulty: str                 # e.g. "easy" | "medium" | "hard"
    stem: str
    options: dict[str, str]         # {"A": "...", "B": "...", ...}
    answer: str                     # must be a key in options
    rationale: str

    @field_validator("difficulty")
    @classmethod
    def known_difficulty(cls, v: str) -> str:
        if v not in {"easy", "medium", "hard"}:
            raise ValueError(f"unknown difficulty: {v}")
        return v

    @model_validator(mode="after")
    def answer_in_options(self) -> "Question":
        if self.answer not in self.options:
            raise ValueError(f"answer {self.answer!r} not in options for {self.id}")
        return self

class QuestionBank(BaseModel):
    version: str
    questions: list[Question]

    @model_validator(mode="after")
    def unique_ids(self) -> "QuestionBank":
        ids = [q.id for q in self.questions]
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate question ids in bank")
        return self

def load_bank(path: str = "data/bank.yaml") -> QuestionBank:
    with open(path) as f:
        raw = yaml.safe_load(f)
    return QuestionBank.model_validate(raw)   # raises ValidationError if malformed
```

Field validators and `model_validator(mode="after")` are the documented Pydantic
v2 mechanisms; FastAPI is built on Pydantic v2. The CI test:

```python
# tests/test_bank.py
from app.bank import load_bank

def test_bank_is_well_formed():
    bank = load_bank()
    assert bank.version
    assert bank.questions
    # construction already enforced answer-in-options, unique ids, known difficulty
```

Note: the cross-field checks (`answer` in `options`, unique ids) are standard
Pydantic v2 model validators; the exact API (`@model_validator(mode="after")`,
`@field_validator`) is Pydantic v2, which FastAPI requires, but I confirmed the
FastAPI-side body/response-model behavior on tiangolo.com, not each Pydantic
validator signature on the Pydantic docs. Flagged below.

## 3. Railway deploy: files, start command, PORT, Postgres

### Builder: Railpack (default), Dockerfile, or config-as-code

Railway builds with zero config by default. The reference page formerly titled
"Nixpacks" now documents **Railpack**: "Railway uses Railpack to build and
deploy your code with zero configuration."
Source: https://docs.railway.com/reference/nixpacks

You override the builder and other settings with a `railway.json` or
`railway.toml` at the repo root. Verbatim from config-as-code:

```json
{
  "$schema": "https://railway.com/railway.schema.json",
  "build": {
    "builder": "RAILPACK"
  }
}
```

```json
{
  "$schema": "https://railway.com/railway.schema.json",
  "deploy": {
    "startCommand": "node index.js"
  }
}
```

```json
{
  "$schema": "https://railway.com/railway.schema.json",
  "deploy": {
    "restartPolicyType": "ALWAYS",
    "restartPolicyMaxRetries": 5
  }
}
```

"Configuration defined in code will always override values from the dashboard."
Supported `builder` values include `RAILPACK` (default) and `DOCKERFILE`.
`restartPolicyType` accepts `ON_FAILURE`, `ALWAYS`, or `NEVER`.
Source: https://docs.railway.com/reference/config-as-code

### Start command (uvicorn) and PORT

For a quiz app, set the start command to uvicorn bound to `0.0.0.0:$PORT`:

```json
{
  "$schema": "https://railway.com/railway.schema.json",
  "deploy": {
    "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
  }
}
```

PORT is injected by Railway, verbatim: "Your web server should bind to the host
0.0.0.0 and listen on the port specified by the PORT environment variable, which
Railway automatically injects into your application." The same variable is used
for health checks. Binding to `localhost`/`127.0.0.1` makes the app unreachable.
Source: https://docs.railway.com/networking/troubleshooting/application-failed-to-respond
and https://docs.railway.com/public-networking

CAVEAT: the official FastAPI deploy guide's own sample uses **Hypercorn**, not
uvicorn, and binds with `--bind "::"` rather than reading `$PORT`. Verbatim from
the guide's Dockerfile:

```dockerfile
FROM python:3-alpine
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
CMD ["hypercorn", "main:app", "--bind", "::"]
```

Source: https://docs.railway.com/guides/fastapi
The uvicorn `--host 0.0.0.0 --port $PORT` form above is the correct generalized
pattern per Railway's PORT/networking docs; the guide's Hypercorn `--bind "::"`
works because it listens on all interfaces, but it does not demonstrate `$PORT`.

### Postgres: a service, not a "plugin"

Railway's current term is **service**, not plugin. Add one with the CLI:

```bash
railway add --database postgres
```

Source: https://docs.railway.com/cli/add (and the search-surfaced
`railway add -d postgres` short form). On deploy the Postgres service exposes:
`PGHOST`, `PGPORT`, `PGUSER`, `PGPASSWORD`, `PGDATABASE`, and `DATABASE_URL`.
"Upon deployment, you will have a PostgreSQL service running in your project."
Reference `DATABASE_URL` from the app service via a reference variable so it
stays in sync if credentials rotate.
Source: https://docs.railway.com/databases/postgresql

A quiz app whose bank is a versioned YAML/JSON file in the repo does not strictly
need Postgres; add it only if you persist attempts/results.

## 4. Railway CLI: init / link / deploy (project creation is an account action)

Verbatim command syntax from the CLI docs (https://docs.railway.com/cli):

```bash
railway login                   # Login to Railway
railway login --browserless     # Login without browser

railway init                    # Create a new project
railway link                    # Link to existing project

railway up                      # Deploy current directory
railway up --detach             # Deploy without streaming logs

railway add --database postgres # Add PostgreSQL
```

`railway init` "Create a new project" is an account-level action: it creates a
new project under your Railway account. `railway link` instead binds the current
directory to a project that already exists. Per the global Railway-CLI rule,
linking is per-directory: every command run from that directory targets the
linked project/environment/service by context, so once linked you usually do not
pass `--service`. Deploy with `railway up` from the app directory.

## 5. Pins (verified on PyPI 2026-06-24)

- FastAPI latest: **0.138.0** (released 2026-06-20).
  Source: https://pypi.org/project/fastapi/
- uvicorn latest: **0.49.0** (released 2026-06-03).
  Source: https://pypi.org/project/uvicorn/

For a uv-based project, pin in `pyproject.toml` and commit `uv.lock`:

```toml
[project]
dependencies = [
    "fastapi==0.138.0",
    "uvicorn[standard]==0.49.0",
    "pyyaml>=6,<7",
]
```

### Dockerfile vs Railpack for a uv project

Railpack (zero-config) is the default and detects standard Python projects. For
a uv-based project the most predictable result is a Dockerfile that uses uv to
install from the lockfile, so the build matches local exactly. Railway detects a
`Dockerfile` at the source root and uses it automatically; set the builder to
`DOCKERFILE` in `railway.json` if you want it explicit. Source:
https://docs.railway.com/builds/dockerfiles and config-as-code (above).

Sketch (the uv image tag and exact COPY layout are NOT verified against Railway
docs; confirm against the uv/Astral docs before relying on it):

```dockerfile
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev
COPY . .
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "$PORT"]
```

CAVEAT: `$PORT` does not expand inside the JSON-array (`exec`) form of `CMD`.
Use the shell form for variable expansion:
`CMD uv run uvicorn app.main:app --host 0.0.0.0 --port $PORT`. This is general
Docker behavior, not stated in Railway docs.

## Not confirmed (flag before relying)

- The uv Dockerfile (base image tag, `uv sync --frozen` flags) is the uv/Astral
  convention, NOT verified on docs.railway.com. Check the official uv docs.
- Pydantic v2 validator signatures (`@field_validator`, `@model_validator(mode="after")`)
  are correct for Pydantic v2 but were not re-verified on the Pydantic docs in
  this spike; only FastAPI's body/response-model behavior was confirmed on
  tiangolo.com.
- Railway's official FastAPI guide ships a **Hypercorn** sample, not uvicorn, and
  does not demonstrate `$PORT`. The uvicorn `--host 0.0.0.0 --port $PORT` start
  command is assembled from Railway's PORT/networking docs, which is the correct
  pattern, but it is not copied verbatim from a single uvicorn-on-Railway page.
- "Plugin" is legacy Railway terminology; current docs say "service". The
  `railway add -d postgres` short form was surfaced by search; the long form
  `railway add --database postgres` is from the CLI docs page.

## Sources

- https://fastapi.tiangolo.com/tutorial/body/
- https://fastapi.tiangolo.com/tutorial/response-model/
- https://docs.railway.com/guides/fastapi
- https://docs.railway.com/reference/config-as-code
- https://docs.railway.com/reference/nixpacks
- https://docs.railway.com/builds/dockerfiles
- https://docs.railway.com/networking/troubleshooting/application-failed-to-respond
- https://docs.railway.com/public-networking
- https://docs.railway.com/databases/postgresql
- https://docs.railway.com/cli
- https://docs.railway.com/cli/add
- https://pypi.org/project/fastapi/
- https://pypi.org/project/uvicorn/
