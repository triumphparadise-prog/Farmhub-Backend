from .base import *

DEBUG = False
LOG_FORMAT = "json"

# Allowed hosts MUST come from .env
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')
render_hostname = env("RENDER_EXTERNAL_HOSTNAME", default="")
if render_hostname and render_hostname not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(render_hostname)

# SECURITY SETTINGS
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = env("SESSION_COOKIE_SAMESITE", default="Lax")
CSRF_COOKIE_SAMESITE = env("CSRF_COOKIE_SAMESITE", default="Lax")

SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_PRELOAD = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

X_FRAME_OPTIONS = 'DENY'

CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=[])

CORS_ALLOW_CREDENTIALS = True  # allow cookies to be sent cross-domain

# Ensure JWT cookie is secure in production
SIMPLE_JWT['AUTH_COOKIE_SECURE'] = env.bool("AUTH_COOKIE_SECURE", default=True)
SIMPLE_JWT['AUTH_COOKIE_SAMESITE'] = env("AUTH_COOKIE_SAMESITE", default="Lax")

if SIMPLE_JWT["AUTH_COOKIE_SAMESITE"] == "None" and not SIMPLE_JWT["AUTH_COOKIE_SECURE"]:
    raise RuntimeError("AUTH_COOKIE_SECURE must be True when AUTH_COOKIE_SAMESITE=None")

EMAIL_BACKEND = "sendgrid_backend.SendgridBackend"
SENDGRID_API_KEY = env("SENDGRID_API_KEY")
SENDGRID_SANDBOX_MODE_IN_DEBUG = False
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="noreply@dchops.com")
