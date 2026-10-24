import environ
from google.oauth2 import service_account

env = environ.Env()
environ.Env.read_env()

GS_PROJECT_ID = env("GS_PROJECT_ID")
GS_BUCKET_NAME = env("GS_BUCKET_NAME")
GS_DEFAULT_ACL = 'publicRead'
# Product images have unique (uuid-derived) names; commerce logo/favicon re-uploads may take up to a week to refresh.
GS_OBJECT_PARAMETERS = {'cache_control': 'public, max-age=604800'}

# https://django-storages.readthedocs.io/en/latest/backends/gcloud.html

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.gcloud.GoogleCloudStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}
