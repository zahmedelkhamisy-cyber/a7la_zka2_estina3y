"""
Auto-router: decides which tool to use for a user message.
"""
import re
from typing import Tuple
from config import Settings


AVAILABLE_TOOLS = {
    "chat": "💬 محادثة عامة وأسئلة معرفية",
    "image_gen": "🎨 توليد صور من وصف نصي",
    "file_creator": "📄 إنشاء ملفات (Word/PDF/TXT)",
    "file_analyzer": "📂 تحليل ملف مرفوع",
    "web_search": "🔍 بحث في الويب عن معلومات حديثة",
    "code_runner": "⚡ تنفيذ كود Python",
}


def _has_word(text: str, words) -> bool:
    """Match whole English words (so 'draw' does not match 'withdraw')."""
    return any(re.search(rf"(?<![a-z0-9]){re.escape(w)}(?![a-z0-9])", text) for w in words)


def detect_tool(user_input: str, has_file: bool = False) -> Tuple[str, str]:
    """Fast keyword-based classification (used as fallback when the LLM is unavailable)."""
    text = user_input.lower().strip()

    # 1. Uploaded file + question about it
    if has_file and (
        any(k in text for k in ["حلل", "ملخص", "لخص", "الملف", "الفايل", "اقرا", "اقرأ", "وش في الملف"])
        or _has_word(text, ["summary", "summarize", "analyze", "read", "file"])
    ):
        return "file_analyzer", "file analysis with uploaded file"

    # 2. Code (check before images/files so pasted code is not misrouted)
    code_keywords = [
        "شغل كود", "شغل الكود", "شغّل كود", "شغّل الكود",
        "نفذ كود", "نفّذ كود", "نفّذ الكود", "نفذ الكود",
        "شغل python", "شغّل python", "شغل بايثون", "نفذ السكربت", "نفّذ السكربت", "شغل السكربت",
        "run code", "execute code", "run python", "execute python", "run this code",
    ]
    if any(k in text for k in code_keywords):
        return "code_runner", "code execution request"

    # 3. Image generation
    image_keywords = [
        "ارسم", "ارسمي", "ولد صورة", "ولد صوره", "ولّد صورة", "اعمل صورة", "اعمل صوره",
        "صورة ل", "صوره ل", "تصميم صورة",
        "generate image", "create image", "make image", "generate a picture",
        "image of", "picture of",
    ]
    if any(k in text for k in image_keywords) or _has_word(text, ["draw", "paint"]):
        return "image_gen", "image generation request"

    # 4. File creation
    file_keywords = [
        "اعمل ملف", "انشاء ملف", "إنشاء ملف", "اعمل مستند", "اكتب ملف",
        "اعمل تقرير", "اكتب مقال", "ملف word", "ملف pdf", "ملف ورد",
        "create file", "generate file", "make document", "word file", "pdf file", "txt file",
        "write article", "create a document", "create a pdf",
    ]
    if any(k in text for k in file_keywords):
        return "file_creator", "file creation request"

    # 5. Web search (explicit requests / fresh info only)
    web_keywords = [
        "ابحث", "دور على", "اخبار", "أخبار", "آخر اخبار", "نتيجة مباراة",
        "search for", "search the web", "google", "latest news", "news about", "who won",
    ]
    if any(k in text for k in web_keywords):
        return "web_search", "web search query"

    # 6. Pasted python code block
    if "```python" in text or "```py\n" in text:
        return "code_runner", "code block"

    return "chat", "general chat"


def detect_tool_with_llm(user_input: str, has_file: bool = False) -> Tuple[str, str]:
    """More accurate classification using the LLM; falls back to keywords on any failure."""
    if not Settings.is_llm_configured():
        return detect_tool(user_input, has_file)

    file_note = "ملاحظة: يوجد ملف مرفوع." if has_file else ""
    prompt = f"""أنت مصنف ذكي. صنف طلب المستخدم لإحدى الفئات التالية فقط:
- chat: محادثة عامة أو سؤال معرفي أو شرح (حتى لو فيه كود)
- image_gen: طلب توليد صورة أو رسم
- file_creator: إنشاء ملف نصي أو مستند (Word/PDF/TXT)
- file_analyzer: تحليل أو قراءة ملف مرفوع
- web_search: الحصول على معلومات حديثة من الإنترنت
- code_runner: طلب صريح لتشغيل/تنفيذ كود بايثون

أجب فقط باسم الفئة بدون أي شرح.

طلب المستخدم: {user_input}
{file_note}
الفئة:"""

    try:
        client = Settings.get_openai_client()
        resp = client.chat.completions.create(
            model=Settings.LLM_CHAT_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            max_tokens=20,
        )
        result = (resp.choices[0].message.content or "").strip().lower()

        # exact match first, then earliest mention
        if result in AVAILABLE_TOOLS:
            return result, f"LLM-classified as {result}"
        found = [(result.find(k), k) for k in AVAILABLE_TOOLS if k in result]
        if found:
            tool = min(found)[1]
            return tool, f"LLM-classified as {tool}"
        return detect_tool(user_input, has_file)
    except Exception:
        return detect_tool(user_input, has_file)


def get_tool_label(tool_name: str, lang: str = "ar") -> str:
    from utils.translations import t
    mapping = {
        "chat": "tool_chat",
        "image_gen": "tool_image",
        "file_creator": "tool_file_create",
        "file_analyzer": "tool_file_analyze",
        "web_search": "tool_web_search",
        "code_runner": "tool_code_run",
    }
    return t(mapping.get(tool_name, "tool_chat"), lang)
