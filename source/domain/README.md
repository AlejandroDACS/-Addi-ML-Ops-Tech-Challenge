# Module: Domain

This directory contains the operational Python functions that act as active Nodes within the LangGraph graph. The functional reasoning where user requests are routed resides here.

## Development Files

### `router.py`
- **Description:** Main routing agent node at the beginning of the flow.
- **Central Logic:** First evaluates whether an incomplete return persists in the active session by checking `is_return_in_progress`. If that's the case, it immediately forwards to the returns flow. If it's a new query, it invokes `get_router_chain` passing the store's topics to infer a target `selected_agent` and pass it back in the state.

### `handle_general.py`
- **Description:** Conversational agent designed for global-purpose customer service requests like products, shipping, promotions, or payments.
- **Central Logic:** Replaced loading the entire context by extracting and processing *only* the specific area indicated by the routing LLM previously via a cross-match in the Knowledge Base. Also, it restricts the attached user JSON fields (via `filter_user_data`), delivering an ecosystem with very few tokens to the bot, shielded, and devoid of irrelevant *data leakage*.

### `handle_returns.py`
- **Description:** Specialized node agent for the critical transactional Returns process (Returns Flow).
- **Central Logic:** Synchronously maintains the conditional flow with memory ("multi-step") without exiting the return context unless a forced escalation or cancellation occurs, operating the allowed timeframe validation on the identified catalog order in the JSON prior to the central system refund.
