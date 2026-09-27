# Tribunal — API & Schema Contracts

This file is the source of truth for what JSON shape each pipeline stage
takes in and returns. If you're building against Tribunal's backend —
frontend, a new agent, or a new pipeline stage — build against what's
written here, not against what you assume the code does.

**Owner of this file: Aniket.** Changes to a contract must be agreed with
whoever consumes it before merging. If you need a field that isn't here,
raise it — don't just add it to your local `schemas.py` and push.

Status legend: ✅ implemented and verified · 🚧 planned, not built.

---

## Shared output shape: `ProponentOutput`

Used by both the Proponent (bull-case) and Antagonist (bear-case) agents.
There is deliberately **one shared shape**, not two separate ones — do not
add `AntagonistOutput` or similar.

```json
{
  "claims": [
    {
      "id": "a1",
      "text": "string — the claim itself",
      "category": "empirical | logical | strategic",
      "confidence": 0.85
    }
  ],
  "summary": "string — overall summary of this agent's position"
}
```

Rules:
- `category` is one of exactly three values: `empirical`, `logical`, `strategic`.
- `confidence` is a float between 0 and 1.
- Claim count is not fixed by schema but agents are prompted for 3-5.
- `id` is a short string, unique within the response (e.g. `p1`, `p2` for
  Proponent; `a1`, `a2` for Antagonist) — not globally unique yet. If claim
  extraction (below) needs global uniqueness across both agents' outputs
  combined, that's an open question to resolve before building that stage.

## Endpoints — Stage 1: Blind Draft ✅

Both endpoints take the same request shape and return the same response
shape (`ProponentOutput` above). They are independent calls — neither
agent sees the other's output. This is intentional and must not change;
it's what "blind" means in Blind Draft.

### `POST /analyze/proponent` ✅
Request:
```json
{ "question": "string — the decision being analyzed" }
```
Response: `ProponentOutput`, bull-case framing.

### `POST /analyze/antagonist` ✅
Request:
```json
{ "question": "string — the decision being analyzed" }
```
Response: `ProponentOutput`, bear-case framing (same shape, opposite stance).

Both endpoints: on failure, return HTTP 500 with `{"detail": "<error string>"}`.
Internally: one retry on malformed JSON/schema failure, exponential backoff
on Gemini 429/503 (see `agents.py` for current known defects in that logic —
not repeated here since this file is about contracts, not implementation
status).

---

## Stage 2: Cross-Examination (Examiner) 🚧

Not yet built. Draft shape below — **not final, needs sign-off from
whoever implements it (Adeel) before frontend or orchestration code
depends on it.**

Input: both agents' outputs together (this is the first stage that sees
both sides — by design, since blindness only applies to Stage 1).

```json
{
  "question": "string",
  "proponent": { "...ProponentOutput shape..." },
  "antagonist": { "...ProponentOutput shape..." }
}
```

Open questions to resolve before building this:
- Does the Examiner return a new shape (e.g. `ExaminerOutput` with
  per-claim critiques), or annotate the existing claims in place?
- Does it reference claims by their `id`s? If so, `id`s likely need to be
  unique across both agents' outputs combined — current `a1`/`p1` scheme
  may need revisiting.
- Does it produce its own confidence scores, or adjust the original ones?

Do not start implementing this endpoint until these are answered in this
file.

## Stage 3: Fact-Checking 🚧 (v1, not v0 — out of scope for now)

No contract drafted yet. Do not build against this.

## Stage 4: Synthesis / Judge 🚧 (v1, not v0 — out of scope for now)

No contract drafted yet. Do not build against this.

---

## For frontend work (Abhay)

Until Examiner exists, the frontend can be built against Stage 1 alone:
send a `question`, call both `/analyze/proponent` and `/analyze/antagonist`
(can be done in parallel client-side, since they're independent), and
render two `ProponentOutput` results side by side. That's a complete,
demoable v0 slice on its own — you don't need to wait for Examiner to
start frontend work.

If you want to build against a fake/mock instead of the live backend
(recommended, so you're not blocked by rate limits or server uptime), use
the example response in Section "Real endpoint test" of
`TRIBUNAL_CONTEXT_AND_PROGRESS.md` as your fixture.

## Change log

- Initial draft — Stage 1 contracts documented from working, audited
  implementation. Stage 2 sketched as open questions, not committed.
