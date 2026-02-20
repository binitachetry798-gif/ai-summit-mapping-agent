---
title: MSE Agent Mapping Tool - Backend API
emoji: 🏭
colorFrom: orange
colorTo: green
sdk: docker
app_port: 7860
pinned: false
---

# MSE Agent Mapping Tool — Backend API

FastAPI backend with Groq Voice, Sarvam AI, and Gemini AI for MSE onboarding on ONDC.

## Endpoints
- `GET /health` — Health check
- `POST /classify` — AI product classification
- `GET /match/snp` — SNP matching
- `POST /voice/transcribe/base64` — Voice transcription (Groq Whisper)
- `POST /onboard/mse` — MSE registration
