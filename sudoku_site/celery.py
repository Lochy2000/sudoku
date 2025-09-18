from __future__ import annotations

import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sudoku_site.settings")

app = Celery("sudoku")

# Load config from Django settings with CELERY_ prefix
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks.py in installed apps
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self: Celery) -> str:  # pragma: no cover - utility
    """Return a string representation of the current task request."""
    return f"Request: {self.request!r}"
