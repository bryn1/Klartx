# KlartX — Plan

## GOAL
KlartX är ett throwaway-projekt (släng-app) som tar myndighetsdokument (PDF/bild) och ger: plain-language-sammanfattning, auto-fyllt formulär, och inskickning via BankID-e-legitimation.

## ACCEPTANCE
1. FastAPI-backend på localhost:8150
2. PDF/Image upload → OCR → LLM-analys → plain-language-sammanfattning
3. Auto-fill formulär med användarens data
4. Frontend med kamera-uppladdning och formulärförhandsgranskning
5. Local LLM via llama.cpp (ingen cloud)
6. BankID-simulering (mock för throwaway)
7. pytest-tester som passerar

## MODULAR PLAN (en modul per fil)

| # | Modul | Concern | Path | Contract ID |
|---|-------|---------|------|-------------|
| T1 | `src/main.py` | FastAPI app, routers, static files, lifespan | `src/main.py` | `@app/router/lifespan` |
| T2 | `src/database.py` | SQLite connection, session management | `src/database.py` | `@db/session/engine` |
| T3 | `src/models.py` | Pydantic schemas (requests/responses) | `src/models.py` | `@schemas/document/field/form` |
| T4 | `src/ocr.py` | Document upload, OCR (Tesseract/local) | `src/ocr.py` | `@ocr/process/upload` |
| T5 | `src/parser.py` | LLM-integration, document understanding, field extraction | `src/parser.py` | `@parser/analyze/summarize` |
| T6 | `src/form.py` | Auto-fill logic, form generation, BankID mock | `src/form.py` | `@form/fill/submit` |
| T7 | `src/tracking.py` | Case tracking, status updates | `src/tracking.py` | `@tracking/status` |
| T8 | `templates/` | HTML templates (Jinja2), camera UI, form preview | `templates/index.html`, `templates/form.html` | `@ui/upload/form/preview` |
| T9 | `static/` | CSS/JS (camera scanner, form interaction) | `static/app.js`, `static/app.css` | `@ui/interactions` |
| T10 | `tests/` | Unit + E2E tests | `tests/test_*.py` | `@tests/all` |

## INTERFACES

### T1 → T2, T3, T4, T5, T6, T7
- FastAPI app injicerar `db.Session` och `llama_engine` via lifespan
- Routers: `/upload`, `/analyze`, `/fill`, `/submit`, `/track`, `/status`

### T2 → T3
- Database models exporterar `Base`, `SessionLocal`, `get_session()`

### T4 → T5
- OCR-export: `process_document(image_bytes) -> str` (ren text)
- Parser-importerar: `analyze_document(text: str) -> dict`, `summarize(text: str) -> str`

### T5 → T6
- Parser-export: `extract_fields(text: str) -> dict[str, Any]` (fältvärden)
- Form-importerar: `fill_form(data: dict) -> dict`

### T6 → T7
- Form-export: `submit_form(form_data: dict, bankid_token: str) -> dict`
- Tracking-importerar: `track_submission(submission: dict) -> str` (case_id)

### T8, T9 → T1
- Templates/Static serving via FastAPI `StaticFiles` och `Jinja2Templates`

## DECISIONS

### A. OCR — Tesseract vs Cloud
- **A:** Tesseract (local, kräver installation) — bäst för throwaway, ingen API-key
- **B:** Cloud (Google Vision, AWS Textract) — kräver API-keys, inte throwaway-vänligt
- **Rekommendation:** A — Tesseract för throwaway-appen

### B. LLM — llama.cpp vs Cloud
- **A:** Local llama.cpp (använd `llama-cpp` skill) — inget API, full kontroll
- **B:** Cloud (OpenAI, Anthropic) — kräver API-keys
- **Rekommendation:** A — Local är rätt för throwaway

### C. Frontend — Jinja2+HTMX vs React
- **A:** Jinja2+HTMX — enklast, snabbast, inget build-step
- **B:** React — mer komplext, build-step, men bra för formulär-dynamik
- **Rekommendation:** A — Jinja2+HTMX för throwaway

## CONSTRAINTS
- Throwaway-app: koda kasta
- Local only: localhost:8150
- Local LLM: llama.cpp
- Modular: en modul per fil
- Git-versionerad: origin = git@github.com:bryn1/klartx.git
- Ingen production-integration (BankID, cloud-OCR, cloud-LLM)
