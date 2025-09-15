from .base import *  # noqa
from .base import BASE_DIR

import os

DEBUG = True

if os.getenv("DATABASE_URL"):
    import dj_database_url  # import only if needed to avoid optional dep issues

    DATABASES: dict = {
        "default": dj_database_url.config(
            env="DATABASE_URL",
            conn_max_age=0,
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": str(BASE_DIR / "db.sqlite3"),
        }
    }

CSRF_TRUSTED_ORIGINS = ["http://localhost:8000", "http://127.0.0.1:8000"]
