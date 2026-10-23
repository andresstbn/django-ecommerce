# App Engine (gunicorn main:app) and Cloud Run entrypoint.
from datakecommerce.wsgi import application

app = application
