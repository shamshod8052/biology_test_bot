import os
import django

# Ensure that Django settings are loaded
os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'main.settings')
os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")
django.setup()

from django.conf import settings
from django.utils.translation import override, gettext as _


def get_translations(base_text: str) -> set[str]:
    translations = set()

    # Iterate through the available language codes
    for lang_code, __ in settings.LANGUAGES:
        with override(lang_code):  # Temporarily set the language
            translations.add(_(base_text))  # Get translation for the text and add to set

    return translations


if __name__ == '__main__':
    print(get_translations('Hello'))  # Test the function with 'Hello'
