import os

DJANGO_ENV = os.getenv("DJANGO_ENV", "dev").lower()

if DJANGO_ENV == "prod":
    from .prod import *  # type: ignore  # noqa: F401,F403
else:
    from .dev import *  # type: ignore  # noqa: F401,F403


