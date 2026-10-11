"""General chat tool."""
from typing import List, Dict
from config import Settings


class LLMError(Exception):
    """Raised when the LLM API is not configured or the request fails."""


def clean_messages(messages: List[Dict]) -> List[Dict]:
    """
    Prepare history for the API:
    - keep ONLY role/content (the app stores extra keys such as tool/extra with
      base64 images, which the API rejects or chokes on)
    - drop error messages
    - merge all system messages into ONE system message at the top
      (many OpenAI-compatible providers reject system messages in the middle)
    """
    system_parts, rest = [], []
    for m in messages:
        if m.get("error") or not m.get("content"):
            continue
        role, content = m.get("role"), m["content"]
        if role == "system":
            system_parts.append(content)
        elif role in ("user", "assistant"):
            rest.append({"role": role, "content": content})
    out = []
    if system_parts:
        out.append({"role": "system", "content": "\n\n".join(system_parts)})
    return out + rest


def run_chat(messages: List[Dict], lang: str = "ar") -> str:
    """Send the conversation to the LLM and return the reply. Raises LLMError on failure."""
    if not Settings.is_llm_configured():
        raise LLMError(
            "LLM API is not configured. Create a .env file (copy .env.example) "
            "and set LLM_API_BASE_URL and LLM_API_KEY."
        )
    try:
        client = Settings.get_openai_client()
        response = client.chat.completions.create(
            model=Settings.LLM_CHAT_MODEL,
            messages=clean_messages(messages),
            temperature=0.7,
        )
        return response.choices[0].message.content or ""
    except Exception as e:
        raise LLMError(str(e)) from e
