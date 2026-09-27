import os
import json
import time
from google import genai
from google.genai import errors as genai_errors
from pydantic import ValidationError
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
    if response.text is None:
        raise ValueError("Gemini returned an empty response")
    raw_text = response.text.strip()

    # Gemini sometimes wraps JSON in markdown fences - strip them if present
    if raw_text.startswith("```"):
        raw_text = raw_text.split("```")[1]
        if raw_text.startswith("json"):
            raw_text = raw_text[4:]
    raw_text = raw_text.strip()

    data = json.loads(raw_text)
    return ProponentOutput(**data)  # validates against schema, raises if malformed


ANTAGONIST_PROMPT = """You are the Antagonist in an adversarial decision-analysis system.
Your ONLY job is to build the strongest possible case AGAINST the following decision.
Do not mention benefits, upsides, or reasons the decision might succeed.
Focus purely on risks, flaws, weaknesses, downside scenarios, failure modes,
vulnerable assumptions, and adverse consequences of going ahead with this decision.

Decision to analyze: {question}

Return ONLY valid JSON matching this exact structure, nothing else, no markdown fences:
{{
  "claims": [
    {{"id": "a1", "text": "...", "category": "empirical", "confidence": 0.8}}
  ],
  "summary": "..."
}}

category must be one of: empirical, logical, strategic
confidence must be a number between 0 and 1
Generate 3-5 claims.
"""


def run_antagonist(question: str) -> ProponentOutput:
    prompt = ANTAGONIST_PROMPT.format(question=question)

    def _call_and_parse() -> ProponentOutput:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
        )
        if response.text is None:
            raise ValueError("Gemini returned an empty response")
        raw_text = response.text.strip()

        # Gemini sometimes wraps JSON in markdown fences - strip them if present
        if raw_text.startswith("```"):
            raw_text = raw_text.split("```")[1]
            if raw_text.startswith("json"):
                raw_text = raw_text[4:]
        raw_text = raw_text.strip()

        data = json.loads(raw_text)
        return ProponentOutput(**data)  # validates against schema, raises if malformed

    # Exponential backoff for 429 (ClientError) and 503 (ServerError).
    # google.genai raises ClientError for 4xx and ServerError for 5xx;
    # both expose the HTTP status code via the .code attribute (int).
    backoff_delays = [2, 4, 8]  # seconds between retries
    result: ProponentOutput | None = None
    for attempt, delay in enumerate(backoff_delays):
        try:
            result = _call_and_parse()
            break  # success — exit the backoff loop
        except (genai_errors.ClientError, genai_errors.ServerError) as exc:
            if exc.code not in (429, 503):
                raise  # not a rate-limit/overload error; propagate immediately
            if attempt == len(backoff_delays) - 1:
                raise  # exhausted all backoff attempts
            time.sleep(delay)
        except (json.JSONDecodeError, ValidationError):
            # Retry once on malformed JSON or schema validation failure.
            result = _call_and_parse()
            break

    if result is None:
        raise RuntimeError("Antagonist analysis did not produce a result")
    return result