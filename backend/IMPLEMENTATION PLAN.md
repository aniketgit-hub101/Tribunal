# Tribunal — Team Implementation Plan

## Architecture (v0 scope)

```
User question
     │
     ├──► Proponent Agent (bull case, blind)
     │
     ├──► Antagonist Agent (bear case, blind)
     │
     ▼
Claim extraction (code, not LLM call — strips agent identity)
     │
     ▼
Examiner Agent (fresh agent, cross-examines stripped claims, rates severity)
     │
     ▼
Output: Bull case + Bear case + Flagged attacks
```

v0 deliberately excludes fact-checking and Judge synthesis — those are v1, built only after this core mechanism is proven to work.

## Team & roles

| Member | Role | Owns |
|---|---|---|
| **Aniket** | Orchestration & Integration Lead | FastAPI backend, identity-stripping logic, final integration, demo |
| **Adeel** | Agent Layer (Proponent, Antagonist, Examiner) | Prompt engineering, Pydantic schemas, extraction/severity logic |
| **Abhay** | Frontend + Verification/Eval Support | Next.js form + results UI, week 7 eval scoring, stretch: Tavily fact-check module (isolated, not wired into main pipeline unless stable) |

## Tech stack

- **Frontend:** Next.js, React, Tailwind — hosted on Vercel
- **Backend:** FastAPI (Python) — hosted on Railway (or Render, free-tier)
- **Database:** PostgreSQL via Supabase or Neon (free tier)
- **LLM:** Gemini API, Groq API
- **Version control:** GitHub

Zero-cost constraint: all tools above are free-tier. No paid API usage in v0.

## Build phases

### Phase 1 — Foundation (independent, parallel)
- [x] Repo created, README written
- [x] Pydantic schema for Proponent output (`schemas.py`)
- [x] Proponent agent implemented (`agents.py`) — calls Gemini, validates against schema
- [x] FastAPI endpoint wired (`main.py`) — `/analyze/proponent`
- [ ] `.env` configured with real API key, tested locally
- [ ] Antagonist agent added (mirrors Proponent, bear-case prompt)
- [ ] Next.js form shell (Abhay) — question input, no backend wiring yet

### Phase 2 — Core adversarial logic
- [ ] Claim extraction function (plain Python — strips which agent said what)
- [ ] Examiner agent — takes stripped claims, attacks assumptions, rates severity (minor/moderate/fatal)
- [ ] New endpoint `/analyze/full` — runs Proponent → Antagonist → extraction → Examiner in sequence
- [ ] Frontend wired to real backend, displays bull/bear + flagged attacks

### Phase 3 — Integration & hardening
- [ ] End-to-end test on real decision questions
- [ ] Retry/backoff for free-tier rate limits
- [ ] Graceful handling of malformed agent JSON

### Phase 4 — Eval & demo
- [ ] 10 test decisions run through pipeline vs single-model baseline
- [ ] Manual scoring: are Examiner attacks substantive or decorative?
- [ ] Demo prep — best example where Examiner catches a real flaw

## What's explicitly out of scope for v0

- Dynamic agent selection / dynamic workflows
- Multiple decision domains (locked to one domain for MVP)
- Human tie-break checkpoint
- Judge/synthesis agent
- Fact-checking in the main pipeline (Abhay's version stays isolated unless proven stable)

## Rules

- One file, one job — don't merge agent logic across functions
- Test after every file/feature, not in batches
- This document is the source of truth for scope — if it's not listed here, it's not v0
