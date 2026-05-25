"""
The three agent nodes for Week 1.

Pattern: each node is a plain function that takes the current state and
returns a dict of state updates. LangGraph merges the updates back in.

Week 2 will: split the analyst into financial / industry / risk,
add a structured extraction node before the analyst, and add code
execution for DCF math.
"""
import json
import os
from anthropic import Anthropic

from tools import get_market_data, get_recent_filings


_client = Anthropic()
MODEL = "claude-sonnet-4-5"  # update to current Sonnet when needed


def _call_claude(prompt: str, max_tokens: int = 2000, temperature: float = 0.0) -> tuple[str, dict]:
    """Call Claude and return (text, usage). Centralized so we can add
    cost tracking and tracing in one place."""
    response = _client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        temperature=temperature,
        messages=[{"role": "user", "content": prompt}],
    )
    text = response.content[0].text
    usage = {
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
    }
    return text, usage


def _estimate_cost(usage: dict) -> float:
    """Rough Sonnet pricing — update to current rates from docs."""
    return (usage["input_tokens"] * 3.0 + usage["output_tokens"] * 15.0) / 1_000_000


# ----- Nodes -----

def data_ingestion_node(state: dict) -> dict:
    """Pull market data + filings metadata. No LLM call in week 1."""
    ticker = state["ticker"]
    print(f"[ingestion] pulling data for {ticker}")

    market = get_market_data(ticker)
    filings_10k = get_recent_filings(ticker, "10-K", limit=2)
    filings_10q = get_recent_filings(ticker, "10-Q", limit=2)

    return {
        "raw_data": {
            "market": market,
            "recent_10K": filings_10k,
            "recent_10Q": filings_10q,
        }
    }


def financial_analyst_node(state: dict) -> dict:
    """Produce a structured financial assessment from raw data."""
    ticker = state["ticker"]
    print(f"[analyst] analyzing {ticker}")

    prompt = f"""You are a buy-side equity analyst. Produce a rigorous, evidence-based financial assessment of {ticker}.

Research question: {state["question"]}

Market & fundamental data (raw JSON from yfinance):
{json.dumps(state["raw_data"]["market"], indent=2, default=str)}

Recent filings available (metadata only — you cannot read the full text yet):
10-K: {json.dumps(state["raw_data"]["recent_10K"], indent=2)}
10-Q: {json.dumps(state["raw_data"]["recent_10Q"], indent=2)}

Produce your assessment in this structure:

## Business snapshot
Two sentences. What they do, sector context.

## Key financial observations
4-6 bullets. Cite specific numbers. Flag any missing or null fields explicitly — do not invent figures.

## Valuation read
Cheap / fair / expensive vs. fundamentals. Justify with the multiples available.

## What I would investigate further
3 specific questions you would need answered before committing to a thesis. These should be things the 10-K would tell you that the market data does not.

Be opinionated. Be concrete. Never fabricate numbers."""

    text, usage = _call_claude(prompt, max_tokens=2000, temperature=0.0)
    cost = _estimate_cost(usage)
    print(f"[analyst] {usage['input_tokens']}in / {usage['output_tokens']}out tokens, ~${cost:.4f}")

    return {
        "financial_analysis": text,
        "cost_usd": state.get("cost_usd", 0.0) + cost,
    }


def memo_writer_node(state: dict) -> dict:
    """Synthesize analysis into an IC-style memo."""
    ticker = state["ticker"]
    print(f"[writer] drafting memo for {ticker}")

    prompt = f"""You are writing an investment committee memo for {ticker}.

Research question: {state["question"]}

Financial assessment to synthesize:
{state["financial_analysis"]}

Raw market data (for reference):
{json.dumps(state["raw_data"]["market"], indent=2, default=str)}

Write a concise IC memo with this structure:

# {ticker} — Investment Memo

**Recommendation:** Buy / Hold / Sell — confidence: Low / Medium / High

## Thesis
3-4 sentences. The core argument.

## Supporting points
3-5 bullets. Each tied to a specific number or fact.

## Key risks
3 bullets. What could break the thesis.

## Open questions
What you would need to verify before sizing the position. Be specific.

Constraints:
- Under 600 words total.
- State assumptions explicitly.
- Do not invent numbers. If the data is insufficient for a confident call, say so and recommend Hold."""

    text, usage = _call_claude(prompt, max_tokens=2000, temperature=0.3)
    cost = _estimate_cost(usage)
    print(f"[writer] {usage['input_tokens']}in / {usage['output_tokens']}out tokens, ~${cost:.4f}")

    return {
        "memo": text,
        "cost_usd": state.get("cost_usd", 0.0) + cost,
    }
