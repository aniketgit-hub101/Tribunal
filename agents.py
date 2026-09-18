import os
import json
from google import genai
from dotenv import load_dotenv
from schemas import ProponentOutput

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

PROPONENT_PROMPT = """You are the Proponent in an adversarial decision-analysis system.
Your ONLY job is to build the strongest possible case FOR the following decision.
Do not mention risks or downsides. Focus purely on upside, ROI, and the bull case.

Decision to analyze: {question}

Return ONLY valid JSON matching this exact structure, nothing else, no markdown fences:
{{
  "claims": [
    {{"id": "p1", "text": "...", "category": "empirical", "confidence": 0.8}}
  ],
  "summary": "..."
}}

category must be one of: empirical, logical, strategic
confidence must be a number between 0 and 1
Generate 3-5 claims.
"""


def run_proponent(question: str) -> ProponentOutput:
    prompt = PROPONENT_PROMPT.format(question=question)
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
    )
    raw_text = response.text.strip()

    # Gemini sometimes wraps JSON in markdown fences - strip them if present
    if raw_text.startswith("```"):
        raw_text = raw_text.split("```")[1]
        if raw_text.startswith("json"):
            raw_text = raw_text[4:]
    raw_text = raw_text.strip()

    data = json.loads(raw_text)
    return ProponentOutput(**data)  # validates against schema, raises if malformed