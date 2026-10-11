# AI Assistant (Streamlit)

Chat, image generation, file creation (txt/md/docx/pdf, Arabic supported), file analysis,
web search and Python execution, with an automatic tool router. UI: Arabic / English.

## Run locally
```bash
python -m venv .venv
.venv\Scripts\activate          # Windows   (Linux/macOS: source .venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env          # Linux/macOS: cp .env.example .env
# edit .env -> set LLM_API_BASE_URL and LLM_API_KEY
streamlit run app.py
```
Your LLM server (e.g. freellmapi on `http://localhost:3001/v1`) must be running first.

## Run on GitHub
* **Codespaces**: repo -> Code -> Codespaces -> Create, then the same commands as above
  (`cp .env.example .env`, edit it, `streamlit run app.py`) and open port 8501.
  `localhost:3001` only works if the LLM server runs inside the same Codespace.
* **Streamlit Community Cloud**: share.streamlit.io -> New app -> pick the repo, main file `app.py`,
  then put the values from `.streamlit/secrets.toml.example` in *Settings -> Secrets*.
  The LLM URL must be PUBLIC (not localhost).

## Public deployment checklist
* Never commit `.env` (it is in `.gitignore`). Rotate any key that was ever committed.
* Set `CODE_EXECUTION_ENABLED=false` - otherwise anyone with the link can run code on your server.
* Set `HISTORY_FILE=""` so visitors do not share/see one common chat history file.
* The Settings panel changes values for the whole running app, so avoid exposing it publicly.

## Optional: Arabic PDF font
PDF export looks for Arial/Tahoma (Windows), DejaVu/Noto/Amiri (Linux) automatically.
You can also drop any Arabic `.ttf` into a `fonts/` folder next to `app.py`.
