import environ

env = environ.Env()
environ.Env.read_env()


ALLOWED_HOSTS = []
APPENGINE_URL = env("APPENGINE_URL", default=None)

if APPENGINE_URL:
    ALLOWED_HOSTS = [APPENGINE_URL]

FRONTEND_URL = env("FRONTEND_URL", default=None)

CORS_ALLOWED_ORIGINS = ["http://localhost:3000"]

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
]

if FRONTEND_URL:
    CORS_ALLOWED_ORIGINS.append(FRONTEND_URL)
