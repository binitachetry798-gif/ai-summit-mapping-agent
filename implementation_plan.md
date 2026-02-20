# AI-Powered MSE Agent Mapping Tool — Implementation Plan

An end-to-end platform targeting the **MSME TEAM Initiative** government competition. The system enables Micro & Small Enterprises (MSEs) to register via multilingual voice, automatically classifies their products using AI, matches them with ONDC Seller Network Participants (SNPs) via vector similarity, and verifies Udyam/GST credentials — reducing onboarding from **4 days → 4 minutes**.

---

## Stack Overview

| Layer | Technology |
|---|---|
| Backend API | Python 3.11, FastAPI, Uvicorn |
| AI / NLP | Sentence-Transformers (`all-MiniLM-L6-v2`), Google Gemini API |
| Voice / ASR | Bhashini ULCA Pipeline API |
| OCR | pytesseract + pdf2image |
| Data | PostgreSQL (SQLAlchemy ORM), Alembic migrations |
| Vector DB | ChromaDB (local, no infra needed for MVP) |
| Frontend | React 18, Vite, Axios |
| DevOps | Docker Compose (backend + PostgreSQL) |

> [!IMPORTANT]
> No paid cloud vector DB (Pinecone/Weaviate) is required. **ChromaDB** runs in-process for the MVP, making the project 100% runnable locally even without internet after setup.

---

## Proposed Changes

### Backend

#### [NEW] `mapping-agent/backend/` directory

```
backend/
├── main.py               # FastAPI app entrypoint
├── requirements.txt
├── .env.example
├── models/
│   ├── database.py       # SQLAlchemy engine & session
│   └── schemas.py        # Pydantic models
├── routers/
│   ├── onboard.py        # POST /onboard/mse
│   ├── classify.py       # POST /classify
│   ├── match.py          # GET /match/snp
│   ├── voice.py          # POST /voice/transcribe
│   └── verify.py         # POST /verify/document
├── services/
│   ├── classifier.py     # Gemini-based product taxonomy classifier
│   ├── matcher.py        # Sentence-Transformers + ChromaDB SNP matcher
│   ├── bhashini.py       # Bhashini ASR + NMT pipeline wrapper
│   └── ocr.py            # Udyam/GST certificate OCR extractor
├── data/
│   └── snp_seed.json     # Mock SNP profiles for matching
└── alembic/              # DB migrations
```

#### [NEW] `backend/main.py`
FastAPI app with CORS, router mounting, and health check.

#### [NEW] `backend/routers/classify.py`
- `POST /classify` — accepts a product description string
- Calls `services/classifier.py` which uses the Gemini API to zero-shot classify into ONDC taxonomy + assign HSN code
- Falls back to keyword matching if Gemini key is absent

#### [NEW] `backend/routers/match.py`
- `GET /match/snp?product_desc=...&location=...&capacity=...`
- Calls `services/matcher.py` — encodes MSE profile with `all-MiniLM-L6-v2`
- Queries ChromaDB for top-3 SNP matches by cosine similarity
- Multiplies similarity score by SNP operational capacity for final ranking

#### [NEW] `backend/routers/voice.py`
- `POST /voice/transcribe` — accepts `audio_base64` + `source_lang` (ISO code, e.g. `hi`, `mr`, `ta`)
- Calls `services/bhashini.py` which invokes the Bhashini ASR → NMT (→ English) pipeline
- Returns transcribed + translated English text for form auto-fill

#### [NEW] `backend/routers/verify.py`
- `POST /verify/document` — accepts uploaded PDF/image of Udyam or GST certificate
- Calls `services/ocr.py` which runs pytesseract to extract GSTIN/Udyam number
- Returns extracted fields + verification status

#### [NEW] `backend/routers/onboard.py`
- `POST /onboard/mse` — full MSE onboarding: saves to PostgreSQL, triggers classify + match

---

### Frontend

#### [NEW] `mapping-agent/frontend/` directory (Vite + React)

```
frontend/
├── index.html
├── vite.config.js
├── src/
│   ├── main.jsx
│   ├── App.jsx
│   ├── index.css          # Design system: dark glassmorphism, gradients
│   ├── api.js             # Axios service layer → backend
│   └── pages/
│       ├── Register.jsx   # MSE registration: voice + manual form
│       ├── Matches.jsx    # SNP match results with confidence scores
│       └── Verify.jsx     # Document upload + OCR results
│   └── components/
│       ├── VoiceInput.jsx # Mic button + language dropdown (22 languages)
│       ├── CategoryBadge.jsx
│       ├── MatchCard.jsx  # SNP match card with score bar
│       └── Navbar.jsx
```

**Design:** Dark glassmorphism, saffron-green-blue Indian DPI color palette, smooth micro-animations, Google Fonts (Inter). Mobile-first and low-bandwidth friendly.

---

### Root Files

#### [NEW] `mapping-agent/README.md`
Competition-ready README covering:
- Problem statement (manual entry + claim verification bottlenecks)
- How each module solves the bottleneck
- Setup instructions
- API reference
- Funding roadmap table

#### [NEW] `mapping-agent/docker-compose.yml`
Spins up PostgreSQL + backend containers.

---

## Verification Plan

### Automated / Terminal Tests

```bash
# 1. Install backend deps
cd backend && pip install -r requirements.txt

# 2. Start backend (no Docker needed for quick test)
uvicorn main:app --reload --port 8000

# 3. Test /classify endpoint
curl -X POST "http://localhost:8000/classify" \
  -H "Content-Type: application/json" \
  -d '{"description": "Handmade leather chappal from Agra"}'
# Expected: {"category": "Fashion & Footwear", "subcategory": "Ethnic > Leather", "hsn_code": "6402"}

# 4. Test /match/snp endpoint
curl "http://localhost:8000/match/snp?product_desc=leather+sandal&location=Agra&capacity=500"
# Expected: top-3 SNP matches with scores

# 5. Test /verify/document (OCR)
curl -X POST "http://localhost:8000/verify/document" \
  -F "file=@sample_udyam.pdf"
# Expected: {"udyam_number": "UDYAM-UP-...", "status": "verified"}
```

### Browser / Visual Tests

```
1. Run frontend: cd frontend && npm run dev  → open http://localhost:5173
2. Click "Register MSE" → select Hindi → click mic icon
   → speak a product description → confirm English translation appears in form
3. Submit form → navigate to /matches → verify 3 SNP cards with scores render
4. Navigate to /verify → upload a PDF → confirm extracted fields are shown
```

### Manual Verification (Competition Demo Flow)
1. Open the dashboard at `http://localhost:5173`
2. Select language "मराठी (Marathi)" from the dropdown
3. Record sample audio → confirm the form auto-fills in English
4. Check the AI-assigned ONDC category and HSN code
5. View SNP match cards with percentage scores and domain labels
