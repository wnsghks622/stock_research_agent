"""
Shared state for the research pipeline.

Every agent reads from and writes to this object. Avoiding direct
agent-to-agent messaging makes the system inspectable: at any point
in the run you can dump the state and see exactly what each agent saw.

Week 1 is intentionally minimal. Week 2-3 additions noted inline.
"""
from typing import TypedDict, Optional


class ResearchState(TypedDict, total=False):
    # Inputs
    ticker: str
    question: str

    # Filled by data ingestion node
    raw_data: dict

    # Filled by financial analyst node
    financial_analysis: str

    # Filled by memo writer node
    memo: str

    # Cost tracking (filled incrementally)
    cost_usd: float

    # Week 2+: structured: dict   (extracted financials)
    # Week 3+: critique: list[dict]
    # Week 3+: revision_count: int
