# Module: Adapters / Chains

This directory is absolutely responsible for architecturally declaring the base chains (LangChain / LLMs) or external adapters, formatting the integral *System Prompts*, and structuring (via Pydantic) exactly what Gemini is asked to predict.

## Development Files

### `router_chain.py`
- **Description:** Fast classification LLM with zero probabilistic temperature.
- **Functionality:** It is forced under the `RouterResponse` schema to analyze inputs to dictate, based on the preloaded contexts of `VALID_TOPICS`, where the graph should branch to (Categorization).

### `general_chain.py`
- **Description:** Natural generative generator (ChatLLM). Client-facing responses.
- **Functionality:** Parametrically refocuses the mandatory conditions, requiring it to respond with a local Colombian tone and to bias all its responses using contextual guidelines brought from the central `knowledge_base`.

### `returns_chain.py`
- **Description:** LLM chain coupled with strict memory focused on Returns (Structured Output).
- **Functionality:** Predicts and determines the next operational strike or validation ("Refund Reason vs Logistics"). The LLM assumes the interactive position with transitions like `STEP_1_VERIFY_AND_REASON` until the conditional human validation concludes with uninterrupted escalation and without false promises.
