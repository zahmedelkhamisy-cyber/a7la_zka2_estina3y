"""Python code execution tool - simple subprocess sandbox (NOT a real security sandbox)."""
import ast
import subprocess
import sys
import os
import tempfile
import re
from typing import Tuple, Optional
from config import Settings

# Environment variables that must NEVER be visible to user code
_SECRET_HINTS = ("KEY", "TOKEN", "SECRET", "PASSWORD", "LLM_API", "WEB_SEARCH_API")


def _safe_env() -> dict:
    env = {
        k: v for k, v in os.environ.items()
        if not any(h in k.upper() for h in _SECRET_HINTS)
    }
    env["PYTHONIOENCODING"] = "utf-8"
    env["MPLBACKEND"] = "Agg"
    return env


def extract_code(user_input: str) -> Optional[str]:
    """Extract Python code from a message (fenced block, or the whole message if it parses as code)."""
    for pat in (r"```(?:python|py)\s*\n(.*?)```", r"```\s*\n(.*?)```"):
        m = re.search(pat, user_input, re.DOTALL)
        if m:
            return m.group(1).strip()

    stripped = user_input.strip()
    try:
        tree = ast.parse(stripped)
        # plain sentences like "hello world" are syntax errors; single bare names are not code
        if tree.body and not all(
            isinstance(n, ast.Expr) and isinstance(n.value, (ast.Name, ast.Constant)) for n in tree.body
        ):
            return stripped
    except SyntaxError:
        pass
    return None


def run_python_code(code: str, lang: str = "ar") -> Tuple[str, str, Optional[str]]:
    """Run code. Returns (stdout, stderr, error_msg)."""
    if not Settings.CODE_EXECUTION_ENABLED:
        return ("", "", "Code execution is disabled" if lang == "en" else "تنفيذ الكود متعطل")
    if not code or not code.strip():
        return ("", "", "Empty code" if lang == "en" else "كود فاضي")

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
        f.write(code)
        temp_path = f.name

    try:
        result = subprocess.run(
            [sys.executable, temp_path],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=Settings.CODE_EXECUTION_TIMEOUT,
            env=_safe_env(),
            cwd=tempfile.gettempdir(),
        )
        error_msg = f"Exit code: {result.returncode}" if result.returncode != 0 else None
        return (result.stdout or "", result.stderr or "", error_msg)
    except subprocess.TimeoutExpired:
        return ("", "", f"Timeout after {Settings.CODE_EXECUTION_TIMEOUT}s")
    except Exception as e:
        return ("", "", str(e))
    finally:
        try:
            os.unlink(temp_path)
        except Exception:
            pass


def format_output(stdout: str, stderr: str, error_msg: Optional[str], lang: str = "ar") -> str:
    parts = []
    if stdout:
        label = "📤 المخرجات:" if lang == "ar" else "📤 Output:"
        parts.append(f"{label}\n```\n{stdout}\n```")
    if stderr:
        label = "❌ خطأ:" if lang == "ar" else "❌ Error:"
        parts.append(f"{label}\n```\n{stderr}\n```")
    if error_msg:
        parts.append(f"⚠️ {error_msg}")
    if not parts:
        return "✅ تم التنفيذ بدون مخرجات" if lang == "ar" else "✅ Executed with no output"
    return "\n\n".join(parts)


def run_code_tool(user_input: str, lang: str = "ar") -> str:
    code = extract_code(user_input)
    if not code:
        hint = (
            "اكتب الكود بين ```python و ``` عشان أقدر أشغله"
            if lang == "ar" else
            "Wrap your code in ```python ... ``` so I can run it"
        )
        return f"⚠️ {hint}"
    stdout, stderr, error_msg = run_python_code(code, lang)
    return format_output(stdout, stderr, error_msg, lang)
