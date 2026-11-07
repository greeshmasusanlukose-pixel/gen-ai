# gen-ai

The FastAPI backend is in [`backend/`](backend/README.md). See its README for local setup, API documentation, AI integration contracts, frontend examples, tests and MVP limitations.

## AI/LLM Service — Kerala Accessibility Assistant

**Hackathon MVP: AI-Powered Independence & Accessibility Assistant for senior citizens and persons with disabilities in Kerala.**  
**Ownership: Member 3 (AI/LLM Service)**

---

### 📌 Integration Guide for Backend (Member 4)

This module provides the core AI assistance engine. It generates dignified, easy-to-read-aloud responses in **Malayalam (`ml`)** and **English (`en`)**, validates all outputs against a strict response schema, enforces strict citations from verified context, and guards against sensitive credential leaks (e.g., OTPs, PINs, card numbers).

---

### 🚀 Quick Start

#### 1. Environment Variable Setup

Set your Gemini API key in your `.env` file (or system environment):

```bash
# In .env
GEMINI_API_KEY=your_google_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
AI_SERVICE_TIMEOUT_SECONDS=15.0
```

> **Note**: If no API key is configured during local frontend/backend development, the service automatically uses a safe offline mock assistant so your local development and testing never crash.

#### 2. How to Call the Service in Your Backend

```python
from ai_service import generate_assistance

# Example 1: Malayalam Government Services (with verified context)
result_ml = generate_assistance(
    user_text="ക്ഷേമ പെൻഷൻ ലഭിക്കാൻ എന്തൊക്കെ വേണം?",
    module="government_services",
    language="ml",
    verified_context=[
        {
            "id": "sevana_doc_01",
            "title": "Sevana Pension Scheme",
            "text": "സേവന പെൻഷൻ ലഭിക്കുന്നതിനായി വരുമാന സർട്ടിഫിക്കറ്റ്, ആധാർ കാർഡ്, ബാങ്ക് പാസ്ബുക്ക് എന്നിവ ആവശ്യമാണ്.",
        }
    ],
)

# Example 2: Digital Safety Check (e.g., analyzing suspicious SMS)
result_en = generate_assistance(
    user_text="Message from unknown sender says account is blocked unless I send code 4491.",
    module="digital_safety",
    language="en",
)
```

---

### 📋 Service Interface Contract

#### Function Signature

```python
def generate_assistance(
    user_text: str,
    module: str,
    language: str,
    verified_context: Optional[List[Dict[str, Any]]] = None,
    prepared_image: Optional[Any] = None,
) -> Dict[str, Any]:
```

#### Input Parameters

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `user_text` | `str` | **Yes** | User's question or OCR/extracted text. Must be non-empty. |
| `module` | `str` | **Yes** | One of: `"government_services"`, `"everyday_tasks"`, `"digital_safety"`, `"family_support"`, `"human_help"`. |
| `language` | `str` | **Yes** | `"ml"` for Malayalam, `"en"` for English. |
| `verified_context` | `list[dict]` | No | Optional list of trusted excerpts: `[{"id": "doc_1", "text": "...", "title": "..."}]`. |
| `prepared_image` | `Any` | No | Optional prepared image (`PIL.Image`, raw bytes, or base64 dict). Does not block text MVP. |

---

### 📦 Exact Return Dictionary Structure

Every response strictly adheres to this structure with guaranteed types:

```json
{
  "language": "ml | en",
  "module": "government_services | everyday_tasks | digital_safety | family_support | human_help",
  "reply": "Short, accessible answer in the requested language",
  "steps": ["Step 1", "Step 2"],
  "warnings": ["Warning if any"],
  "source_refs": ["IDs of verified excerpts actually used"],
  "needs_human_help": false,
  "follow_up_question": "Optional single follow-up question or null"
}
```

### Field Guarantees
- **`language`**: Always `"ml"` or `"en"`.
- **`module`**: Always one of the 5 supported modules.
- **`reply`**: Concise, respectful, easy-to-read-aloud answer.
- **`steps`**: List of strings (empty `[]` if none).
- **`warnings`**: List of strings (empty `[]` if none).
- **`source_refs`**: List of source IDs from `verified_context` actually used (empty `[]` if none). **Never hallucinates citations.**
- **`needs_human_help`**: Boolean `true`/`false`. Automatically set to `true` for emergency/hazardous tasks, unverified government queries, or system fallbacks.
- **`follow_up_question`**: Single question string or `null` (`None` in Python).

---

### 🛡️ Privacy & Security Design

1. **On-Device/Local Privacy Masking**: Aadhaar numbers, phone numbers, credit card numbers, and credentials are automatically masked before any request is sent to cloud AI APIs.
2. **Backend Privacy Validation**: Unmasked credentials or raw PII are caught and sanitized before cloud dispatch.
3. **Government Services**: Answers strictly from supplied `verified_context`. If context is missing, it states the detail cannot be confirmed and flags `needs_human_help: true`.
4. **Digital Safety**: Identifies observable warning signs without claiming absolute certainty. Recommends verified official channels (e.g., Cyber Helpline 1930) and never requests or echoes OTPs, PINs, or bank numbers.
5. **Human Assistance**: Human assistance is strictly permission-based; the AI suggests contacts but never automatically contacts anyone.

