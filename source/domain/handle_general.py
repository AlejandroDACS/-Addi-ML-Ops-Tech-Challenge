from typing import Any, Dict

from source.application.state import GraphState
from source.adapters.utils.knowledge_base import SCENARIO_KNOWLEDGE_BASE
from source.adapters.utils.data_filter import filter_user_data
from source.adapters.chains.general_chain import get_general_chain

async def handle_general(state: GraphState) -> Dict[str, Any]:
    """Handle questions dynamically based on the selected topic's KB entry."""

    # Default to FUERA_DE_ALCANCE if no topic was selected
    selected_topic = state.get("selected_topic", "FUERA_DE_ALCANCE")
    kb_entry = SCENARIO_KNOWLEDGE_BASE.get(selected_topic, SCENARIO_KNOWLEDGE_BASE["FUERA_DE_ALCANCE"])

    relevant_fields = kb_entry.get("variables", [])
    filtered_data = filter_user_data(state.get("user_data"), relevant_fields)

    knowledge_base_text = f"CONTEXTO: {kb_entry['contexto']}\n\nINSTRUCCIONES:\n{kb_entry['instrucciones']}"

    try:
        chain = get_general_chain()
        result = await chain.ainvoke({
            "knowledge_base": knowledge_base_text,
            "user_data": str(filtered_data),
            "messages": state.get("messages", []),
            "question": state["question"],
        })

        return {"generation": result.respuesta_final}

    except Exception as e:
        print(f"[ERROR] handle_general failed: {e}")
        return {
            "generation": "Disculpa, tuve un problema procesando tu solicitud. Por favor intenta de nuevo o contacta a nuestro equipo de soporte.",
        }
