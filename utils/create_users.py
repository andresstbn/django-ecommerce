import os
from django.contrib.auth import get_user_model

UserModel = get_user_model()
DEFAULT_SUPERUSER_PASSWORD = os.environ.get("DEFAULT_SUPERUSER_PASSWORD")

try:
    emails_to_create = [
        ("tania@datak.co", "Tania", "Fonseca"),
        ("daniel@datak.co", "Daniel", "Esteban"),
        ("daniel+apiuser@datak.co", "ApiUser", "ApiUser")
    ]

    for user_data in emails_to_create:
        user = UserModel.objects.create(
            email=user_data[0],
            is_superuser=True,
        )
        if not DEFAULT_SUPERUSER_PASSWORD:
            raise ValueError(
                "Set DEFAULT_SUPERUSER_PASSWORD environment variable before running this script"
            )
        user.set_password(DEFAULT_SUPERUSER_PASSWORD)
        user.save()

except Exception as e:
    print(e)
    pass
