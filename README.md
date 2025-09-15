suduko.png

# Sudoku Backend (Django)

Backend for Sudoku generation, gameplay, and daily challenges. Built with Django 5, DRF, and Postgres (SQLite fallback in dev).

### Features (scaffolded)
- Django project with split settings (`base.py`, `dev.py`, `prod.py`)
- Apps: `accounts`, `puzzle`
- REST framework wired
- Healthcheck at `/healthz`
- Dockerfile + docker-compose (Postgres + web)
- Tooling: ruff, mypy, pytest, pre-commit
- CI: GitHub Actions (lint, type-check, tests)

### Quickstart (Windows PowerShell)
1) Create and activate venv, install deps
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
```

2) Run DB migrations and server
```powershell
python manage.py migrate
python manage.py runserver
```

3) Visit
- App: `http://127.0.0.1:8000`
- Health: `http://127.0.0.1:8000/healthz`

### With Docker
```powershell
Copy-Item .env.example .env
docker compose up --build
```

### Developer tooling
- Lint: `ruff check .`  | Format: `ruff format .`
- Types: `mypy .`
- Tests: `pytest -q`
- Hooks: `pre-commit install`

### Settings
- Default module: `sudoku_site.settings` (switches via `DJANGO_ENV=dev|prod`)
- Env vars: `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`, `DATABASE_URL`

Detailed setup and usage: see `docs/bootstrap-and-usage.md`.

### ERD
See `ops/erd.md` for a text ERD of core models.
