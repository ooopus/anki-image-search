# translator.py - Translation Support

import gettext
import os
from pathlib import Path

from .config.languages import LanguageCode

# Global translator instance
_translator = None


def get_translator():
    """Get or create translator instance"""
    global _translator
    if _translator is None:
        _translator = setup_translator()
    return _translator


def setup_translator():
    """Setup gettext translator based on config"""
    from .config.config import load_config

    config = load_config()
    lang_code = config.language

    # Auto-detect language if set to AUTO
    if lang_code == LanguageCode.AUTO:
        from aqt import mw

        if mw and hasattr(mw.pm, "meta") and "defaultLang" in mw.pm.meta:
            anki_lang = mw.pm.meta["defaultLang"]
            # Map Anki language codes to our language codes
            lang_map = {
                "zh_CN": LanguageCode.ZH_CN,
                "zh_TW": LanguageCode.ZH_CN,
                "en_US": LanguageCode.EN_US,
            }
            lang_code = lang_map.get(anki_lang, LanguageCode.EN_US)
        else:
            lang_code = LanguageCode.EN_US

    # Setup gettext
    locale_dir = Path(__file__).parent / "locales"
    try:
        translation = gettext.translation(
            "messages", localedir=str(locale_dir), languages=[lang_code.value]
        )
        return translation.gettext
    except FileNotFoundError:
        # Fallback to NullTranslations (returns original strings)
        return gettext.NullTranslations().gettext


def _(message: str) -> str:
    """Translate message"""
    translator = get_translator()
    return translator(message)


def reload_translator():
    """Reload translator (called when language setting changes)"""
    global _translator
    _translator = None
