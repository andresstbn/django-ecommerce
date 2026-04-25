import environ
from google.oauth2 import service_account

env = environ.Env()
environ.Env.read_env()

GS_PROJECT_ID = env("GS_PROJECT_ID")
GS_BUCKET_NAME = env("GS_BUCKET_NAME")
GS_DEFAULT_ACL = 'publicRead'

# https://django-storages.readthedocs.io/en/latest/backends/gcloud.html

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.gcloud.GoogleCloudStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}
