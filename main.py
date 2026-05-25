"""
CLI entry point.

Usage:
    python main.py NKE
    python main.py NKE --question "Is Nike's brand moat eroding given China weakness?"
"""
import argparse
import json
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

from graph import build_graph


def main():
    parser = argparse.ArgumentParser(description="Multi-agent equity research pipeline")
    parser.add_argument("ticker", help="Stock ticker, e.g. NKE")
    parser.add_argument(
        "--question",
        default="Should I take a position in this name at current levels?",
        help="Research question to drive the analysis",
    )
    args = parser.parse_args()

    ticker = args.ticker.upper()
    graph = build_graph()

    initial_state = {
        "ticker": ticker,
        "question": args.question,
        "cost_usd": 0.0,
    }

    print(f"\n=== Equity research pipeline: {ticker} ===")
    print(f"Question: {args.question}\n")

    final = graph.invoke(initial_state)

    # Save outputs
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = Path("outputs")
    out_dir.mkdir(exist_ok=True)

    memo_path = out_dir / f"{ticker}_{timestamp}_memo.md"
    state_path = out_dir / f"{ticker}_{timestamp}_state.json"

    memo_path.write_text(final["memo"])
    state_path.write_text(json.dumps(final, indent=2, default=str))

    print("\n" + "=" * 60)
    print("MEMO")
    print("=" * 60)
    print(final["memo"])
    print("\n" + "=" * 60)
    print(f"Memo: {memo_path}")
    print(f"State: {state_path}")
    print(f"Total cost: ${final.get('cost_usd', 0):.4f}")
    print("=" * 60)


if __name__ == "__main__":
    main()
