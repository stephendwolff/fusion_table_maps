import os

from django.conf import settings

API_KEY_FILE_PATH = os.path.join(settings.BASE_DIR, 'google_api_key.txt')


def get_google_api_key():
    with open(API_KEY_FILE_PATH, 'r') as api_key_file:
        api_key = api_key_file.read()

    return api_key
