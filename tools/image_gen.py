"""Image generation tool (OpenAI-compatible /images/generations)."""
from typing import Optional
import base64
from config import Settings
from tools.chat import LLMError


def _download(url: str) -> bytes:
    import requests
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    return r.content


def _extract(response) -> Optional[bytes]:
    if not response or not getattr(response, "data", None):
        return None
    item = response.data[0]
    b64 = getattr(item, "b64_json", None)
    if b64:
        return base64.b64decode(b64)
    url = getattr(item, "url", None)
    if url:
        return _download(url)
    return None


def generate_image(prompt: str, lang: str = "ar", size: str = "1024x1024") -> Optional[bytes]:
    """
    Generate an image and return its bytes.
    Raises LLMError with the real reason if the API refuses (so the user can see why).
    """
    if not Settings.is_llm_configured():
        raise LLMError("LLM API is not configured (.env missing?)")

    client = Settings.get_openai_client()
    first_error = None

    # Attempt 1: ask for base64 directly
    try:
        img = _extract(client.images.generate(
            model=Settings.LLM_IMAGE_MODEL, prompt=prompt, n=1, size=size,
            response_format="b64_json",
        ))
        if img:
            return img
    except Exception as e:
        first_error = e

    # Attempt 2: provider may not support response_format -> default (URL)
    try:
        img = _extract(client.images.generate(
            model=Settings.LLM_IMAGE_MODEL, prompt=prompt, n=1, size=size,
        ))
        if img:
            return img
    except Exception as e:
        raise LLMError(f"Image generation failed: {e}") from e

    if first_error:
        raise LLMError(f"Image generation failed: {first_error}")
    return None


def get_supported_sizes() -> list:
    return ["256x256", "512x512", "1024x1024", "1024x1792", "1792x1024"]
