# Tribunal

**Adversarial Adjudication Engine** — a deterministic multi-agent system for stress-testing high-stakes decisions.

## What this is

Instead of asking a single AI model a complex decision question, Tribunal runs the question through a structured, adversarial pipeline:

1. **Blind Draft** — two agents independently build the strongest case *for* and *against* the decision, without seeing each other's work.
2. **Cross-Examination** — a third, fresh agent attacks the claims from both sides, identifying logical gaps and weak assumptions.
3. *(Planned for v1)* **Fact-Checking** — empirical claims get verified against live web search.
4. *(Planned for v1)* **Synthesis** — a Judge agent produces a final Decision Matrix, with human tie-break on unresolved conflicts.

This is deliberately **not** a chatbot group-chat. Every step is a fixed, structured pipeline with schema-validated JSON output — no open-ended conversation loops.

## Why

Multi-agent AI frameworks often degrade into consensus bias, where agents agree too easily and compound each other's mistakes. Tribunal is built to avoid that by keeping agents blind to each other during initial reasoning, then structuring disagreement deliberately rather than letting it emerge from free chat.

## Current status (v0 — in progress)

- [x] Project architecture defined
- [x] Backend scaffolded (FastAPI)
- [x] Pydantic schema for agent output
- [x] Proponent agent (bull-case) — calls Gemini API, returns structured JSON
- [ ] Antagonist agent (bear-case)
- [ ] Claim extraction + identity-stripping
- [ ] Examiner agent (cross-examination)
- [ ] Frontend (Next.js)

## Tech stack

- **Frontend:** Next.js, React, Tailwind — hosted on Vercel
- **Backend:** FastAPI (Python) — hosted on Railway (or Render)
- **Database:** PostgreSQL via Supabase or Neon
- **LLM:** Gemini API, Groq API
- **Version control:** GitHub

## Team

Aniket (lead, orchestration/backend), Adeel (agent logic), Abhay (frontend + eval + Authentication)
