# Sudoku Django App — Project Plan

This document outlines the phased implementation plan for the Sudoku web & mobile app built with **Django**.  
The project will support multiple grid sizes (4×4, 6×6, 9×9), difficulty levels, user authentication, saved sessions, and daily challenges.

---

## Phase 0 — Project Bootstrap
**Goals**
- Set up a reproducible dev environment and CI/CD.

**Tasks**
- [ ] Initialize repo with Python 3.12.
- [ ] Add tooling: `ruff`, `mypy`, `pytest`, `pre-commit`.
- [ ] Add Docker Compose (Django, Postgres, Redis optional).
- [ ] Create Django project `sudoku_site/` with apps: `accounts/`, `puzzle/`.
- [ ] Split settings: `base.py`, `dev.py`, `prod.py`.
- [ ] Configure GitHub Actions to run lint, type checks, and tests.

**Definition of Done**
- Running `docker compose up` brings DB + app up.
- `pytest` passes a hello-world test.
- CI is green.

---

## Phase 1 — Domain Modeling & DB Schema
**Goals**
- Define core entities and relationships.

**Tasks**
- [ ] Create `PuzzleTemplate` model (puzzle definition).
- [ ] Create `GameSession` model (per-user state).
- [ ] Create `DailyChallenge` model.
- [ ] Add indexes and constraints.
- [ ] Register models in Django Admin.

**DoD**
- Migrations apply cleanly.
- Admin shows models with filters.

---

## Phase 2 — Sudoku Engine Abstraction
**Goals**
- Separate puzzle logic from Django.

**Tasks**
- [ ] Define `Engine` base class with `generate`, `solve`, `has_unique_solution`, `rate_difficulty`.
- [ ] Implement `dokusan_engine` for 9×9.
- [ ] Stub `dlx_engine` for generic sizes.
- [ ] Add engine selector factory.

**DoD**
- Tests can generate and solve a 9×9 grid with uniqueness check.

---

## Phase 3 — Puzzle Generation Pipeline
**Goals**
- Persist reusable puzzles and seed DB.

**Tasks**
- [ ] Implement `generate_template` service.
- [ ] Add management commands: `seed_puzzles`, `clear_puzzles`.
- [ ] Validate puzzles with uniqueness check.

**DoD**
- Seeder generates N puzzles per difficulty and stores them.

---

## Phase 4 — Game Lifecycle
**Goals**
- Implement play-through CRUD.

**Tasks**
- [ ] Service to start game from template.
- [ ] Service to apply moves (number/pencil).
- [ ] Validate board state.
- [ ] Mark game as complete.

**DoD**
- Unit tests simulate a full game lifecycle.

---

## Phase 5 — Authentication
**Goals**
- Secure sessions and user identity.

**Tasks**
- [ ] Configure Django auth.
- [ ] Add signup/login/logout endpoints.
- [ ] Enforce password validators.

**DoD**
- Auth flows tested and secure endpoints require login.

---

## Phase 6 — API Layer
**Goals**
- Expose clean contract for frontend.

**Tasks**
- [ ] Implement DRF or HTMX views:
  - `/api/puzzles/` (get puzzle).
  - `/api/games/` (create game).
  - `/api/games/{id}` (fetch/save progress).
  - `/api/games/{id}/check` (validate board).
  - `/api/daily/{date}` (daily challenge).
- [ ] Generate OpenAPI schema.

**DoD**
- API endpoints return correct JSON.
- Tests cover core flows.

---

## Phase 7 — Daily Challenge
**Goals**
- Provide one puzzle per day.

**Tasks**
- [ ] Service to create daily challenges.
- [ ] Management command to seed challenges.
- [ ] Endpoint/view for daily challenge.

**DoD**
- Stable daily puzzle served for each date.

---

## Phase 8 — Hints (Optional)
**Goals**
- Add human-technique-based hints.

**Tasks**
- [ ] Extend engine to provide next logical step.
- [ ] Add `/api/games/{id}/hint`.

**DoD**
- Test puzzles return correct hints.

---

## Phase 9 — Smaller Grids
**Goals**
- Support 4×4 and 6×6 puzzles.

**Tasks**
- [ ] Generalize board indexing.
- [ ] Implement generator/solver for non-9×9.
- [ ] Update validators.

**DoD**
- Tests pass for smaller grids.

---

## Phase 10 — Undo/Redo & Integrity
**Goals**
- Track move history and errors.

**Tasks**
- [ ] Add undo/redo stack logic.
- [ ] Enforce legality checks.
- [ ] Track mistakes count.

**DoD**
- Illegal moves rejected; undo/redo works.

---

## Phase 11 — Admin Tools
**Goals**
- Enable puzzle ops for staff.

**Tasks**
- [ ] Add list filters in admin.
- [ ] Add actions: validate, export/import.
- [ ] Add dashboard for queue depth.

**DoD**
- Staff can manage puzzles without shell access.

---

## Phase 12 — Background Jobs (Optional)
**Goals**
- Automate puzzle queues and daily scheduling.

**Tasks**
- [ ] Integrate Celery + Redis.
- [ ] Periodic tasks: refill puzzle queues, pre-create daily challenges.
- [ ] Add task monitoring/logging.

**DoD**
- Queue refills and daily puzzles auto-generate.

---

## Phase 13 — Analytics
**Goals**
- Track player behavior for tuning.

**Tasks**
- [ ] Log events: game start, hint use, complete.
- [ ] Add reporting queries.
- [ ] Optional admin charts.

**DoD**
- Query average time per difficulty from DB.

---

## Phase 14 — Security & Compliance
**Goals**
- Harden app for deployment.

**Tasks**
- [ ] Enable CSRF protection.
- [ ] Secure session cookies.
- [ ] Rate-limit puzzle creation.
- [ ] Backup strategy for Postgres.

**DoD**
- Security checklist passes.

---

## Phase 15 — Minimal UI
**Goals**
- Provide basic interface to test backend.

**Tasks**
- [ ] Create game board renderer.
- [ ] Add new game form.
- [ ] Enable save/resume and daily challenge views.

**DoD**
- Full game playable via web UI.

---

## Phase 16 — Performance & Scale
**Goals**
- Ensure responsiveness under load.

**Tasks**
- [ ] Load test endpoints.
- [ ] Optimize queries and caching.
- [ ] Tune background job throughput.

**DoD**
- P95 latencies meet target thresholds.

---

# Repo Layout
/sudoku_site/ # Django project
settings/
base.py
dev.py
prod.py
/accounts/
/puzzle/
models.py
services/
engines/
base.py
dokusan_engine.py
dlx_engine.py
factory.py
generation.py
gameplay.py
/tests/
/ops/
erd.md
runbooks.md
PROJECT_PLAN.md