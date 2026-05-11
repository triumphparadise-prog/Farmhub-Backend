"""
WSGI config for backend project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.management import call_command
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings.prod')

application = get_wsgi_application()


def run_startup_migrations():
    if os.environ.get("ENV") != "production":
        return

    enabled = os.environ.get("RUN_MIGRATIONS_ON_STARTUP", "true").lower()
    if enabled not in {"1", "true", "yes"}:
        return

    call_command("migrate", interactive=False, verbosity=1)


run_startup_migrations()
