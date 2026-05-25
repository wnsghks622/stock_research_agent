"""
Data fetching tools.

Week 1 keeps this simple:
- EDGAR for filings *metadata* (form type, date, URL)
- yfinance for market data and basic fundamentals

Week 2 will add: full 10-K text extraction, MD&A and risk factors parsing,
earnings call transcripts.
"""
import os
import requests
import yfinance as yf


def _headers() -> dict:
    """SEC requires a User-Agent in the form 'Name email@domain.com'."""
    ua = os.getenv("SEC_USER_AGENT")
    if not ua:
        raise RuntimeError(
            "SEC_USER_AGENT not set. SEC EDGAR will block requests without it. "
            "Set it in your .env file."
        )
    return {"User-Agent": ua}


def get_cik(ticker: str) -> str:
    """Resolve a ticker symbol to its zero-padded CIK number."""
    res = requests.get(
        "https://www.sec.gov/files/company_tickers.json",
        headers=_headers(),
        timeout=10,
    )
    res.raise_for_status()
    tickers = res.json()
    for v in tickers.values():
        if v["ticker"] == ticker.upper():
            return str(v["cik_str"]).zfill(10)
    raise ValueError(f"Ticker {ticker} not found in SEC EDGAR")


def get_recent_filings(ticker: str, form_type: str = "10-K", limit: int = 2) -> list[dict]:
    """Return recent filings of a given type with URLs to the primary document."""
    cik = get_cik(ticker)
    res = requests.get(
        f"https://data.sec.gov/submissions/CIK{cik}.json",
        headers=_headers(),
        timeout=10,
    )
    res.raise_for_status()
    data = res.json()
    recent = data["filings"]["recent"]

    filings = []
    for i, form in enumerate(recent["form"]):
        if form == form_type and len(filings) < limit:
            accession_clean = recent["accessionNumber"][i].replace("-", "")
            filings.append({
                "form": form,
                "filing_date": recent["filingDate"][i],
                "accession": recent["accessionNumber"][i],
                "primary_doc": recent["primaryDocument"][i],
                "url": (
                    f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/"
                    f"{accession_clean}/{recent['primaryDocument'][i]}"
                ),
            })
    return filings


def get_market_data(ticker: str) -> dict:
    """Pull key market and fundamental data via yfinance.

    Returns a flat dict for easy serialization into prompts. Missing fields
    come back as None — the analyst is instructed to flag missing data.
    """
    t = yf.Ticker(ticker)
    info = t.info

    hist = t.history(period="1y")
    price_change_1y = None
    if len(hist) > 1:
        price_change_1y = round(
            (hist["Close"].iloc[-1] / hist["Close"].iloc[0] - 1) * 100, 2
        )

    return {
        "name": info.get("longName"),
        "sector": info.get("sector"),
        "industry": info.get("industry"),
        "business_summary": info.get("longBusinessSummary", "")[:1500],
        "market_cap": info.get("marketCap"),
        "enterprise_value": info.get("enterpriseValue"),
        "pe_trailing": info.get("trailingPE"),
        "pe_forward": info.get("forwardPE"),
        "ev_to_ebitda": info.get("enterpriseToEbitda"),
        "price_to_book": info.get("priceToBook"),
        "price_to_sales": info.get("priceToSalesTrailing12Months"),
        "profit_margin": info.get("profitMargins"),
        "gross_margin": info.get("grossMargins"),
        "operating_margin": info.get("operatingMargins"),
        "return_on_equity": info.get("returnOnEquity"),
        "revenue_ttm": info.get("totalRevenue"),
        "revenue_growth_yoy": info.get("revenueGrowth"),
        "earnings_growth_yoy": info.get("earningsGrowth"),
        "free_cash_flow": info.get("freeCashflow"),
        "total_debt": info.get("totalDebt"),
        "total_cash": info.get("totalCash"),
        "current_price": info.get("currentPrice"),
        "52w_high": info.get("fiftyTwoWeekHigh"),
        "52w_low": info.get("fiftyTwoWeekLow"),
        "price_change_1y_pct": price_change_1y,
        "beta": info.get("beta"),
        "dividend_yield": info.get("dividendYield"),
    }
