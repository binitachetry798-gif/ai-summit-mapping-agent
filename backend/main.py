"""
AI-Powered MSE Agent Mapping Tool — FastAPI Backend
MSME TEAM Initiative | ONDC-Ready | DPI-Compliant

Author: TEAM Initiative Dev
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from models.database import init_db
from routers import classify, match, voice, verify, onboard, contracts

load_dotenv()

# ─── App Setup ──────────────────────────────────────────────────────────────

app = FastAPI(
    title="MSE Agent Mapping Tool API",
    description="""
    ## AI-Powered MSE-to-ONDC Onboarding Platform
    
    Built for the **MSME TEAM Initiative** — This system reduces MSE registration 
    from 4 days to 4 minutes using:
    - **AI Product Classification** (Gemini API + ONDC taxonomy)
    - **Intelligent SNP Matching** (Vector Similarity via ChromaDB)
    - **Multilingual Voice Onboarding** (Bhashini ULCA — 22 Indian languages)
    - **OCR Document Verification** (Udyam/GST Certificate scanning)
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    contact={"name": "TEAM Initiative", "email": "team@mse-mapper.in"},
    license_info={"name": "MIT"},
)

# ─── CORS ───────────────────────────────────────────────────────────────────

origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000,http://localhost:8001").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routers ────────────────────────────────────────────────────────────────

app.include_router(onboard.router)
app.include_router(classify.router)
app.include_router(match.router)
app.include_router(voice.router)
app.include_router(verify.router)
app.include_router(contracts.router)

# ─── Startup ────────────────────────────────────────────────────────────────

@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup."""
    init_db()
    print("✅ Database initialized")
    print("✅ MSE Agent Mapping API is ready")


# ─── Health Check ────────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
async def root():
    return {
        "service": "MSE Agent Mapping Tool",
        "version": "1.0.0",
        "status": "running",
        "initiative": "MSME TEAM Initiative",
        "docs": "/docs",
        "endpoints": {
            "onboard": "/onboard/mse",
            "classify": "/classify",
            "match_snp": "/match/snp",
            "voice": "/voice/transcribe",
            "languages": "/voice/languages",
            "verify": "/verify/document",
            "list_mses": "/onboard/mse/list"
        }
    }


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy", "service": "mse-mapper-api"}
