# Testing Strategy

## Layers

| Layer | Tooling | What it covers |
|---|---|---|
| Unit — risk engine | pytest, no DB | Pure scoring/classification logic (Phase 3+) |
| Unit — authorization | pytest | `require_role` guard logic in isolation (`tests/test_authorization.py`) |
| API / integration | pytest + FastAPI TestClient | Endpoint behaviour, auth flows, expected success AND expected failure |
| Security regression | pytest | Specific "must never happen" assertions - e.g. username enumeration, missing-auth 401s |
| Static analysis | ruff, bandit | Lint + Python security anti-pattern scanning |
| Dependency scan | pip-audit | Known-CVE dependencies |
| Secret scan | gitleaks (CI) | Accidental credential commits |
| Frontend | `tsc --build` + `vite build` in CI | Type safety and build correctness |

## Why both SQLite and Postgres in CI

`tests/conftest.py` defaults to a local SQLite file so the full suite runs
in seconds with zero external services — useful during active development.
CI additionally runs the suite against a real Postgres service container
(see `.github/workflows/ci.yml`) so Postgres-specific behaviour (JSONB
columns, real foreign-key enforcement) is exercised before merge. See ADR
0002 for the reasoning.

## Running locally

```bash
cd backend
pip install -r requirements-dev.txt
pytest                      # fast path, SQLite
ruff check .
bandit -r app -x tests
```

## A caught gotcha: verifying against a stale Docker image

While verifying Phase 6 end to end, `docker compose up -d` reused existing
containers after a Docker Desktop restart interrupted a prior build,
silently serving the *previous* phase's image (new endpoints 404'd even
though the code was committed and unit-tested). The fix: after any Docker
Desktop restart during active development, rebuild with `--no-cache` and
recreate with `--force-recreate` rather than trusting `docker compose up
-d --build` to detect staleness on its own - then re-verify with a direct
`docker exec ... ls` check that the expected new file is actually present
in the running container before treating the phase as verified. Recorded
here because it's exactly the kind of gap that unit tests alone (all
passing throughout) could not have caught - only an actual end-to-end run
surfaced it.

## What "expected failure" tests look like here

Every auth-sensitive feature has at least one test asserting the request
is correctly *rejected*, not just that valid requests succeed — see
`tests/test_auth.py` (wrong password, unknown user, inactive account,
missing/invalid token) and `tests/test_authorization.py` (wrong role).
This pattern continues in every subsequent phase: an API test file is not
considered complete with only happy-path assertions.
