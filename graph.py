"""
LangGraph wiring.

Week 1: sequential pipeline.
    ingestion -> analyst -> writer -> END

Week 2 will add a structured_extraction node after ingestion.
Week 3 will add the critic node and a conditional revision edge.
"""
from langgraph.graph import StateGraph, END

from state import ResearchState
from agents import (
    data_ingestion_node,
    financial_analyst_node,
    memo_writer_node,
)


def build_graph():
    workflow = StateGraph(ResearchState)

    workflow.add_node("ingestion", data_ingestion_node)
    workflow.add_node("analyst", financial_analyst_node)
    workflow.add_node("writer", memo_writer_node)

    workflow.set_entry_point("ingestion")
    workflow.add_edge("ingestion", "analyst")
    workflow.add_edge("analyst", "writer")
    workflow.add_edge("writer", END)

    return workflow.compile()
