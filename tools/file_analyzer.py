"""Analyze an uploaded file."""
from typing import Dict
from config import Settings
from tools.chat import run_chat


def analyze_file(file_info: Dict, user_question: str, lang: str = "ar") -> str:
    """Answer a question about an uploaded file. Raises LLMError on API failure."""
    if not file_info.get("text"):
        return "⚠️ " + ("مقدرتش أقرأ نص من الملف" if lang == "ar" else "Could not extract text from file")

    text = file_info["text"]
    name = file_info.get("name", "file")

    sys_prompt = Settings.SYSTEM_PROMPTS["file_analyzer"]
    if file_info.get("truncated"):
        full_len = file_info.get("full_length", len(text))
        sys_prompt += f"\n\nملاحظة: تم اقتصار الملف على {len(text)} حرف من أصل {full_len}."
    sys_prompt += f"\n\nمحتوى ملف اسمه {name}:\n{text}"

    messages = [
        {"role": "system", "content": sys_prompt},   # ONE system message
        {"role": "user", "content": user_question},
    ]
    return run_chat(messages, lang)


def summarize_file(file_info: Dict, lang: str = "ar") -> str:
    question = "اعمل ملخص واضح ومفصل للمحتوى ده" if lang == "ar" else "Give me a clear detailed summary of this content"
    return analyze_file(file_info, question, lang)
