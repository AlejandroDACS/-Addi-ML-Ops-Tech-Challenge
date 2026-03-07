from typing import Any, Dict

from source.application.state import GraphState
from source.adapters.utils.data_filter import filter_user_data
from source.adapters.chains.returns_chain import get_returns_chain

async def handle_returns(state: GraphState) -> Dict[str, Any]:
    """Handle multi-step returns flow."""
    state["flow"].append("handle_returns")

    # The returns node needs primarily orders and primer_nombre
    filtered_data = filter_user_data(state.get("user_data"), ["primer_nombre", "orders"])
    
    current_step = state.get("current_step")
    if not current_step:
        current_step = "STEP_1_VERIFY_AND_REASON"

    try:
        chain = get_returns_chain()
        result = await chain.ainvoke({
            "user_data": str(filtered_data),
            "messages": state.get("messages", []),
            "question": state["question"],
            "current_step": current_step
        })

        return {
            "generation": result.respuesta_final,
            "current_step": result.next_step,
            "is_return_in_progress": result.is_return_in_progress
        }

    except Exception as e:
        print(f"[ERROR] handle_returns failed: {e}")
        return {
            "generation": "Disculpa, tuve un problema procesando tu devolución. ¿Podrías intentar de nuevo o contactar a nuestro equipo de soporte?",
            "is_return_in_progress": False
        }
