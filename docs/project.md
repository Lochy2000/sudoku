Phase 0 — Project bootstrap

Goals

Create a clean, reproducible dev environment.

Establish mono-/multi-app layout, config, and QA baseline.

Tasks

Repo init with Python 3.12.

Tooling: ruff (lint), mypy (typing), pytest (tests), pre-commit.

Docker compose (web, postgres, redis if using Celery/Channels later).

Django project sudoku_site/ and apps: accounts/, puzzle/.

Settings split: base.py, dev.py, prod.py; .env handling.

Basic CI (GitHub Actions): run lint, type check, tests.

Deliverables

docker-compose.yml, Dockerfile, pyproject.toml or requirements/*.txt

Django project with INSTALLED_APPS wired, Postgres connection, migrations ready.

Pre-commit hooks configured.

DoD

docker compose up brings DB + app up; pytest passes a hello-world test; CI green.

Phase 1 — Domain modeling & DB schema

Goals

Lock in data structures for puzzles and sessions across multiple grid sizes.

Tasks

Models in puzzle/models.py:

PuzzleTemplate(id, size, box_h, box_w, givens, solution, difficulty_metric, difficulty_label, source, created_at)

GameSession(id, user(FK|nullable), puzzle(FK), board_state(JSON), pencil_marks(JSON), mistakes_count, time_seconds, status, started_at, updated_at, completed_at)

DailyChallenge(date, puzzle(FK), created_at)

Constraints & indexes:

Index (size, difficulty_label) on PuzzleTemplate.

Unique (date) on DailyChallenge.

Admin registrations with useful list filters.

Deliverables

Initial migration + ERD diagram (even a text ERD in README).

Field-level docstrings describing serialization formats (e.g., board as 1D string vs JSON).

DoD

Migrations apply cleanly; admin shows models; unit tests can create/save instances.

Phase 2 — Sudoku engine abstraction

Goals

Decouple generation/solving from Django; support multiple engines and sizes.

Tasks

Create puzzle/services/engines/:

base.py: class Engine(ABC) with generate(size, difficulty), solve(grid), has_unique_solution(grid), rate_difficulty(grid) contracts.

dokusan_engine.py (initially for 9×9).

dlx_engine.py for generalized sizes (4×4, 6×6, 9×9). (DLX for uniqueness; simple backtracking+MRV for generation.)

Engine selector puzzle/services/factory.py that picks based on (size, source); configurable via settings.

Deterministic seeding option for reproducible tests (accept seed).

Deliverables

Engine interface + at least one working stub with tests (e.g., solve a known easy 9×9, confirm uniqueness).

DoD

Tests can call Engine.generate(9, 'medium') and get a uniquely solvable grid + solution.

Phase 3 — Puzzle generation pipeline & seeders

Goals

Persist re-usable puzzles; support pre-generation queues.

Tasks

puzzle/services/generation.py:

generate_template(size, difficulty, source) → PuzzleTemplate.

Validates uniqueness via Engine.has_unique_solution.

Computes/stores difficulty_metric and maps → difficulty_label.

Management commands:

python manage.py seed_puzzles --size 9 --difficulty medium --count 200 --source dokusan

python manage.py clear_puzzles (safe guard in non-prod).

Data validation tests (every saved template is valid & unique).

Deliverables

Populated DB with sample templates for 9×9 across difficulties.

DoD

Seeder produces requested count; random spot-check test validates uniqueness and solution correctness.

Phase 4 — Game lifecycle: create, save, resume, complete

Goals

CRUD lifecycle for an individual play-through.

Tasks

Services:

start_game(user, template_id) → GameSession with initial board_state = givens.

apply_move(game_id, cell_index, value, mode='number'|'pencil') (service updates state; pencil marks maintain set semantics).

validate_board(game_id) — compare against PuzzleTemplate.solution.

complete_game(game_id) — set status & timestamps.

Server-side enforcement rules:

Disallow changing givens.

Enforce valid number range (1–size).

Optional: return conflict info (row/col/box duplicates).

Deliverables

Unit tests for lifecycle and edge cases (invalid moves, out-of-range, editing givens).

DoD

Test creates a game, plays some moves, saves, reloads, completes successfully.

Phase 5 — Auth & accounts

Goals

Secure sessions; allow guest → user upgrade later (optional).

Tasks

Use Django auth; custom user optional (future social login).

Signup/login/logout endpoints; password validators; email normalization.

Optional: allow anonymous game start and link session → user on login.

Deliverables

Auth views (or DRF auth endpoints if using API-first).

Tests for auth flows.

DoD

Auth works locally; protected endpoints blocked unauthenticated.

Phase 6 — API (or views) for gameplay

Goals

Clean contract for frontends (htmx or SPA).

Tasks

If DRF:

POST /api/puzzles/ → get random template by size & difficulty (uses queue or on-demand).

POST /api/games/ → start from template id.

GET /api/games/{id} → current state.

PUT /api/games/{id} → save board_state, pencil_marks, time_seconds, status.

POST /api/games/{id}/check → board validation.

GET /api/daily/{YYYY-MM-DD} → daily puzzle & user’s session if exists.

If htmx: mirror endpoints as server-rendered partials with CSRF headers set.

Deliverables

OpenAPI schema (DRF Spectacular) or API docs page; Postman collection.

DoD

Contract tested via API tests; schema builds without errors.

Phase 7 — Daily challenge & streaks

Goals

One puzzle per day per size/difficulty (choose one for MVP), track streaks later.

Tasks

create_daily_challenge(date, size, difficulty) service that picks/creates a PuzzleTemplate & saves in DailyChallenge.

Management command: seed_daily_challenges --start 2025-09-01 --days 30 --size 9 --difficulty medium.

Endpoint to fetch today’s challenge; ensure idempotence.

Deliverables

Daily challenge populated for N days ahead.

Basic leaderboard table (to fill later).

DoD

Today’s endpoint returns a stable puzzle; creating twice doesn’t duplicate.

Phase 8 — Hints & human-technique checks (optional in MVP)

Goals

Provide logic-based hints (singles, pairs, etc.) and difficulty verification.

Tasks

Extend engine to expose “next logical step” if available (singles-first policy).

POST /api/games/{id}/hint returns a structured hint (cell(s), operation, technique).

Deliverables

Hint service with at least single-candidate hints; logs technique usage for analytics.

DoD

Tests assert that on known positions, hint returns the expected step.

Phase 9 — Smaller grids (4×4, 6×6)

Goals

Support non-9×9 boards with correct sub-box definitions.

Tasks

Generalize board indexing helpers for box_h × box_w.

Add engines for smaller sizes (DLX-based uniqueness + generator).

Update validation and move rules to use dynamic size.

Deliverables

Seeders produce 4×4 and 6×6 templates.

API accepts size parameter.

DoD

Test suites pass for 4×4 & 6×6 generation, play, and completion.

Phase 10 — Undo/redo & integrity

Goals

Robust editing model with time and mistake tracking.

Tasks

Client-side undo/redo stack spec (we can store snapshots server-side at save points).

Server sanity checks on incoming board: reject illegal changes to givens; normalize pencil marks.

Mistake rules: optionally track wrong entries vs conflicts vs check-on-demand only.

Deliverables

Validation service that returns granular error types.

DoD

Tests simulate bad updates and receive consistent errors; legal updates persist.

Phase 11 — Admin & ops tools

Goals

Operability for non-devs.

Tasks

Admin list filters: by size/difficulty, created_at, source.

Admin actions: validate selected templates; export/import puzzles (CSV/JSON).

Dashboard page: puzzle queue levels per (size,difficulty); button to trigger seeders.

Deliverables

Admin utilities + docs.

DoD

Staff can see queue depth and regenerate batches without shell.

Phase 12 — Background jobs (optional but recommended)

Goals

Keep puzzle queues full and daily challenges scheduled.

Tasks

Celery + Redis.

Periodic tasks:

Refill queue when below watermark (e.g., min 100 per bucket).

Pre-create daily challenges 14 days ahead.

Observability: task logging, retry policy, alerts on failures.

Deliverables

Celery beat schedule; Grafana/Prometheus optional.

DoD

Killing the queue triggers refill automatically; daily jobs populate future dates.

Phase 13 — Observability, metrics, analytics

Goals

See how players use difficulty levels; tune ratings.

Tasks

Structured logs (JSON) for game events (start, hint, complete).

Metrics: avg time per difficulty, hint usage, abandon rate.

Feature flags for A/B (difficulty thresholds, hint types).

Deliverables

Lightweight analytics store (Postgres tables or a simple events table).

Admin charts (optional) or export script.

DoD

Can query “avg time for 9×9 medium last 7 days” from DB.

Phase 14 — Security & compliance hardening

Goals

Ship a safe app.

Tasks

CSRF for forms/htmx; session config (HTTPOnly, Secure cookies).

Rate limit puzzle creation endpoints (simple cache throttle).

Input validation for all APIs; schema validation (pydantic or DRF serializers).

Backups for Postgres (dev instruction + cron in prod).

Deliverables

Security checklist in repo; threat model notes (basic).

DoD

Automated tests cover auth-required endpoints; rate limits verified.

Phase 15 — Minimal UI scaffolding (to exercise backend)

Goals

Thin UI to test flows before a full design.

Tasks

Server-rendered HTML (Django templates) or tiny HTMX layer:

New Game form (size, difficulty).

Board renderer (table/div grid), number/pencil toggles.

Save/Resume and “Daily” page.

Keyboard shortcuts (1–9, arrows) — minimal.

Deliverables

Basic playable page hitting real endpoints.

DoD

You can start, play, save, resume, and complete a puzzle entirely through the minimal UI.

Phase 16 — Performance & scale checks

Goals

Ensure generation and API are responsive.

Tasks

Load test puzzle fetch, game save, and validation endpoints.

Cache static templates (read-heavy) if needed.

Confirm generators run in background; on-demand has sane timeouts.

Deliverables

K6/Locust scripts; profiling notes.

DoD

Under expected load (e.g., 200 RPS reads, 20 RPS writes), API < p95 300ms on reads, < 800ms on writes (tune to your target).

Cross-cutting standards (apply throughout)

Config via env: engine choices per size, difficulty thresholds, queue watermarks.

Strict typing on services; dataclasses/pydantic models for engine I/O.

Test fixture library: known valid puzzles for 4×4/6×6/9×9; golden files for hint steps.

Serialization format:

Boards: 1D string ("0" for empty) or flat list; always include size, box_h, box_w.

Pencil marks: {cell_index: [ints...]} with indices 0..(size*size-1).

Difficulty mapping: Central config file that maps engine metric → label; make it A/B tunable.

Suggested repo layout
/sudoku
  /sudoku_site/               # Django project
    settings/
      base.py
      dev.py
      prod.py
  /accounts/
  /puzzle/
    admin.py
    models.py
    api/                      # DRF views/serializers OR views/partials for htmx
    services/
      engines/
        base.py
        dokusan_engine.py
        dlx_engine.py
      factory.py
      generation.py
      gameplay.py             # start_game, apply_move, validate, complete
      validation.py           # conflict checks, legality
    management/
      commands/
        seed_puzzles.py
        seed_daily.py
        clear_puzzles.py
  /ops/
    erd.md
    runbooks.md
/tests/
  /unit/
  /integration/
  /api/

Rollout order (fastest path to “playable”)

Phases 0–3 (bootstrap, models, engine abstraction, generation + seeding for 9×9).

Phase 4 + 6 (game lifecycle + API).

Phase 5 (auth).

Phase 7 (daily challenge).

Phase 15 (minimal UI to verify end-to-end).

Phase 9 (smaller grids), 8 (hints), 12–14 (jobs, analytics, security), 16 (perf).