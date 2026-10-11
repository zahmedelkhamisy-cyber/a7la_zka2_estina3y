"""ترجمات الواجهة ثنائية اللغة (عربي/إنجليزي)."""

TRANSLATIONS = {
    "ar": {
        # العناوين
        "app_title": "🤖 مساعد AI الذكي",
        "conversations": "المحادثات",
        "new_conversation": "➕ محادثة جديدة",
        "settings": "⚙️ الإعدادات",
        "api_status": "حالة الـ API",

        # اللغة
        "language": "اللغة",
        "arabic": "العربية",
        "english": "English",

        # الوضع
        "mode": "الوضع",
        "auto_mode": "تلقائي (AI بيختار الأداة)",
        "manual_mode": "يدوي (اختيار يدوي)",

        # الأدوات
        "tool_chat": "💬 محادثة",
        "tool_image": "🎨 توليد صورة",
        "tool_file_create": "📄 إنشاء ملف",
        "tool_file_analyze": "📂 تحليل ملف",
        "tool_web_search": "🔍 بحث ويب",
        "tool_code_run": "⚡ تنفيذ كود",

        # رسائل
        "thinking": "بيفكر...",
        "generating_image": "بيولّد الصورة...",
        "searching_web": "بيبحث في الويب...",
        "running_code": "بيشغّل الكود...",
        "creating_file": "بيعمل الملف...",
        "file_loaded": "تم تحميل {filename} ✅ اسأل عنه دلوقتي",
        "file_uploaded": "📁 الملف المرفوع",
        "no_file": "مفيش ملف مرفوع",
        "ask_here": "اكتب سؤالك هنا...",
        "no_conversations": "مفيش محادثات بعد",
        "error_occurred": "⚠️ حصل خطأ: {error}",
        "no_api_key": "⚠️ LLM_API_KEY مش مظبوط. عدّل ملف .env",
        "no_image_result": "⚠️ مفيش صورة اتولدت",
        "file_ready": "✅ الملف جاهز للتنزيل:",
        "code_output": "📤 المخرجات:",
        "code_error": "❌ خطأ في الكود:",
        "search_results": "🔍 نتائج البحث:",
        "no_search_results": "مفيش نتائج بحث",
        "file_read_failed": "⚠️ مقدرتش أقرأ نص الملف ده (ممكن يكون صور / PDF ممسوح)",
        "auto_routed_to": "🤖 الـ AI اختار: {tool}",

        # أزرار
        "download_file": "⬇️ تنزيل الملف",
        "clear_history": "🗑️ مسح كل المحادثات",
        "delete_conv": "🗑️ حذف",
        "override_tool": "أجبر استخدام أداة معينة:",

        # رفع الملفات
        "upload_file": "ارفع ملف (PDF, Word, TXT, Excel)",
        "upload_hint": "الملف هيتحلل ويتبعت للـ AI",

        # الإعدادات
        "llm_base_url": "رابط الـ API",
        "llm_key": "مفتاح الـ LLM",
        "chat_model": "موديل الشات",
        "image_model": "موديل الصور",
        "web_provider": "مزود بحث الويب",
        "save_settings": "💾 حفظ الإعدادات",
        "settings_saved": "تم حفظ الإعدادات ✅",

        # أرقام
        "messages_count": "{n} رسالة",
        "today": "اليوم",
    },
    "en": {
        # Titles
        "app_title": "🤖 Smart AI Assistant",
        "conversations": "Conversations",
        "new_conversation": "➕ New Conversation",
        "settings": "⚙️ Settings",
        "api_status": "API Status",

        # Language
        "language": "Language",
        "arabic": "العربية",
        "english": "English",

        # Mode
        "mode": "Mode",
        "auto_mode": "Auto (AI picks the tool)",
        "manual_mode": "Manual (pick tool yourself)",

        # Tools
        "tool_chat": "💬 Chat",
        "tool_image": "🎨 Image Generation",
        "tool_file_create": "📄 Create File",
        "tool_file_analyze": "📂 Analyze File",
        "tool_web_search": "🔍 Web Search",
        "tool_code_run": "⚡ Run Code",

        # Messages
        "thinking": "Thinking...",
        "generating_image": "Generating image...",
        "searching_web": "Searching the web...",
        "running_code": "Running code...",
        "creating_file": "Creating file...",
        "file_loaded": "Loaded {filename} ✅ Ask about it now",
        "file_uploaded": "📁 Uploaded File",
        "no_file": "No file uploaded",
        "ask_here": "Type your question here...",
        "no_conversations": "No conversations yet",
        "error_occurred": "⚠️ Error occurred: {error}",
        "no_api_key": "⚠️ LLM_API_KEY is not set. Edit .env file",
        "no_image_result": "⚠️ No image was generated",
        "file_ready": "✅ File ready for download:",
        "code_output": "📤 Output:",
        "code_error": "❌ Code error:",
        "search_results": "🔍 Search results:",
        "no_search_results": "No search results",
        "file_read_failed": "⚠️ Could not read text from this file (maybe scanned/images only)",
        "auto_routed_to": "🤖 AI chose: {tool}",

        # Buttons
        "download_file": "⬇️ Download File",
        "clear_history": "🗑️ Clear All",
        "delete_conv": "🗑️ Delete",
        "override_tool": "Force a specific tool:",

        # Upload
        "upload_file": "Upload file (PDF, Word, TXT, Excel)",
        "upload_hint": "File will be analyzed by AI",

        # Settings
        "llm_base_url": "API URL",
        "llm_key": "LLM Key",
        "chat_model": "Chat Model",
        "image_model": "Image Model",
        "web_provider": "Web Search Provider",
        "save_settings": "💾 Save Settings",
        "settings_saved": "Settings saved ✅",

        # Counts
        "messages_count": "{n} messages",
        "today": "Today",
    },
}


def t(key: str, lang: str = "ar", **kwargs) -> str:
    """يرجع نص مترجم للغة المطلوبة مع دعم المتغيرات."""
    text = TRANSLATIONS.get(lang, {}).get(key, key)
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, IndexError):
            pass
    return text
