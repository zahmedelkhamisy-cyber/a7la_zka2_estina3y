"""UI helpers - RTL support and display widgets."""
import html as _html
import streamlit as st
from utils.translations import t

_TOOL_STYLE = {
    "chat": ("#3b82f6", "💬", "tool_chat"),
    "image_gen": ("#ec4899", "🎨", "tool_image"),
    "file_creator": ("#10b981", "📄", "tool_file_create"),
    "file_analyzer": ("#f59e0b", "📂", "tool_file_analyze"),
    "web_search": ("#8b5cf6", "🔍", "tool_web_search"),
    "code_runner": ("#ef4444", "⚡", "tool_code_run"),
}


def apply_rtl(lang: str):
    """RTL for Arabic, LTR for English. Code stays LTR."""
    direction = "rtl" if lang == "ar" else "ltr"
    align = "right" if lang == "ar" else "left"
    st.markdown(
        f"""
        <style>
        .stApp, .stMarkdown, [data-testid="stChatMessage"], [data-testid="stSidebar"] {{
            direction: {direction};
            text-align: {align};
        }}
        .stChatInput textarea {{ direction: {direction}; }}
        pre, code, pre * {{ direction: ltr !important; text-align: left !important; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def display_tool_badge(tool_name: str, lang: str = "ar"):
    color, emoji, key = _TOOL_STYLE.get(tool_name, ("#6b7280", "🔧", "tool_chat"))
    label = t(key, lang)
    st.markdown(
        f"""
        <div style="display:inline-block;background:{color}22;color:{color};
             border:1px solid {color};border-radius:12px;padding:4px 12px;
             font-size:12px;font-weight:600;margin-bottom:8px;">
            {emoji} {_html.escape(label)}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_api_status(settings_dict: dict, lang: str = "ar"):
    st.markdown("---")
    st.subheader(t("api_status", lang))

    def badge(ok: bool, label: str) -> str:
        icon = "✅" if ok else "❌"
        color = "#10b981" if ok else "#ef4444"
        return f"<div style='color:{color}'>{icon} {_html.escape(label)}</div>"

    out = badge(settings_dict.get("llm_configured", False), "LLM API")
    out += badge(
        settings_dict.get("web_search_configured", False),
        f"Web Search ({settings_dict.get('web_search_provider', 'duckduckgo')})",
    )
    out += badge(settings_dict.get("code_execution", False), "Code Runner")
    st.markdown(out, unsafe_allow_html=True)


def display_search_results(results: list, lang: str = "ar"):
    if not results:
        st.info(t("no_search_results", lang))
        return
    for i, r in enumerate(results, 1):
        title = _html.escape(r.get("title", "") or r.get("url", ""))
        url = _html.escape(r.get("url", r.get("link", "")), quote=True)
        snippet = _html.escape((r.get("snippet", r.get("content", "")) or "")[:200])
        st.markdown(
            f"""
            <div style="border:1px solid #e5e7eb;border-radius:8px;padding:12px;
                        margin-bottom:8px;background:#f9fafb;">
                <div style="font-weight:600;">
                    {i}. <a href="{url}" target="_blank" rel="noopener noreferrer"
                            style="color:#1d4ed8;text-decoration:none;">{title}</a>
                </div>
                <div style="color:#6b7280;font-size:12px;margin-top:4px;">{snippet}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
