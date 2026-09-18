from pydantic import BaseModel
from typing import List
from enum import Enum


class ClaimCategory(str, Enum):
    empirical = "empirical"
    logical = "logical"
    strategic = "strategic"


class Claim(BaseModel):
    id: str
    text: str
    category: ClaimCategory
    confidence: float  # 0.0 to 1.0


class ProponentOutput(BaseModel):
    claims: List[Claim]
    summary: str