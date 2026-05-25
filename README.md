# Equity Research Agent

Multi-agent pipeline for equity research memos. LangGraph + Claude.

## Week 1 scope

Sequential pipeline: data ingestion → financial analyst → memo writer.

Intentionally not in scope yet:
- No 10-K full-text parsing (week 2)
- No DCF code execution (week 2)
- No critic / revision loop (week 3)
- No eval harness (week 4)

The point of week 1 is plumbing. Get one ticker producing a memo end-to-end.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# edit .env: add ANTHROPIC_API_KEY and your real SEC_USER_AGENT
```

The `SEC_USER_AGENT` must be a real `Name email@domain.com` string. SEC EDGAR blocks requests without it.

## Run

```bash
python main.py NKE
python main.py SNPS --question "Does the Ansys integration justify current multiples?"
```

Outputs land in `outputs/`:
- `{TICKER}_{timestamp}_memo.md` — the final memo
- `{TICKER}_{timestamp}_state.json` — full state dump for inspection

## Week 1 checklist

- [ ] Setup completes without errors
- [ ] `python main.py NKE` produces a memo
- [ ] State dump contains populated `raw_data`, `financial_analysis`, `memo`
- [ ] Run on NKE, SNPS, UNH — all three complete
- [ ] Memo for NKE roughly aligns with your existing thesis (sanity check)
- [ ] Total cost per run logged and under $0.30
- [ ] Read the SNPS memo critically — flag every claim that's unsupported by the data the agent actually had access to

## What to watch for

The week 1 analyst is reasoning over yfinance numbers + filings *metadata* only — no 10-K body text. Expect the memo to be shallow on qualitative business detail. That's the point. Week 2 fixes it by adding real document parsing.

The "investigate further" section in the analyst output is your roadmap for week 2 — those are exactly the gaps that real filings content will fill.

## File layout

```
equity-research-agent/
├── requirements.txt
├── .env.example
├── state.py         # ResearchState TypedDict
├── tools.py         # SEC + yfinance fetchers
├── agents.py        # the three nodes
├── graph.py         # LangGraph wiring
├── main.py          # CLI entry
└── outputs/         # generated memos (gitignored)
```

## Next: week 2

- Fetch full 10-K text, parse MD&A and Risk Factors sections
- Add structured extraction node (Haiku-based) producing a known financials schema
- Wire in Anthropic code execution for DCF
- Split the analyst into financial + industry + risk
