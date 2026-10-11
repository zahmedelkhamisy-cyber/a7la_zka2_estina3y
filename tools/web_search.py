"""Web search tool - DuckDuckGo (free), SerpAPI or Brave."""
import html as _html
import re
import urllib.parse
from typing import List, Dict
from config import Settings
from tools.chat import run_chat


def search_web(query: str, max_results: int = 5, lang: str = "ar") -> List[Dict]:
    """Returns a list of {title, url, snippet}."""
    provider = Settings.WEB_SEARCH_PROVIDER.lower()
    if provider == "serpapi" and Settings.WEB_SEARCH_API_KEY:
        return _search_serpapi(query, max_results)
    if provider == "brave" and Settings.WEB_SEARCH_API_KEY:
        return _search_brave(query, max_results)
    return _search_duckduckgo(query, max_results)


def _search_duckduckgo(query: str, max_results: int) -> List[Dict]:
    # 1) 'ddgs' (new name of the package), 2) legacy 'duckduckgo_search', 3) plain HTML
    DDGS = None
    try:
        from ddgs import DDGS  # type: ignore
    except ImportError:
        try:
            from duckduckgo_search import DDGS  # type: ignore
        except ImportError:
            DDGS = None

    if DDGS is not None:
        try:
            results = []
            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=max_results):
                    results.append({
                        "title": r.get("title", ""),
                        "url": r.get("href", r.get("url", "")),
                        "snippet": r.get("body", r.get("snippet", "")),
                    })
            if results:
                return results
        except Exception as e:
            print(f"DDGS error: {e}")

    return _search_duckduckgo_html(query, max_results)


def _search_duckduckgo_html(query: str, max_results: int) -> List[Dict]:
    try:
        import requests
        resp = requests.post(
            "https://html.duckduckgo.com/html/",
            data={"q": query},
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"},
            timeout=15,
        )
        page = resp.text
        results = []
        for m in re.finditer(r'<a[^>]*class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', page, re.DOTALL):
            href, title_html = m.groups()
            snippet = ""
            sm = re.search(r'class="result__snippet"[^>]*>(.*?)</a>', page[m.end():m.end() + 3000], re.DOTALL)
            if sm:
                snippet = _html.unescape(re.sub(r"<[^>]+>", "", sm.group(1))).strip()
            results.append({
                "title": _html.unescape(re.sub(r"<[^>]+>", "", title_html)).strip(),
                "url": _decode_ddg_url(_html.unescape(href)),
                "snippet": snippet,
            })
            if len(results) >= max_results:
                break
        return results
    except Exception as e:
        print(f"DuckDuckGo HTML search error: {e}")
        return []


def _decode_ddg_url(url: str) -> str:
    if url.startswith("//"):
        url = "https:" + url
    if "uddg=" in url:
        try:
            parsed = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
            return parsed.get("uddg", [url])[0]
        except Exception:
            pass
    return url


def _search_serpapi(query: str, max_results: int) -> List[Dict]:
    try:
        import requests
        resp = requests.get(
            "https://serpapi.com/search",
            params={"q": query, "num": max_results, "api_key": Settings.WEB_SEARCH_API_KEY, "engine": "google"},
            timeout=15,
        )
        if resp.status_code != 200:
            return []
        return [
            {"title": r.get("title", ""), "url": r.get("link", ""), "snippet": r.get("snippet", "")}
            for r in resp.json().get("organic_results", [])[:max_results]
        ]
    except Exception as e:
        print(f"SerpAPI search error: {e}")
        return []


def _search_brave(query: str, max_results: int) -> List[Dict]:
    try:
        import requests
        resp = requests.get(
            "https://api.search.brave.com/res/v1/web/search",
            headers={"Accept": "application/json", "X-Subscription-Token": Settings.WEB_SEARCH_API_KEY},
            params={"q": query, "count": max_results},
            timeout=15,
        )
        if resp.status_code != 200:
            return []
        return [
            {"title": r.get("title", ""), "url": r.get("url", ""), "snippet": r.get("description", "")}
            for r in resp.json().get("web", {}).get("results", [])[:max_results]
        ]
    except Exception as e:
        print(f"Brave search error: {e}")
        return []


def summarize_results(query: str, results: List[Dict], lang: str = "ar") -> str:
    """Summarize ALREADY-fetched results (so we don't search twice)."""
    if not results:
        return "مفيش نتائج اتلقت" if lang == "ar" else "No results found"

    sources = "\n\n**المصادر:**\n" if lang == "ar" else "\n\n**Sources:**\n"
    sources += "".join(
        f"- [{r['title'].replace('[', '(').replace(']', ')')}]({r['url']})\n" for r in results
    )

    if not Settings.is_llm_configured():
        return sources.strip()

    results_text = ""
    for i, r in enumerate(results, 1):
        results_text += f"{i}. {r['title']}\nURL: {r['url']}\nSnippet: {r.get('snippet', '')}\n\n"

    sys_prompt = (
        "انت مساعد ذكي. اقرأ نتائج البحث التالية واعمل ملخص واضح بالعربي "
        "للمعلومات المطلوبة. اذكر المصادر."
        if lang == "ar" else
        "You are a smart assistant. Summarize the search results clearly. Cite sources."
    )
    messages = [
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": f"السؤال: {query}\n\nنتائج البحث:\n{results_text}"},
    ]
    try:
        return run_chat(messages, lang) + sources
    except Exception as e:
        return f"⚠️ Error summarizing: {e}{sources}"


def search_and_summarize(query: str, lang: str = "ar") -> str:
    return summarize_results(query, search_web(query, max_results=5, lang=lang), lang)
