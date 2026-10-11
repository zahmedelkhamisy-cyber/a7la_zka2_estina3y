"""
App settings. Reads values from a .env file, environment variables,
or Streamlit secrets (for Streamlit Community Cloud).
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

try:
    from dotenv import load_dotenv
    for _p in (BASE_DIR / ".env", Path.cwd() / ".env"):
        if _p.exists():
            load_dotenv(_p, encoding="utf-8")
            break
except ImportError:
    pass  # python-dotenv not installed - rely on real environment variables


def _get(key: str, default: str = "") -> str:
    """Read from env vars first, then Streamlit secrets, then default."""
    val = os.getenv(key)
    if val is not None and val != "":
        return val
    try:
        import streamlit as st
        if key in st.secrets:
            return str(st.secrets[key])
    except Exception:
        pass
    return default


def _get_int(key: str, default: int) -> int:
    try:
        return int(_get(key, str(default)))
    except (TypeError, ValueError):
        return default


def _resolve_history_path(value: str) -> str:
    """History file is stored next to app.py (not in the current working dir)."""
    if not value:
        return ""  # empty = do not persist history on disk
    p = Path(value)
    return str(p if p.is_absolute() else BASE_DIR / p)


class Settings:
    """All app settings in one place."""

    # ====== Main LLM (chat + images) ======
    LLM_API_BASE_URL: str = _get("LLM_API_BASE_URL", "http://localhost:3001/v1").rstrip("/")
    LLM_API_KEY: str = _get("LLM_API_KEY", "")
    LLM_CHAT_MODEL: str = _get("LLM_CHAT_MODEL", "auto")
    LLM_IMAGE_MODEL: str = _get("LLM_IMAGE_MODEL", "dall-e-3")
    LLM_AUDIO_MODEL: str = _get("LLM_AUDIO_MODEL", "tts-1")

    # ====== Web search ======
    WEB_SEARCH_PROVIDER: str = _get("WEB_SEARCH_PROVIDER", "duckduckgo").lower()  # duckduckgo | serpapi | brave
    WEB_SEARCH_API_KEY: str = _get("WEB_SEARCH_API_KEY", "")

    # ====== Code execution ======
    CODE_EXECUTION_ENABLED: bool = _get("CODE_EXECUTION_ENABLED", "true").lower() == "true"
    CODE_EXECUTION_TIMEOUT: int = _get_int("CODE_EXECUTION_TIMEOUT", 10)

    # ====== General ======
    # os.environ.get so that an explicitly EMPTY value disables persistence
    HISTORY_FILE: str = _resolve_history_path(
        os.environ["HISTORY_FILE"] if "HISTORY_FILE" in os.environ else _get("HISTORY_FILE", "chat_history.json")
    )
    MAX_FILE_CHARS: int = _get_int("MAX_FILE_CHARS", 8000)
    DEFAULT_LANGUAGE: str = _get("DEFAULT_LANGUAGE", "ar")  # ar | en

    # ====== System prompts ======
    SYSTEM_PROMPTS = {
        "chat": (
            "انت مساعد ذكي بترد بالعربي بشكل واضح ومباشر. "
            "إذا سُئلت بالإنجليزية، رد بالإنجليزية."
        ),
        "file_creator": (
            "انت مساعد متخصص في إنشاء محتوى ملفات. "
            "لما يطلب منك المستخدم إنشاء ملف، رد بالمحتوى الكامل الجاهز للنسخ "
            "من غير مقدمات أو تعليقات. حدد نوع الملف في أول سطر بصيغة "
            "[FILE_TYPE: txt|docx|pdf|md] ثم ضع المحتوى بعدها. "
            "استخدم # و ## للعناوين و - للنقاط."
        ),
        "file_analyzer": (
            "انت مساعد متخصص في تحليل الملفات. بناءً على المحتوى المرفق، "
            "اعمل ملخص واضح واستخرج النقاط الأساسية والكلمات المفتاحية."
        ),
    }

    @classmethod
    def is_llm_configured(cls) -> bool:
        return bool(cls.LLM_API_KEY and cls.LLM_API_BASE_URL)

    @classmethod
    def get_openai_client(cls):
        from openai import OpenAI
        return OpenAI(
            base_url=cls.LLM_API_BASE_URL,
            api_key=cls.LLM_API_KEY,
            timeout=90.0,
            max_retries=1,
        )

    @classmethod
    def summary(cls) -> dict:
        return {
            "llm_configured": cls.is_llm_configured(),
            "llm_base_url": cls.LLM_API_BASE_URL,
            "chat_model": cls.LLM_CHAT_MODEL,
            "image_model": cls.LLM_IMAGE_MODEL,
            "web_search_provider": cls.WEB_SEARCH_PROVIDER,
            "web_search_configured": bool(cls.WEB_SEARCH_API_KEY) or cls.WEB_SEARCH_PROVIDER == "duckduckgo",
            "code_execution": cls.CODE_EXECUTION_ENABLED,
            "language": cls.DEFAULT_LANGUAGE,
        }
