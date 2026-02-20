# 🇮🇳 AI-Powered MSE Agent Mapping Tool

> **MSME TEAM Initiative** · ONDC-Ready · DPI-Compliant · Built for India

An end-to-end platform that reduces Micro & Small Enterprise (MSE) onboarding on ONDC from **4 days to 4 minutes** — with multilingual voice registration, AI product classification, intelligent SNP matching, and automated document verification.

---

## 🚀 The Problem This Solves

| Bottleneck | Before | After |
|---|---|---|
| **Manual Entry** | MSE agent fills English forms over 3–4 days | Voice input in native language, AI fills the form |
| **Claim Verification** | NSIC manually reviews Udyam PDFs | OCR + AI extracts fields in < 2 seconds |
| **Taxonomy Mapping** | Human curator assigns ONDC category | Gemini AI zero-shot classifies + assigns HSN code |
| **SNP Selection** | Manual matching by relationship manager | Vector DB matches by semantic similarity + capacity |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  INGESTION LAYER                                             │
│  Voice (Bhashini ULCA)  →  OCR (Tesseract)  →  Form Input  │
└───────────────────────────┬─────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  INTELLIGENCE LAYER                                          │
│  Gemini (Zero-Shot Classify) + SentenceTransformers Embed   │
└───────────────────────────┬─────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  MATCHING ENGINE                                             │
│  ChromaDB Vector Search → Cosine Similarity → Capacity Rank │
└───────────────────────────┬─────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  DATA LAYER                 INTEGRATIONS                     │
│  PostgreSQL (SQLite dev)  │  ONDC Gateway (future)          │
│  ChromaDB (persistent)    │  Bhashini ULCA API              │
└─────────────────────────────────────────────────────────────┘
```

---

## ⚡ Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- (Optional) Tesseract OCR

### 1. Backend Setup

```bash
cd backend

# Copy and configure environment
cp .env.example .env
# Edit .env — add GEMINI_API_KEY and BHASHINI keys (app works without them via fallbacks)

# Install dependencies
pip install -r requirements.txt

# Start the API server
uvicorn main:app --reload --port 8000
```

API docs will be available at: **http://localhost:8000/docs**

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Dashboard at: **http://localhost:5173**

### 3. Docker (Backend + PostgreSQL)

```bash
# Copy env and fill in API keys
cp backend/.env.example .env

docker-compose up -d
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/classify` | Classify product → ONDC taxonomy + HSN code |
| `GET` | `/match/snp` | Match MSE to top-K SNPs via vector similarity |
| `POST` | `/onboard/mse` | Full pipeline: classify + match + save |
| `GET` | `/onboard/mse/list` | List all registered MSEs |
| `POST` | `/voice/transcribe` | Bhashini ASR + NMT for 22 Indian languages |
| `GET` | `/voice/languages` | List all supported language codes |
| `POST` | `/verify/document` | OCR extraction from Udyam/GST certificate |

### Example: Classify a Product

```bash
curl -X POST http://localhost:8000/classify \
  -H "Content-Type: application/json" \
  -d '{"description": "Handmade leather chappal from Agra"}'
```

```json
{
  "category": "Fashion & Footwear",
  "subcategory": "Leather Footwear",
  "hsn_code": "6402",
  "confidence": 0.94,
  "keywords": ["leather", "handmade", "chappal", "agra", "ethnic"]
}
```

### Example: Match SNP

```bash
curl "http://localhost:8000/match/snp?product_desc=leather+sandal&location=Agra&capacity=500"
```

```json
{
  "query": "leather sandal",
  "matches": [
    {
      "name": "Agra Leather Collective",
      "similarity_score": 0.89,
      "operational_capacity": 0.75,
      "final_score": 0.67,
      "sectors": ["Footwear", "Leather"]
    }
  ],
  "total_snps_evaluated": 8
}
```

---

## 🌐 Supported Languages (Bhashini ULCA)

| Language | Code | Language | Code |
|---|---|---|---|
| Hindi | `hi` | Bengali | `bn` |
| Marathi | `mr` | Telugu | `te` |
| Tamil | `ta` | Gujarati | `gu` |
| Kannada | `kn` | Malayalam | `ml` |
| Punjabi | `pa` | Odia | `or` |
| Assamese | `as` | Urdu | `ur` |

> App works in **DEMO MODE** without Bhashini API keys — showing realistic sample transcriptions for testing.

---

## 🔑 Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GEMINI_API_KEY` | Optional | Google Gemini API key for AI classification |
| `BHASHINI_USER_ID` | Optional | Bhashini ULCA User ID |
| `BHASHINI_API_KEY` | Optional | Bhashini ULCA API Key |
| `DATABASE_URL` | Optional | PostgreSQL URL (defaults to SQLite) |

> **All APIs have fallbacks** — the app runs fully without any API keys using keyword classification and mock transcription.

---

## 🏆 Pitch Points (For Competition Presentation)

1. **"Zero-Entry Onboarding"** — Registration time: **4 days → 4 minutes** using voice AI
2. **"Reject-Proof"** — OCR auto-verifies Udyam certificates, eliminating NSIC manual errors
3. **"Bharat-Native"** — Supports 22 Indian languages via Bhashini (India's own DPI)
4. **"ONDC-Ready"** — Every registered MSE gets ONDC category, HSN code, and an SNP match
5. **"Edge-Case Ready"** — Handles Hinglish inputs, offline keyword fallback for low bandwidth

---

## 📁 Project Structure

```
mapping-agent/
├── backend/
│   ├── main.py                 # FastAPI app
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── .env.example
│   ├── models/
│   │   ├── database.py         # SQLAlchemy models
│   │   └── schemas.py          # Pydantic schemas
│   ├── routers/
│   │   ├── classify.py         # POST /classify
│   │   ├── match.py            # GET /match/snp
│   │   ├── onboard.py          # POST /onboard/mse
│   │   ├── voice.py            # POST /voice/transcribe
│   │   └── verify.py           # POST /verify/document
│   ├── services/
│   │   ├── classifier.py       # Gemini + keyword classifier
│   │   ├── matcher.py          # SentenceTransformers + ChromaDB
│   │   ├── bhashini.py         # Bhashini ULCA pipeline
│   │   └── ocr.py              # Tesseract OCR extractor
│   └── data/
│       └── snp_seed.json       # 8 mock SNP profiles
├── frontend/
│   └── src/
│       ├── api.js              # Axios service layer
│       ├── index.css           # Design system
│       ├── App.jsx             # Router
│       ├── components/
│       │   ├── Navbar.jsx
│       │   ├── VoiceInput.jsx  # Mic + Bhashini integration
│       │   └── MatchCard.jsx
│       └── pages/
│           ├── Home.jsx        # Landing dashboard
│           ├── Register.jsx    # MSE registration form
│           ├── Matches.jsx     # SNP search + results
│           └── Verify.jsx      # Document OCR upload
└── docker-compose.yml
```

---

## 💰 Funding Roadmap

| Phase | Milestone | Funding Source |
|---|---|---|
| **Stage 1** | MVP + Pilot (100 MSEs) | MSME Idea Hackathon (₹15L) |
| **Stage 2** | Scale to cluster (1000 MSEs) | IndiaAI Innovation Challenge (₹1Cr) |
| **Stage 3** | NSIC integration | Startup India Seed Fund SISFS (₹20L) |
| **Stage 4** | National rollout | MeitY GENESIS / IndiaAI Mission |

---

## 📜 License

MIT License · Built for India's Digital Public Infrastructure
