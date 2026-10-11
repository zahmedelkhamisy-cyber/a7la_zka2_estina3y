"""
🤖 مساعد AI الذكي - تطبيق Streamlit متعدد الوظائف
يدعم: شات، توليد صور، إنشاء ملفات، تحليل ملفات، بحث ويب، تنفيذ كود
مع موجّه تلقائي بيختار الأداة المناسبة وواجهة ثنائية اللغة (عربي/إنجليزي).

Run:  streamlit run app.py
"""
import base64
import os
import sys
import uuid
from pathlib import Path

import streamlit as st

# make imports work no matter where the app is launched from
sys.path.insert(0, str(Path(__file__).resolve().parent))

# must be the first Streamlit command
st.set_page_config(
    page_title="مساعد AI الذكي",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

from config import Settings  # noqa: E402
from utils.translations import t  # noqa: E402
from utils.history import load_history, save_history, delete_conversation, clear_all_history  # noqa: E402
from utils.file_extract import get_file_summary  # noqa: E402
from utils.ui_helpers import apply_rtl, display_tool_badge, render_api_status, display_search_results  # noqa: E402
from tools.router import detect_tool_with_llm  # noqa: E402
from tools.chat import run_chat  # noqa: E402
from tools.image_gen import generate_image  # noqa: E402
from tools.file_creator import create_file_from_prompt  # noqa: E402
from tools.file_analyzer import analyze_file  # noqa: E402
from tools.web_search import search_web, summarize_results  # noqa: E402
from tools.code_runner import run_code_tool, extract_code  # noqa: E402

DEFAULT_TITLES = ["محادثة جديدة", "New Conversation"]

# Newer Streamlit uses width="stretch"; older versions only know use_container_width.
import inspect  # noqa: E402
STRETCH = (
    {"width": "stretch"}
    if "width" in inspect.signature(st.button).parameters
    else {"use_container_width": True}
)


# ============================================================ state helpers
def _new_conv_data(lang: str) -> dict:
    return {
        "title": t("new_conversation", lang).replace("➕ ", ""),
        "messages": [{"role": "system", "content": Settings.SYSTEM_PROMPTS["chat"]}],
    }


def _create_conversation(lang: str) -> str:
    new_id = str(uuid.uuid4())
    st.session_state.history[new_id] = _new_conv_data(lang)
    st.session_state.current_id = new_id
    return new_id


def init_session_state():
    if "history" not in st.session_state:
        st.session_state.history = load_history(Settings.HISTORY_FILE)
    if "lang" not in st.session_state:
        st.session_state.lang = Settings.DEFAULT_LANGUAGE if Settings.DEFAULT_LANGUAGE in ("ar", "en") else "ar"
    if "current_id" not in st.session_state or st.session_state.current_id not in st.session_state.history:
        if st.session_state.history:
            st.session_state.current_id = list(st.session_state.history.keys())[-1]
        else:
            _create_conversation(st.session_state.lang)
    if "mode" not in st.session_state:
        st.session_state.mode = "auto"  # auto | manual
    if "override_tool" not in st.session_state:
        st.session_state.override_tool = "auto"
    if "show_settings" not in st.session_state:
        st.session_state.show_settings = False


def get_current_conversation() -> dict:
    return st.session_state.history[st.session_state.current_id]


def _persist():
    save_history(st.session_state.history, Settings.HISTORY_FILE)


# ============================================================ sidebar
def render_sidebar():
    lang = st.session_state.lang
    with st.sidebar:
        st.header(t("conversations", lang))

        if st.button(t("new_conversation", lang), **STRETCH):
            _create_conversation(lang)
            _persist()
            st.rerun()

        st.divider()

        conv_ids = list(st.session_state.history.keys())
        if conv_ids:
            for conv_id in reversed(conv_ids):
                conv = st.session_state.history[conv_id]
                title = conv.get("title", "...")
                msg_count = len([m for m in conv.get("messages", []) if m.get("role") != "system"])

                col1, col2 = st.columns([4, 1])
                with col1:
                    if st.button(
                        f"{title[:30]} ({msg_count})",
                        key=f"conv_{conv_id}",
                        **STRETCH,
                        help=title,
                        type="primary" if conv_id == st.session_state.current_id else "secondary",
                    ):
                        st.session_state.current_id = conv_id
                        st.rerun()
                with col2:
                    if st.button("🗑️", key=f"del_{conv_id}"):
                        st.session_state.history = delete_conversation(st.session_state.history, conv_id)
                        if st.session_state.current_id == conv_id:
                            remaining = list(st.session_state.history.keys())
                            if remaining:
                                st.session_state.current_id = remaining[-1]
                            else:
                                _create_conversation(lang)
                        _persist()
                        st.rerun()
        else:
            st.info(t("no_conversations", lang))

        st.divider()

        if conv_ids and st.button(t("clear_history", lang), **STRETCH):
            st.session_state.history = clear_all_history(Settings.HISTORY_FILE)
            _create_conversation(lang)
            _persist()
            st.rerun()

        st.divider()

        # file upload
        st.subheader(t("upload_file", lang))
        st.file_uploader(
            t("upload_file", lang),
            type=["pdf", "docx", "txt", "csv", "xlsx"],
            key="file_uploader",
            label_visibility="collapsed",
        )

        st.divider()

        # language
        st.subheader(t("language", lang))
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🇪🇬 عربي", **STRETCH, type="primary" if lang == "ar" else "secondary"):
                st.session_state.lang = "ar"
                st.rerun()
        with c2:
            if st.button("🇬🇧 English", **STRETCH, type="primary" if lang == "en" else "secondary"):
                st.session_state.lang = "en"
                st.rerun()

        st.divider()

        # mode
        st.subheader(t("mode", lang))
        m1, m2 = st.columns(2)
        with m1:
            if st.button(
                "🤖 " + t("auto_mode", lang).split(" (")[0],
                **STRETCH,
                type="primary" if st.session_state.mode == "auto" else "secondary",
            ):
                st.session_state.mode = "auto"
                st.session_state.override_tool = "auto"
                st.rerun()
        with m2:
            if st.button(
                "✋ " + t("manual_mode", lang).split(" (")[0],
                **STRETCH,
                type="primary" if st.session_state.mode == "manual" else "secondary",
            ):
                st.session_state.mode = "manual"
                st.rerun()

        if st.session_state.mode == "manual":
            tool_options = {
                "auto": t("auto_mode", lang),
                "chat": t("tool_chat", lang),
                "image_gen": t("tool_image", lang),
                "file_creator": t("tool_file_create", lang),
                "file_analyzer": t("tool_file_analyze", lang),
                "web_search": t("tool_web_search", lang),
                "code_runner": t("tool_code_run", lang),
            }
            keys = list(tool_options.keys())
            current_idx = keys.index(st.session_state.override_tool) if st.session_state.override_tool in keys else 0
            st.session_state.override_tool = st.selectbox(
                t("override_tool", lang),
                keys,
                index=current_idx,
                format_func=lambda x: tool_options[x],
            )

        st.divider()
        render_api_status(Settings.summary(), lang)

        if st.button(t("settings", lang), **STRETCH):
            st.session_state.show_settings = not st.session_state.show_settings
            st.rerun()

        if st.session_state.show_settings:
            render_settings_panel(lang)


def render_settings_panel(lang: str):
    providers = ["duckduckgo", "serpapi", "brave"]
    with st.expander(t("settings", lang), expanded=True):
        with st.form("settings_form"):
            new_base = st.text_input(t("llm_base_url", lang), value=Settings.LLM_API_BASE_URL)
            new_key = st.text_input(
                t("llm_key", lang), value="", type="password",
                placeholder="•••••• (leave empty to keep current)",
            )
            new_chat_model = st.text_input(t("chat_model", lang), value=Settings.LLM_CHAT_MODEL)
            new_image_model = st.text_input(t("image_model", lang), value=Settings.LLM_IMAGE_MODEL)
            idx = providers.index(Settings.WEB_SEARCH_PROVIDER) if Settings.WEB_SEARCH_PROVIDER in providers else 0
            new_web_provider = st.selectbox(t("web_provider", lang), providers, index=idx)
            submitted = st.form_submit_button(t("save_settings", lang))

        if submitted:
            Settings.LLM_API_BASE_URL = new_base.strip().rstrip("/")
            if new_key.strip():
                Settings.LLM_API_KEY = new_key.strip()
            Settings.LLM_CHAT_MODEL = new_chat_model.strip() or "auto"
            Settings.LLM_IMAGE_MODEL = new_image_model.strip() or "dall-e-3"
            Settings.WEB_SEARCH_PROVIDER = new_web_provider
            st.session_state.flash = t("settings_saved", lang)
            st.rerun()


# ============================================================ message processing
def _load_uploaded_file(current: dict, uploaded_file, lang: str) -> bool:
    """Extract an uploaded file once per conversation. Returns False on failure."""
    if uploaded_file is None:
        return True
    file_key = f"{uploaded_file.name}:{uploaded_file.size}"
    if current.get("loaded_file") == file_key:
        return True

    info = get_file_summary(uploaded_file, Settings.MAX_FILE_CHARS)
    if not info.get("text"):
        st.error(t("file_read_failed", lang) + f"\n\n{info.get('error', '')}")
        return False

    current["file_info"] = info
    current["loaded_file"] = file_key
    current["messages"].append({
        "role": "system",
        "content": f"محتوى ملف مرفق اسمه {info['name']} (نوع: {info['type']}):\n{info['text']}",
    })
    st.session_state.flash = t("file_loaded", lang, filename=info["name"])
    return True


def process_user_message(user_input: str, uploaded_file):
    """Run the right tool for the message. Returns False if nothing was processed."""
    lang = st.session_state.lang
    current = get_current_conversation()

    if not _load_uploaded_file(current, uploaded_file, lang):
        return False
    file_info = current.get("file_info")

    # --- choose tool
    manual = st.session_state.mode == "manual" and st.session_state.override_tool != "auto"
    if manual:
        tool = st.session_state.override_tool
    else:
        tool, _ = detect_tool_with_llm(user_input, has_file=file_info is not None)
        # sanity re-routes for auto mode
        if tool == "code_runner" and not extract_code(user_input):
            tool = "chat"
        if tool == "file_analyzer" and not file_info:
            tool = "chat"

    display_tool_badge(tool, lang)

    current["messages"].append({"role": "user", "content": user_input})
    if current.get("title") in DEFAULT_TITLES:
        current["title"] = user_input.strip()[:30] or current["title"]

    result = execute_tool(tool, user_input, file_info, current, lang)

    if result.get("text"):
        current["messages"].append({
            "role": "assistant",
            "content": result["text"],
            "tool": tool,
            "extra": result.get("extra"),
            "error": bool(result.get("error")),  # errors are shown but never sent back to the LLM
        })
    _persist()
    return True


def execute_tool(tool: str, user_input: str, file_info, current: dict, lang: str) -> dict:
    """Run a tool. Returns {text, extra, error?}."""
    with st.spinner(_get_spinner_message(tool, lang)):
        try:
            if tool == "image_gen":
                img_bytes = generate_image(user_input, lang)
                if img_bytes:
                    return {
                        "text": "🎨 تم توليد الصورة:" if lang == "ar" else "🎨 Image generated:",
                        "extra": {"type": "image", "data": base64.b64encode(img_bytes).decode()},
                    }
                return {"text": t("no_image_result", lang), "extra": None, "error": True}

            if tool == "file_creator":
                file_bytes, filename, file_format = create_file_from_prompt(user_input, lang)
                if file_bytes:
                    return {
                        "text": t("file_ready", lang),
                        "extra": {
                            "type": "file",
                            "data": base64.b64encode(file_bytes).decode(),
                            "filename": filename,
                            "mime": _get_mime(file_format),
                        },
                    }
                return {"text": "⚠️ فشل إنشاء الملف" if lang == "ar" else "⚠️ Failed to create file",
                        "extra": None, "error": True}

            if tool == "file_analyzer":
                if file_info:
                    return {"text": analyze_file(file_info, user_input, lang), "extra": None}
                msg = ("📂 مفيش ملف مرفوع. ارفع ملف من الشريط الجانبي الأول."
                       if lang == "ar" else "📂 No file uploaded. Upload one from the sidebar first.")
                return {"text": msg, "extra": None, "error": True}

            if tool == "web_search":
                results = search_web(user_input, max_results=5, lang=lang)
                summary = summarize_results(user_input, results, lang)  # one search only
                return {"text": summary, "extra": {"type": "search_results", "data": results}}

            if tool == "code_runner":
                return {"text": run_code_tool(user_input, lang), "extra": None}

            # chat (and fallback)
            return {"text": run_chat(current["messages"], lang), "extra": None}

        except Exception as e:
            return {"text": t("error_occurred", lang, error=str(e)), "extra": None, "error": True}


def _get_spinner_message(tool: str, lang: str) -> str:
    mapping = {
        "chat": "thinking", "image_gen": "generating_image", "file_creator": "creating_file",
        "file_analyzer": "thinking", "web_search": "searching_web", "code_runner": "running_code",
    }
    return t(mapping.get(tool, "thinking"), lang)


def _get_mime(fmt: str) -> str:
    return {
        "txt": "text/plain",
        "md": "text/markdown",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "pdf": "application/pdf",
    }.get(fmt, "application/octet-stream")


# ============================================================ rendering
def render_chat_messages():
    current = get_current_conversation()
    lang = st.session_state.lang
    for i, msg in enumerate(current["messages"]):
        if msg["role"] == "system":
            continue
        with st.chat_message(msg["role"]):
            if msg["role"] == "assistant" and msg.get("tool"):
                display_tool_badge(msg["tool"], lang)
            if msg.get("content"):
                st.markdown(msg["content"])
            if msg.get("extra"):
                _render_extra(msg["extra"], lang, key=f"{st.session_state.current_id}_{i}")


def _render_extra(extra: dict, lang: str, key: str = "x"):
    kind = extra.get("type")
    if kind == "image":
        try:
            st.image(base64.b64decode(extra["data"]), **STRETCH)
        except Exception:
            pass
    elif kind == "file":
        try:
            st.download_button(
                label=t("download_file", lang),
                data=base64.b64decode(extra["data"]),
                file_name=extra.get("filename", "file.bin"),
                mime=extra.get("mime", "application/octet-stream"),
                **STRETCH,
                key=f"dl_{key}",  # unique key: several files in one chat would otherwise collide
            )
        except Exception:
            pass
    elif kind == "search_results":
        results = extra.get("data", [])
        if results:
            with st.expander(t("search_results", lang), expanded=False):
                display_search_results(results, lang)


def render_main():
    lang = st.session_state.lang
    current = get_current_conversation()

    if "flash" in st.session_state:
        st.toast(st.session_state.pop("flash"))

    st.title(f"🤖 {current.get('title', 'AI Assistant')}")

    if not Settings.is_llm_configured():
        st.warning(t("no_api_key", lang))
        st.info(
            "📝 انسخ `.env.example` باسم `.env` جنب `app.py` واكتب فيه:\n"
            "```\nLLM_API_BASE_URL=http://localhost:3001/v1\nLLM_API_KEY=your-key\n```\n"
            "أو حطهم من ⚙️ الإعدادات في الشريط الجانبي."
            if lang == "ar" else
            "📝 Copy `.env.example` to `.env` next to `app.py` and set:\n"
            "```\nLLM_API_BASE_URL=http://localhost:3001/v1\nLLM_API_KEY=your-key\n```\n"
            "or enter them from ⚙️ Settings in the sidebar."
        )

    render_chat_messages()

    user_input = st.chat_input(t("ask_here", lang))
    if user_input:
        with st.chat_message("user"):
            st.markdown(user_input)
        with st.chat_message("assistant"):
            ok = process_user_message(user_input, st.session_state.get("file_uploader"))
        if ok:
            st.rerun()  # redraw from history (also refreshes the sidebar title)


def main():
    init_session_state()
    apply_rtl(st.session_state.lang)
    render_sidebar()
    render_main()


main()
