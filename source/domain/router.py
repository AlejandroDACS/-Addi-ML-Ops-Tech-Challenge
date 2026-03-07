from source.application.state import GraphState
from source.adapters.chains.router_chain import get_router_chain
from source.adapters.utils.knowledge_base import SCENARIO_KNOWLEDGE_BASE

async def router_node(state: GraphState) -> GraphState:
    """Analyze user input and route to the correct agent."""
    
    # If a return is already in progress, bypass routing to remain in the Returns flow
    if state.get("is_return_in_progress"):
        return {
            "selected_topic": "DEVOLUCIONES",
            "selected_agent": "handle_returns",
            "router_reasoning": "Bypassed router: Return flow in progress.",
            "flow": state.get("flow", []) + ["router(bypassed)"]
        }
        
    chain = get_router_chain()
    
    topics_list = "\n".join([f"- {topic}: {SCENARIO_KNOWLEDGE_BASE[topic]['contexto']}" for topic in SCENARIO_KNOWLEDGE_BASE])
    
    result = await chain.ainvoke({
        "question": state["question"],
        "messages": state.get("messages", []),
        "topics_list": topics_list
    })
    
    selected_topic = result.selected_topic
    
    # Validation fallback just in case the LLM hallucinates a topic
    if selected_topic not in SCENARIO_KNOWLEDGE_BASE:
        selected_topic = "FUERA_DE_ALCANCE"
        
    selected_agent = SCENARIO_KNOWLEDGE_BASE[selected_topic]["responsible_agent"]

    return {
        "selected_topic": selected_topic,
        "selected_agent": selected_agent,
        "router_reasoning": result.reasoning,
        "flow": state.get("flow", []) + ["router"]
    }
