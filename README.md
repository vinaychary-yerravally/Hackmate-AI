# HackMatch AI

Flask web app that acts as an AI mentor for **Smart India Hackathon (SIH)** teams.
Enter a project idea and it returns recommended SIH problem statements, fit
analysis, MVP features, and a suggested tech stack (via Google Gemini).

## Setup

```bash
python3 -m venv .venv-linux
.venv-linux/bin/pip install -r requirements.txt
```

Create a `.env` file in the project root:

```
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-2.5-flash
GEMINI_MODEL_FALLBACKS=gemini-flash-latest,gemini-2.5-flash-lite,gemini-3.1-flash-lite
```

`GEMINI_MODEL` is the primary model; the fallbacks are tried in order when a
model is overloaded (HTTP 503) or unavailable.

## Run

```bash
.venv-linux/bin/python app.py     # http://127.0.0.1:5000
```

Override host/port/debug with `HOST`, `PORT`, and `FLASK_DEBUG` env vars.

## Test

```bash
.venv-linux/bin/python test_gemini.py          # live API connectivity check
.venv-linux/bin/python -m unittest test_app -v # unit tests (no network)
```

## Data pipeline scripts (offline, optional)

| Script | Does | Output |
|---|---|---|
| `fetch_historical_sih.py` | Pulls 2023/2024 problem statements from a community archive | `sih_multiyear_dataset.csv` |
| `extract_text.py` | Parses `../sih-2k25batch1.pdf` with pdfplumber | `sih_batch1_clean.csv` |
| `extract_data.py` | Cleans `sih_batch1_raw.csv` | `sih_batch1_clean.csv` |

> Note: `sih_problem_statements.csv` (101 real 2025 statements) is **not** read by
> the running app — the matcher generates suggestions with the LLM. Wire it in if
> you want grounded, verifiable PS IDs instead of generated ones.