## AI/LLM Service — Kerala Accessibility Assistant

**Hackathon MVP: AI-Powered Independence & Accessibility Assistant for senior citizens and persons with disabilities in Kerala.**  
**Ownership: Member 3 (AI/LLM Service)**

---

### 📌 Integration Guide for Backend (Member 4)

This module provides the core AI assistance engine. It generates dignified, easy-to-read-aloud responses in **Malayalam (`ml`)** and **English (`en`)**, validates all outputs against a strict response schema, enforces strict citations from verified context, and guards against sensitive credential leaks (e.g., OTPs, PINs, card numbers).

---

### 🚀 Quick Start

#### 1. Environment Variable Setup

Set your Gemini API key in your `.env` file (or system environment):

```bash
# In .env
GEMINI_API_KEY=your_google_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
AI_SERVICE_TIMEOUT_SECONDS=15.0
```

> **Note**: If no API key is configured during local frontend/backend development, the service automatically uses a safe offline mock assistant so your local development and testing never crash.

#### 2. How to Call the Service in Your Backend

```python
from ai_service import generate_assistance

# Example 1: Malayalam Government Services (with verified context)
result_ml = generate_assistance(
    user_text="ക്ഷേമ പെൻഷൻ ലഭിക്കാൻ എന്തൊക്കെ വേണം?",
    module="government_services",
    language="ml",
    verified_context=[
        {
            "id": "sevana_doc_01",
            "title": "Sevana Pension Scheme",
            "text": "സേവന പെൻഷൻ ലഭിക്കുന്നതിനായി വരുമാന സർട്ടിഫിക്കറ്റ്, ആധാർ കാർഡ്, ബാങ്ക് പാസ്ബുക്ക് എന്നിവ ആവശ്യമാണ്.",
        }
    ],
)

# Example 2: Digital Safety Check (e.g., analyzing suspicious SMS)
result_en = generate_assistance(
    user_text="Message from unknown sender says account is blocked unless I send code 4491.",
    module="digital_safety",
    language="en",
)
```

---

### 📋 Service Interface Contract

#### Function Signature

```python
def generate_assistance(
    user_text: str,
    module: str,
    language: str,
    verified_context: Optional[List[Dict[str, Any]]] = None,
    prepared_image: Optional[Any] = None,
) -> Dict[str, Any]:
```

#### Input Parameters

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `user_text` | `str` | **Yes** | User's question or OCR/extracted text. Must be non-empty. |
| `module` | `str` | **Yes** | One of: `"government_services"`, `"everyday_tasks"`, `"digital_safety"`, `"family_support"`, `"human_help"`. |
| `language` | `str` | **Yes** | `"ml"` for Malayalam, `"en"` for English. |
| `verified_context` | `list[dict]` | No | Optional list of trusted excerpts: `[{"id": "doc_1", "text": "...", "title": "..."}]`. |
| `prepared_image` | `Any` | No | Optional prepared image (`PIL.Image`, raw bytes, or base64 dict). Does not block text MVP. |

---

### 📦 Exact Return Dictionary Structure

Every response strictly adheres to this structure with guaranteed types:

```json
{
  "language": "ml | en",
  "module": "government_services | everyday_tasks | digital_safety | family_support | human_help",
  "reply": "Short, accessible answer in the requested language",
  "steps": ["Step 1", "Step 2"],
  "warnings": ["Warning if any"],
  "source_refs": ["IDs of verified excerpts actually used"],
  "needs_human_help": false,
  "follow_up_question": "Optional single follow-up question or null"
}
```

### Field Guarantees
- **`language`**: Always `"ml"` or `"en"`.
- **`module`**: Always one of the 5 supported modules.
- **`reply`**: Concise, respectful, easy-to-read-aloud answer.
- **`steps`**: List of strings (empty `[]` if none).
- **`warnings`**: List of strings (empty `[]` if none).
- **`source_refs`**: List of source IDs from `verified_context` actually used (empty `[]` if none). **Never hallucinates citations.**
- **`needs_human_help`**: Boolean `true`/`false`. Automatically set to `true` for emergency/hazardous tasks, unverified government queries, or system fallbacks.
- **`follow_up_question`**: Single question string or `null` (`None` in Python).

---

### 🛡️ Privacy & Security Design

1. **On-Device/Local Privacy Masking**: Aadhaar numbers, phone numbers, credit card numbers, and credentials are automatically masked before any request is sent to cloud AI APIs.
2. **Backend Privacy Validation**: Unmasked credentials or raw PII are caught and sanitized before cloud dispatch.
3. **Government Services**: Answers strictly from supplied `verified_context`. If context is missing, it states the detail cannot be confirmed and flags `needs_human_help: true`.
4. **Digital Safety**: Identifies observable warning signs without claiming absolute certainty. Recommends verified official channels (e.g., Cyber Helpline 1930) and never requests or echoes OTPs, PINs, or bank numbers.
5. **Human Assistance**: Human assistance is strictly permission-based; the AI suggests contacts but never automatically contacts anyone.
