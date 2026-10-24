import environ

env = environ.Env()
environ.Env.read_env()


APPENGINE_URL = env("APPENGINE_URL", default=None)
# Comma separated; lets the same build serve App Engine and Cloud Run hosts.
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[APPENGINE_URL] if APPENGINE_URL else [])

FRONTEND_URL = env("FRONTEND_URL", default=None)

CORS_ALLOWED_ORIGINS = ["http://localhost:3000"]

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
]

if FRONTEND_URL:
    CORS_ALLOWED_ORIGINS.append(FRONTEND_URL)
