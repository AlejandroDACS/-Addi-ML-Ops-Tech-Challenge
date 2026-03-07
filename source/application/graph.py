"""
LangGraph workflow for the Emporyum Tech assistant.

Currently: fetch_user_data -> router -> [handle_general, handle_returns] -> END
"""

from langgraph.graph import StateGraph, END

from source.application.state import GraphState
from source.domain.fetch_user_data import fetch_user_data
from source.domain.router import router_node
from source.domain.handle_general import handle_general
from source.domain.handle_returns import handle_returns

def route_to_agent(state: GraphState):
    """Conditional edge from router to the specific agent."""
    selected_agent = state.get("selected_agent", "handle_general")
    if selected_agent == "handle_returns":
        return "handle_returns"
    return "handle_general"

# Build graph
workflow = StateGraph(GraphState)

workflow.add_node("fetch_user_data", fetch_user_data)
workflow.add_node("router", router_node)
workflow.add_node("handle_general", handle_general)
workflow.add_node("handle_returns", handle_returns)

workflow.set_entry_point("fetch_user_data")
workflow.add_edge("fetch_user_data", "router")

workflow.add_conditional_edges(
    "router",
    route_to_agent,
    {
        "handle_returns": "handle_returns",
        "handle_general": "handle_general",
    }
)

workflow.add_edge("handle_general", END)
workflow.add_edge("handle_returns", END)
