# Independence & Accessibility Assistant — backend MVP

> Work-in-progress snapshot: the latest integration baseline fails during import because `app/database/__init__.py` references `engine`, `SessionLocal`, and `init_db`, which are absent from the active session module. Additional model files also define an alternate schema. These files are preserved pending reconciliation. The 30-test result below describes the earlier working state, not this snapshot. Member 3's newly pulled AI service is not yet connected; verified source data and the new integration tests remain pending. No frontend is included.

Python 3.11+ / FastAPI / Pydantic / SQLAlchemy / SQLite / HTTPX. No frontend is included or modified. All five modules use the same database and bearer identity. API docs: [Swagger](http://127.0.0.1:8000/docs), [OpenAPI](http://127.0.0.1:8000/openapi.json).

## Run locally

From the repository root (PowerShell):

```powershell
cd backend
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
Copy-Item .env.example .env
.venv/Scripts/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

POSIX: use `.venv/bin/python` and `cp .env.example .env`. Python packages are pinned to the versions used during development. The `.env` file is loaded relative to `backend/`. The default SQLite database is also inside `backend/`, independent of the working directory. Startup creates all tables and imports the reviewed catalogue; no separate initialization command is required. Run one worker for the SQLite MVP. `/health` checks database connectivity, not upstream AI availability.

```powershell
.venv/Scripts/python -m pytest -q
```

Tests create isolated temporary SQLite databases and use no real AI keys or external services.

Validation on Python 3.13.7: **30 tests passed**, including actual Uvicorn startup on loopback and a Malayalam chat/history HTTP journey. `pip check` also passed. The installed Starlette version emits one non-failing deprecation warning for its HTTPX-backed test client. On restricted Windows environments, asyncio's loopback socket initialization may require running tests outside the sandbox.

## Architecture

- `app/api/routes`: validated HTTP inputs, authenticated identity, typed outputs.
- `app/services`: AI adapter, file processing, language selection, assistance transitions, catalogue loading.
- `app/repositories`: record creation, ownership checks and owner-scoped lists.
- `app/models/entities.py`: eleven tables, foreign keys, indexes, timestamps and conversation/message ORM relationships.
- `app/database/session.py`: per-request transaction, commit on success, rollback on error, SQLite foreign keys enabled.
- `app/core`: environment settings, errors, request size limit and session authentication.
- `app/schemas/api.py`: public request/response contracts; extra fields rejected.

Switch `DATABASE_URL` and install a PostgreSQL driver to use PostgreSQL. Introduce migrations before changing an existing deployed schema: `create_all` only initializes tables, it does not migrate them.

## Endpoints

Except health, docs, registration and government lookup, endpoints require `Authorization: Bearer <access_token>`. Success bodies are typed JSON objects or lists; errors always have `{"error":{"code":"...","message":"..."}}`. Validation errors add field paths without echoing submitted values. Use Swagger for all fields and schemas.

| Method | Path | Purpose |
| --- | --- | --- |
| POST | `/api/users` | Create demo user and expiring bearer token (201) |
| GET | `/api/users/me` | Current user |
| DELETE | `/api/users/sessions` | Revoke user's sessions (204) |
| POST | `/api/assistant/chat` | Text question; optional conversation `session_id` |
| GET | `/api/assistant/history/{session_id}` | Owner-only conversation |
| POST | `/api/assistant/upload` | Multipart `file` and `language` (201) |
| POST | `/api/assistant/speech` | TTS through a capable gateway; otherwise 501 |
| GET | `/api/government/schemes?q=&language=` | Search reviewed knowledge |
| GET | `/api/government/schemes/{id}` | Reviewed details and source |
| POST | `/api/guardian/analyze` | Redacted suspicious text; structured risk |
| POST, GET | `/api/family/contacts` | Private emergency contacts |
| DELETE | `/api/family/contacts/{id}` | Remove contact (204) |
| POST, GET | `/api/family/members` | Link an existing user record |
| PUT | `/api/family/members/{id}/consent` | Grant/revoke assistance sharing |
| POST | `/api/family/assistance` | Create a consent-controlled request (201) |
| GET | `/api/family/assistance/inbox` | Recipient sees requests with active consent |
| GET | `/api/human-help/helpers` | Available verified helpers; demo flags explicit |
| POST, GET | `/api/human-help/requests` | Create/list owner's assistance requests |
| GET, PATCH | `/api/human-help/requests/{id}` | Owner reads or advances workflow |

Lists are capped (100 schemes/helpers, 200 contacts/requests/members). Conversation history returns the whole conversation; the provider receives the latest 20 messages. Add pagination and retention policies for production.

## Frontend integration and complete journey

`examples/api-client.js` is a standalone integration example with one central backend URL, not a new frontend. Keep the session token in memory; never put it in URLs. CORS origins are an explicit JSON list in `.env`.

1. `POST /api/users` with `{"name":"അമ്മ","language":"ml"}`. Save `user.id` and `access_token`.
2. With the bearer header, `POST /api/assistant/chat` with `{"text":"പെൻഷൻ അപേക്ഷിക്കാൻ സഹായിക്കാമോ?","language":"ml"}`.
3. Receive `{"session_id":"<uuid>","answer":{"text":"...","steps":["..."],"language":"ml","is_mock":true}}`. Display a visible mock label when `is_mock` is true.
4. Fetch `/api/assistant/history/<uuid>` to retrieve the saved question and answer.
5. Create `/api/human-help/requests` with `{"category":"government","description":"അപേക്ഷിക്കാൻ സഹായം വേണം"}`.
6. List helpers. PATCH the request with `{"status":"assigned","helper_id":"demo-helper"}`, then `{"status":"in_progress"}`, then `{"status":"resolved","resolution":"സഹായം ലഭിച്ചു"}`.

Allowed statuses: `pending → assigned → in_progress → resolved`; cancellation is allowed from any nonterminal state. Resolution text is mandatory when resolving. The owner manages status for this MVP. No actual helper is contacted.

For family sharing, register a second identity, link it using `member_user_id`, then PUT `{"granted":true}` to its consent endpoint. Create a family assistance request with that member record ID. Only that request's category, description, timestamps and progress appear in the recipient inbox. Revoking consent removes inbox access immediately; previously seen information cannot be recalled. Contacts, chat histories and uploaded files are never shared through family access. Family members cannot update the owner's requests.

## Member 3 AI integration

No Member 3 implementation existed in the repository. `AIService` defines separate chat, image, document, transcription, speech and safety operations. `MockAI` gives clearly labelled bilingual test replies; its guardian result is simple keyword screening, not a real phishing model. Voice mock operations return 501, never fabricated audio/transcripts.

To connect an AI service, set `AI_PROVIDER=http`, `AI_BASE_URL`, `AI_API_KEY`, `AI_MODEL`, and the supported `AI_CAPABILITIES` list. `HTTPAI` sends POST requests to `<base>/<operation>` with optional bearer credentials. The gateway should implement provider-specific models/format support and enforce its own output safety policies. Alternatively inject an implementation using `create_app(settings, ai=adapter)`.

| Operation | JSON request (plus `model`) | Response |
| --- | --- | --- |
| `chat` | `text`, `language`, `history: [{role,text}]` | AIResult |
| `document` | extracted `text`, `language` | AIResult |
| `image` | `data_base64`, `media_type`, `language` | AIResult |
| `transcribe` | `data_base64`, `media_type`, `language` | AIResult (text is transcription) |
| `safety` | `text`, `language` | SafetyOut |
| `speak` | `text`, `language` | SpeechOut |

AIResult: `{"text":"...","steps":[],"language":"ml","is_mock":false}`.
SafetyOut: `{"risk_level":"unknown","reason":"...","warning_signs":[],"recommended_safe_action":"...","language":"ml","is_mock":false}`. Risk levels: low/medium/high/unknown. The backend adds a fixed disclaimer: predictions do not prove safety.
SpeechOut: `{"audio_base64":"...","media_type":"audio/wav","is_mock":false}` (or `audio/mpeg`).

Gateway calls have an explicit HTTPX timeout. Unavailable/malformed providers return sanitized 503 responses without saving half a conversation. Unsupported operations return 501. Real-provider failure never silently falls back to mock. The adapter does not follow redirects. Language selection is separate from business logic; Malayalam characters take priority for mixed input, while explicit `ml`/`en` wins. The provider is responsible for translation and the quality of language output.

## Government knowledge

`data/schemes.json` intentionally contains `[]`: no approved source documents were supplied. Search returns an explicit bilingual unavailable message. Do not fill this with generated claims. A trusted maintainer can supply a JSON list matching `SchemeIn` in `app/schemas/api.py`: id, title, language, description, eligibility[], benefits[], documents[], procedure[], source_url, verified_at (ISO timestamp), verified (boolean). Verify the exact claims against the source before setting `verified=true`. Restart to import/upsert. Set an existing record to `verified=false` to withdraw it; removing it from the file alone does not delete database records. No public catalogue-write endpoint exists. Verification reflects maintainer review, not automated fact checking. Automated tests use synthetic fixtures only.

## File handling and privacy

Supported: PNG/JPEG/WebP (decoded format checked, 16 million pixel limit), UTF-8 TXT, unencrypted text PDF (30 pages), PCM WAV (120 seconds, only with transcription capability). PDF without extractable text returns 422; DOC/DOCX/MP3 and other formats return 415. File bytes determine format; browser MIME claims are not trusted. Default file limit is 10 MiB, with a separate total request limit including multipart overhead. Originals and filenames are never persisted or exposed; only media type, byte count, owner, ID and timestamp are stored. Text is extracted before invoking the document adapter. Image/audio bytes go only to the configured provider when supported. Upload explanations are returned directly and not added to chat history.

Do not submit actual passwords, PINs or OTPs, including inside attachments. Intake rejects common labelled secrets and standalone 4–8 digit codes before storage/provider calls; this intentionally also rejects some innocent numbers. This heuristic cannot guarantee detection of arbitrary unlabeled passwords, secrets in images/audio, or secrets embedded in contact fields. The backend does not log request bodies or persist original uploads, but cannot promise never to process a secret a user submits. A strict no-secret environment must disable binary uploads or add a vetted redaction service before external AI access. Provider retention policies must be reviewed separately.

## MVP limitations

- Registration creates an anonymous demo identity with a random token (only its SHA-256 digest is stored). Tokens expire after 24 hours by default; there is no recovery, identity proofing, refresh, or production login. Losing/expiring the token loses access through this API. Use a real identity provider before deployment.
- Demo helpers are explicitly simulated. Set `SEED_DEMO_HELPERS=false` for a fresh non-demo database. Already seeded records remain until an administrator removes them. No SMS, email, emergency dispatch, payments, or live notifications are implemented. Family uses a real database-backed polling inbox.
- No real model, speech service or reviewed government dataset is bundled. HTTP integration is contract-tested with mocks, not validated against a teammate's live service.
- Local MVP only: add TLS, rate limits, production authentication, database migrations/backups, retention/deletion policies, upload scanning and stronger resource isolation before public hosting. Request-size limits do not replace connection/concurrency limits at a reverse proxy.
