"""Save / load chat history on disk (JSON). An empty path means 'do not persist'."""
import json
import os
import uuid
from typing import Dict, Any


def load_history(history_file: str) -> Dict[str, Any]:
    if history_file and os.path.exists(history_file):
        try:
            with open(history_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, dict) else {}
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def save_history(history: Dict[str, Any], history_file: str) -> None:
    if not history_file:
        return
    try:
        tmp = history_file + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
        os.replace(tmp, history_file)  # atomic - no corrupted file if the app is killed mid-write
    except OSError as e:
        print(f"Could not save history: {e}")


def new_conversation(system_prompt: str) -> str:
    return str(uuid.uuid4())


def delete_conversation(history: Dict[str, Any], conv_id: str) -> Dict[str, Any]:
    history.pop(conv_id, None)
    return history


def clear_all_history(history_file: str) -> Dict[str, Any]:
    if history_file and os.path.exists(history_file):
        try:
            os.remove(history_file)
        except OSError:
            pass
    return {}
