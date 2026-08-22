from app.locales.en import TEXTS as EN
from app.locales.ru import TEXTS as RU
from app.locales.tr import TEXTS as TR


TRANSLATIONS = {
    "ru": RU,
    "en": EN,
    "tr": TR,
}

DEFAULT_LANGUAGE = "ru"


def t(
    key: str,
    language: str | None = None,
) -> str:
    language = language or DEFAULT_LANGUAGE

    translations = TRANSLATIONS.get(
        language,
        TRANSLATIONS[DEFAULT_LANGUAGE],
    )

    return translations.get(
        key,
        TRANSLATIONS[DEFAULT_LANGUAGE].get(
            key,
            key,
        ),
    )